# Troubleshooting

## Missing `fastapi` or `pydantic` errors

This usually means the wrong interpreter is active or the repo backend path is not on `PYTHONPATH`.

Use:

```powershell
cd "c:\Users\nagur\D_drive\MyFolder\projects\void"
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m pytest -q
```

## ModuleNotFoundError: app

Run tests from the project root or set `PYTHONPATH=backend`.

## Frontend build issues

Make sure dependencies are installed in the frontend directory:

```powershell
cd frontend
npm install
npm run build
```

## Local runtime startup issues

Confirm the venv is active and the backend package is resolvable before starting uvicorn.
