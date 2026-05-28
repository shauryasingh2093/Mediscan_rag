from pathlib import Path
from PIL import Image
import pytesseract
import docx

TEXT_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".gif"}

try:
    from pypdf import PdfReader as _PdfReader
except Exception:
    try:
        from PyPDF2 import PdfReader as _PdfReader
    except Exception:
        try:
            import pypdf2 as _pypdf2
            _PdfReader = _pypdf2.PdfReader
        except Exception:
            _PdfReader = None

def extract_text_from_txt(path: Path):
    return path.read_text(encoding="utf-8", errors="ignore")

def extract_text_from_pdf(path: Path):
    if _PdfReader is None:
        raise ImportError("No PDF reader available (install pypdf or PyPDF2)")
    text = []
    with open(path, "rb") as f:
        reader = _PdfReader(f)
        for page in getattr(reader, 'pages', []):
            page_text = getattr(page, 'extract_text', None)
            if page_text is None:
                page_text = getattr(page, 'extractText', None)
            text.append((page_text() if page_text else "") or "")
    return "\n".join(text)

def extract_text_from_docx(path: Path):
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text_from_image(path: Path):
    image = Image.open(path)
    return pytesseract.image_to_string(image)

def extract_text(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return extract_text_from_txt(path)
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix == ".docx":
        return extract_text_from_docx(path)
    if suffix in TEXT_IMAGE_EXTENSIONS:
        return extract_text_from_image(path)

    raise ValueError(f"Unsupported file extension: {suffix}")