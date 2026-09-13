from datetime import timedelta, datetime, UTC
from fastapi import APIRouter, Depends, Header, Body, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4

from app.api.deps import get_db, get_current_user
from app.contracts.schemas import (
    RegisterRequest,
    UserSummaryResponse,
    LoginRequest,
    AuthTokenResponse,
    RefreshTokenRequest,
    ProfileUpdateRequest
)
from app.core.security import (
    hash_password,
    verify_password,
    encode_token,
    decode_token,
    hash_refresh_token
)
from app.db.base import User, RefreshToken, Session as DbSession
from app.repositories.users import user_repo

router = APIRouter(prefix="/auth", tags=["auth"])


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
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
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
    
    return AuthTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        email=user.email,
        role=user.role
    )


@router.post("/refresh", response_model=AuthTokenResponse)
def refresh_user_token(
    payload: RefreshTokenRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    decoded = decode_token(payload.refresh_token, token_kind="refresh")
    if not decoded:
        raise HTTPException(status_code=401, detail="INVALID_REFRESH_TOKEN")
        
    refresh_user_id, refresh_email = decoded
    if refresh_user_id != current_user.id:
        raise HTTPException(status_code=401, detail="INVALID_REFRESH_TOKEN")
        
    token_hash = hash_refresh_token(payload.refresh_token)
    
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
def logout_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(DbSession).filter(DbSession.user_id == current_user.id).update({"is_active": False})
    db.commit()


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
