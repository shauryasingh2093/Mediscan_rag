# Mediscan_rag

AI-powered medical intelligence assistant (work-in-progress).

See `backend/` for the FastAPI server and `backend/ocr` for the OCR extractor.

How to run (local):

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
