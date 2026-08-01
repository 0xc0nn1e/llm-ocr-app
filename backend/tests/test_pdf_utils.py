"""Tests for PDF -> PNG conversion."""

import fitz  # PyMuPDF
import pytest

from app.pdf_utils import pdf_first_page_to_png, pdf_to_pngs
from app.errors import ProviderError


def _make_pdf_bytes(pages: int = 1, text: str = "テスト") -> bytes:
    """Create a PDF with the given number of pages, as bytes."""
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"{text} page {i + 1}")
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_pdf_first_page_to_png_returns_png():
    """A valid PDF is rendered to PNG bytes (starts with PNG signature)."""
    pdf_bytes = _make_pdf_bytes()
    png = pdf_first_page_to_png(pdf_bytes)

    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(png) > 0


def test_pdf_invalid_bytes_raises():
    """Non-PDF bytes raise ProviderError."""
    with pytest.raises(ProviderError):
        pdf_first_page_to_png(b"this is not a pdf")


def test_pdf_to_pngs_returns_one_image_per_page():
    """A 3-page PDF returns 3 PNG images, in order."""
    pdf_bytes = _make_pdf_bytes(pages=3)
    images = pdf_to_pngs(pdf_bytes)

    assert len(images) == 3
    for img in images:
        assert img[:8] == b"\x89PNG\r\n\x1a\n"


def test_pdf_to_pngs_respects_max_pages_cap():
    """A PDF with more pages than the cap only returns the capped amount."""
    from app.config import settings
    pdf_bytes = _make_pdf_bytes(pages=15)
    images = pdf_to_pngs(pdf_bytes)

    assert len(images) == settings.max_pdf_pages  # _MAX_PAGES