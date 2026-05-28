from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from backend.ocr import extract_text

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_report(file: UploadFile = File(...)):
    if not file.content_type.startswith(("application/pdf", "image/", "text/")):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    destination = UPLOAD_DIR / file.filename
    contents = await file.read()
    destination.write_bytes(contents)

    extracted_text = None
    try:
        extracted_text = extract_text(destination)
    except ValueError:
        extracted_text = None
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {exc}")

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
        "saved_to": str(destination),
        "extracted_text": extracted_text,
    }