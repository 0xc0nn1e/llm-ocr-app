"""Tests for /api/analyze, with the Claude provider mocked (no real API)."""

import io
import base64
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import AnalysisResult

client = TestClient(app)


def _png_bytes() -> bytes:
    """Bytes of a minimal valid 1x1 PNG."""
    b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4"
        "nGNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
    )
    return base64.b64decode(b64)


@patch("app.routers.analyze.ClaudeProvider")
def test_analyze_returns_result(mock_provider_cls):
    """A valid image returns the provider's analysis result."""
    # Mock the provider to return a fixed result (no real API call).
    mock_provider = mock_provider_cls.return_value
    mock_provider.analyze_images.return_value = AnalysisResult(
        ocr="テスト文字",
        description="これはテスト画像です。",
        tags=["テスト", "画像"],
        alt="テスト用の画像",
    )

    files = {"file": ("test.png", io.BytesIO(_png_bytes()), "image/png")}
    res = client.post("/api/analyze", files=files)

    assert res.status_code == 200
    body = res.json()
    assert body["ocr"] == "テスト文字"
    assert body["tags"] == ["テスト", "画像"]
    assert body["alt"] == "テスト用の画像"


@patch("app.routers.analyze.ClaudeProvider")
def test_analyze_rejects_unsupported_type(mock_provider_cls):
    """An unsupported file is rejected before the provider is called."""
    files = {"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")}
    res = client.post("/api/analyze", files=files)

    assert res.status_code == 400
    body = res.json()
    assert body["error"]["code"] == "UNSUPPORTED_FILE_TYPE"
    # Provider must NOT be called when validation fails.
    mock_provider_cls.return_value.analyze_images.assert_not_called()