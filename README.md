# Mediscan_rag

AI-powered medical intelligence assistant (work-in-progress).

See `backend/` for the FastAPI server and `backend/ocr` for the OCR extractor.

How to run (local):

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /api/health` - service health check
- `POST /api/upload` - upload a report and extract text
- `POST /api/upload?auto_ingest=true` - upload, extract, and index text into ChromaDB
- `POST /api/ingest` - ingest existing uploaded files or raw text into the vector store

## Ingestion examples

Upload and index a file in one request:

```bash
curl -X POST "http://127.0.0.1:8000/api/upload?auto_ingest=true" -F "file=@/path/to/report.pdf"
```

Ingest an already-uploaded file by filename:

```bash
curl -X POST "http://127.0.0.1:8000/api/ingest" -d "filename=report.pdf"
```

Ingest raw text directly:

```bash
curl -X POST "http://127.0.0.1:8000/api/ingest" -d "text=This is a medical report summary."
```
