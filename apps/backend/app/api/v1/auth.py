from datetime import timedelta, datetime, UTC
from fastapi import APIRouter, Depends, Header, Body, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from uuid import uuid4
import secrets

from app.api.deps import get_db, get_current_user
from app.schemas import (
    RegisterRequest,
    UserSummaryResponse,
    LoginRequest,
    AuthTokenResponse,
    RefreshTokenRequest,
    ProfileUpdateRequest,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest
)
from app.core.security import (
    hash_password,
    verify_password,
    encode_token,
    decode_token,
    hash_refresh_token
)
from app.models.base import User, RefreshToken, Session as DbSession, PasswordResetToken, EmailVerificationToken
from app.repositories.users import user_repo
from app.core.config import get_settings as _get_settings

router = APIRouter(prefix="/auth", tags=["auth"])

_settings = _get_settings()
_IS_SECURE = _settings.environment not in ("development", "dev", "local")

def _set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(key="void_access_token", value=access_token, httponly=True, secure=_IS_SECURE, samesite="lax", max_age=3600)
    response.set_cookie(key="void_refresh_token", value=refresh_token, httponly=True, secure=_IS_SECURE, samesite="lax", max_age=30*24*3600)


@router.post("/register", response_model=UserSummaryResponse, status_code=201)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    if user_repo.get_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="USER_ALREADY_EXISTS")
        
    user = user_repo.create(db, {
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "full_name": payload.full_name.strip(),
        "role": "USER"
    })
    db.commit()
    return user


@router.post("/login", response_model=AuthTokenResponse)
def login_user(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = user_repo.get_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS")
        
    access_token = encode_token(user.id, user.email, token_kind="access", ttl=timedelta(hours=1))
    refresh_token = encode_token(user.id, user.email, token_kind="refresh", ttl=timedelta(days=30))
    
    db_session = DbSession(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(UTC) + timedelta(days=30)
    )
    db.add(db_session)
    db.commit()
    
    response.set_cookie(key="void_access_token", value=access_token, httponly=True, secure=_IS_SECURE, samesite="lax", max_age=3600)
    response.set_cookie(key="void_refresh_token", value=refresh_token, httponly=True, secure=_IS_SECURE, samesite="lax", max_age=30*24*3600)
    
    return AuthTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        email=user.email,
        role=user.role
    )


@router.post("/refresh", response_model=AuthTokenResponse)
def refresh_user_token(
    request: Request,
    response: Response,
    payload: RefreshTokenRequest | None = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    refresh_token = (payload.refresh_token if payload else None) or request.cookies.get("void_refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="MISSING_REFRESH_TOKEN")

    decoded = decode_token(refresh_token, token_kind="refresh")
    if not decoded:
        raise HTTPException(status_code=401, detail="INVALID_REFRESH_TOKEN")
        
    refresh_user_id, refresh_email = decoded
    if refresh_user_id != current_user.id:
        raise HTTPException(status_code=401, detail="INVALID_REFRESH_TOKEN")
        
    token_hash = hash_refresh_token(refresh_token)
    
    db_session = db.query(DbSession).filter(DbSession.token_hash == token_hash, DbSession.user_id == current_user.id, DbSession.is_active == True).first()
    
    if not db_session:
        raise HTTPException(status_code=401, detail="REFRESH_TOKEN_REUSE_DETECTED")
        
    db_session.is_active = False
    
    new_access = encode_token(current_user.id, current_user.email, token_kind="access", ttl=timedelta(hours=1))
    new_refresh = encode_token(current_user.id, current_user.email, token_kind="refresh", ttl=timedelta(days=30))
    
    new_db_session = DbSession(
        user_id=current_user.id,
        token_hash=hash_refresh_token(new_refresh),
        expires_at=datetime.now(UTC) + timedelta(days=30)
    )
    db.add(new_db_session)
    db.commit()
    
    response.set_cookie(key="void_access_token", value=new_access, httponly=True, secure=_IS_SECURE, samesite="lax", max_age=3600)
    response.set_cookie(key="void_refresh_token", value=new_refresh, httponly=True, secure=_IS_SECURE, samesite="lax", max_age=30*24*3600)
    
    return AuthTokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        user_id=current_user.id,
        email=current_user.email,
        role=current_user.role
    )


@router.get("/me", response_model=UserSummaryResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=204)
def logout_user(response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(DbSession).filter(DbSession.user_id == current_user.id).update({"is_active": False})
    db.commit()
    response.delete_cookie("void_access_token")
    response.delete_cookie("void_refresh_token")


@router.patch("/profile", response_model=UserSummaryResponse)
def update_profile(
    payload: ProfileUpdateRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    current_user.ai_awareness = payload.ai_awareness
    current_user.default_mode = payload.default_mode
    current_user.explanation_level = payload.explanation_level
    current_user.execution_priority = payload.execution_priority
    current_user.onboarding_completed = True
    db.commit()
    return current_user


@router.post("/verify-email", status_code=200)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    # Dev mock logic
    token_hash = hash_refresh_token(payload.token)
    token_record = db.query(EmailVerificationToken).filter_by(token_hash=token_hash, is_used=False).first()
    if not token_record or token_record.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="AUTH_INVALID_TOKEN")
    
    token_record.is_used = True
    db.commit()
    return {"status": "success"}


@router.post("/forgot-password", status_code=200)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = user_repo.get_by_email(db, payload.email)
    if user:
        raw_token = secrets.token_urlsafe(32)
        token_record = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(hours=1)
        )
        db.add(token_record)
        db.commit()
        print(f"[DEV ONLY] Password reset token for {user.email}: {raw_token}")
    
    # Always return 200 to prevent user enumeration
    return {"status": "success"}


@router.post("/reset-password", status_code=200)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hash_refresh_token(payload.token)
    token_record = db.query(PasswordResetToken).filter_by(token_hash=token_hash, is_used=False).first()
    
    if not token_record or token_record.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="AUTH_INVALID_TOKEN")
        
    user = user_repo.get(db, token_record.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="AUTH_INVALID_TOKEN")
        
    user.password_hash = hash_password(payload.new_password)
    token_record.is_used = True
    
    db.query(DbSession).filter_by(user_id=user.id).update({"is_active": False})
    
    db.commit()
    return {"status": "success"}


@router.post("/change-password", status_code=200)
def change_password(
    payload: ChangePasswordRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="AUTH_INVALID_CREDENTIALS")
        
    current_user.password_hash = hash_password(payload.new_password)
    db.query(DbSession).filter(DbSession.user_id == current_user.id).update({"is_active": False})
    
    db.commit()
    return {"status": "success"}


@router.get("/sessions")
def get_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(DbSession).filter_by(user_id=current_user.id, is_active=True).all()
    return [
        {"id": s.id, "created_at": s.created_at, "expires_at": s.expires_at} 
        for s in sessions
    ]
