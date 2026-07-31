"""Upload endpoint: accepts a file, validates it, returns metadata."""

from fastapi import APIRouter, UploadFile, File

from app.validation import validate_upload

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    """Accept an uploaded file, validate type/size, return its metadata.

    Does not persist the file or call any LLM yet; it only confirms the
    file is acceptable and echoes back basic info. Validation failures
    raise AppError, handled globally in main.py.
    """
    # Read into memory to measure size. Files here are small (images / short
    # PDFs), so in-memory is fine and avoids disk I/O.
    contents = await file.read()
    size = len(contents)

    # Raises AppError on failure; the global handler converts it to a
    # structured 400 response.
    extension = validate_upload(file, size)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "extension": extension,
        "size": size,
    }