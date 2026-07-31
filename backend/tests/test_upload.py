"""Tests for the /api/upload endpoint and file validation."""

import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _png_bytes() -> bytes:
    """Return the bytes of a minimal valid 1x1 PNG."""
    # A tiny hardcoded 1x1 PNG; enough for content-type based validation.
    import base64

    b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4"
        "nGNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
    )
    return base64.b64decode(b64)


def test_health():
    """Health endpoint returns ok."""
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_upload_valid_png():
    """A valid PNG is accepted and its metadata returned."""
    files = {"file": ("test.png", io.BytesIO(_png_bytes()), "image/png")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 200
    body = res.json()
    assert body["content_type"] == "image/png"
    assert body["extension"] == "png"
    assert body["size"] > 0


def test_upload_rejects_unsupported_type():
    """A text file is rejected with the correct error code."""
    files = {"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 400
    body = res.json()
    assert body["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_upload_rejects_empty_file():
    """An empty file is rejected with EMPTY_FILE."""
    files = {"file": ("empty.png", io.BytesIO(b""), "image/png")}
    res = client.post("/api/upload", files=files)
    assert res.status_code == 400
    body = res.json()
    assert body["error"]["code"] == "EMPTY_FILE"