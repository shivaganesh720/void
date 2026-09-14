# VOID Development Guide

## Local Setup

### 1. Backend (Python/FastAPI)
The backend is completely self-contained in the `backend/` directory.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .\.venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Frontend (Next.js)
The frontend is completely self-contained in the `frontend/` directory.

```bash
cd frontend
npm install
npm run dev
```

## Database Migrations
VOID uses SQLAlchemy and Alembic. The primary development database is SQLite, while production targets PostgreSQL.

```bash
cd backend
alembic revision --autogenerate -m "Description of change"
alembic upgrade head
```

## Running Tests
Tests are located in `backend/tests/` and use `pytest`. The test suite uses an in-memory SQLite database (`:memory:`) to ensure isolation.

```bash
cd backend
export PYTHONPATH="."  # Or $env:PYTHONPATH="." on Windows PowerShell
pytest tests/unit -v
```

## Development Rules
1. **API Prefix:** All new endpoints must be prefixed with `/api/v1/`.
2. **Dependency Injection:** Use FastAPI `Depends` for database sessions, current users, and gateway instances.
3. **Database Portability:** Do not use database-specific features (e.g. `PGUUID`) unless absolutely necessary. Use `sqlalchemy.Uuid` to ensure compatibility across SQLite and PostgreSQL.
4. **MVC Separation:** Keep business logic out of routers. Use the `repositories/` layer for database access and `services/` for business logic.

## Troubleshooting
- **Alembic FileNotFoundError:** Ensure you are running alembic commands from the `backend/` directory.
- **Tests Failing with Missing Column:** Ensure you are using the `db_session` fixture or `app.dependency_overrides[get_db]` in your tests instead of creating raw un-migrated `SessionLocal` instances.
