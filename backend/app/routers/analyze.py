"""Analyze endpoint: upload a file, run it through the LLM, return results."""

from fastapi import APIRouter, UploadFile, File

from app.validation import validate_upload
from app.providers.claude import ClaudeProvider
from app.schemas import AnalysisResult
from app.pdf_utils import pdf_first_page_to_png

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_file(file: UploadFile = File(...)) -> AnalysisResult:
    """Upload a file, validate it, analyze it with the LLM, return results.

    PDFs are rendered to a PNG image first so every provider receives an
    image (uniform input). Validation and provider errors raise AppError,
    handled globally in main.py.
    """
    contents = await file.read()
    size = len(contents)

    # Reuse upload validation (type + size).
    extension = validate_upload(file, size)

    # Normalize input to an image. PDFs -> PNG so the vision API can read them.
    if extension == "pdf":
        image_bytes = pdf_first_page_to_png(contents)
        media_type = "image/png"
    else:
        image_bytes = contents
        media_type = file.content_type or ""

    provider = ClaudeProvider()
    result = provider.analyze_image(image_bytes, media_type)

    return result