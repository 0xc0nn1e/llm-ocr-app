"""PDF utilities: convert PDF pages to PNG images for the vision API."""

import fitz  # PyMuPDF

from app.config import settings
from app.errors import ProviderError


# Render scale. Higher = sharper (better OCR) but larger. 2.0 ≈ 144 DPI,
# a good balance for text legibility without huge payloads.
_RENDER_SCALE = 2.0

# Safety cap: avoid sending an unbounded number of pages/images to the LLM.
_MAX_PAGES = 10


def pdf_first_page_to_png(pdf_bytes: bytes) -> bytes:
    """Render the first page of a PDF to PNG bytes.

    Kept for reuse in tests and any single-page-only use case.
    """
    pages = pdf_to_pngs(pdf_bytes)
    return pages[0]


def pdf_to_pngs(pdf_bytes: bytes) -> list[bytes]:
    """Render all pages of a PDF (up to _MAX_PAGES) to a list of PNG bytes.

    Args:
        pdf_bytes: Raw bytes of the PDF file.

    Returns:
        List of PNG-encoded bytes, one per page, in page order.

    Raises:
        ProviderError: if the PDF can't be opened or has no pages.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise ProviderError(f"PDF の読み込みに失敗しました: {e}")

    try:
        if doc.page_count == 0:
            raise ProviderError("PDF にページが含まれていません。")

        matrix = fitz.Matrix(_RENDER_SCALE, _RENDER_SCALE)
        page_count = min(doc.page_count, settings.max_pdf_pages)

        images = []
        for i in range(page_count):
            page = doc.load_page(i)
            pixmap = page.get_pixmap(matrix=matrix)
            images.append(pixmap.tobytes("png"))
        return images
    finally:
        doc.close()