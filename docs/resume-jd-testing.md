# Resume/JD Testing

Backend commands:

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m pytest tests\unit -q
```

Frontend command:

```powershell
Set-Location frontend
npm run build
```

Covered now: state transitions, safe upload validation, text analysis, structured score bounds, and API success/retrieval behavior. The repository still needs authenticated access tests, durable persistence tests, real DOCX/PDF fixtures, provider gateway contract tests, browser tests, and cross-project authorization tests.
