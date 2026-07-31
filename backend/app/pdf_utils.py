"""PDF utilities: convert PDF pages to PNG images for the vision API."""

import fitz  # PyMuPDF

from app.errors import ProviderError


# Render scale. Higher = sharper (better OCR) but larger. 2.0 ≈ 144 DPI,
# a good balance for text legibility without huge payloads.
_RENDER_SCALE = 2.0


def pdf_first_page_to_png(pdf_bytes: bytes) -> bytes:
    """Render the first page of a PDF to PNG bytes.

    Args:
        pdf_bytes: Raw bytes of the PDF file.

    Returns:
        PNG-encoded bytes of the first page.

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

        page = doc.load_page(0)  # first page only (multi-page is a WANT item)
        matrix = fitz.Matrix(_RENDER_SCALE, _RENDER_SCALE)
        pixmap = page.get_pixmap(matrix=matrix)
        return pixmap.tobytes("png")
    finally:
        doc.close()