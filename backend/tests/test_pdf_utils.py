"""Tests for PDF -> PNG conversion."""

import fitz  # PyMuPDF
import pytest

from app.pdf_utils import pdf_first_page_to_png
from app.errors import ProviderError


def _make_pdf_bytes(text: str = "テスト") -> bytes:
    """Create a minimal one-page PDF with some text, as bytes."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_pdf_first_page_to_png_returns_png():
    """A valid PDF is rendered to PNG bytes (starts with PNG signature)."""
    pdf_bytes = _make_pdf_bytes()
    png = pdf_first_page_to_png(pdf_bytes)

    # PNG files start with this 8-byte signature.
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(png) > 0


def test_pdf_invalid_bytes_raises():
    """Non-PDF bytes raise ProviderError."""
    with pytest.raises(ProviderError):
        pdf_first_page_to_png(b"this is not a pdf")