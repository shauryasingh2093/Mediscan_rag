from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.ingestion import ingest_text
from backend.ocr import extract_text
from backend.app.api.uploads import UPLOAD_DIR

router = APIRouter()


@router.post("/ingest")
async def ingest_document(
    filename: Optional[str] = None,
    text: Optional[str] = None,
    collection: str = "medical_reports",
):
    if not filename and not text:
        raise HTTPException(status_code=400, detail="Provide either a filename or text to ingest.")

    source_text = text
    if filename and source_text is None:
        source_path = UPLOAD_DIR / filename
        if not source_path.exists():
            raise HTTPException(status_code=404, detail=f"Uploaded file not found: {filename}")
        try:
            source_text = extract_text(source_path)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Text extraction failed: {exc}")

    if source_text is None or not source_text.strip():
        raise HTTPException(status_code=400, detail="Ingested text is empty.")

    identifier = filename or "inline_text"
    metadata = {"filename": filename} if filename else {"source": "inline"}

    try:
        result = ingest_text(identifier=identifier, text=source_text, metadata=metadata, collection_name=collection)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")

    return result
