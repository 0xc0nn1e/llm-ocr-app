"""Analyze endpoint: upload a file, run it through the LLM, return results."""

from fastapi import APIRouter, UploadFile, File

from app.validation import validate_upload, ALLOWED_TYPES
from app.providers.claude import ClaudeProvider
from app.schemas import AnalysisResult

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_file(file: UploadFile = File(...)) -> AnalysisResult:
    """Upload a file, validate it, analyze it with the LLM, return results.

    Reuses the same validation as /upload, then feeds the image bytes to
    the Claude provider. Validation and provider errors both raise AppError,
    handled globally in main.py.
    """
    # Read into memory (files are small: images / short PDFs).
    contents = await file.read()
    size = len(contents)

    # Reuse the upload validation (same rules: type + size).
    extension = validate_upload(file, size)

    # For now we only handle images. PDF -> image comes in the next commit.
    media_type = file.content_type or ""

    # Call the LLM provider. Raises ProviderError / InvalidResponse on failure,
    # both handled by the global error handler.
    provider = ClaudeProvider()
    result = provider.analyze_image(contents, media_type)

    return result