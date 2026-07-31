"""File validation for uploads: allowed types and size limits."""

from fastapi import UploadFile
from app.config import settings

from app.errors import UnsupportedFileType, EmptyFile, FileTooLarge

# Allowed MIME types mapped to canonical extensions.
ALLOWED_TYPES: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "application/pdf": "pdf",
}

def validate_upload(file: UploadFile, size: int) -> str:
    """Validate an uploaded file's content type and size.

    Returns the canonical extension (e.g. "jpg") on success.
    Raises an AppError subclass on failure.
    """
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        allowed = ", ".join(ALLOWED_TYPES.keys())
        raise UnsupportedFileType(
            f"対応していないファイル形式です: {content_type or '不明'}. "
            f"対応形式: {allowed}"
        )

    if size == 0:
        raise EmptyFile("ファイルが空です。")

    if size > settings.max_file_size:
        mb = settings.max_file_size // (1024 * 1024)
        raise FileTooLarge(f"ファイルサイズが上限（{mb}MB）を超えています。")

    return ALLOWED_TYPES[content_type]