# Deployment Status

## Local Development

```powershell
cd "c:\Users\nagur\D_drive\MyFolder\projects\void"
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend:

```powershell
cd frontend
npm install
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
```

## Production Status

- not yet production-ready
- durable PostgreSQL repository, policy enforcement, and external provider integration are still pending
