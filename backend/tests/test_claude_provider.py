"""Tests for ClaudeProvider using a mocked Anthropic client (no real API calls)."""

from unittest.mock import MagicMock, patch

import pytest

from app.errors import ProviderError, InvalidResponse
from app.schemas import AnalysisResult


def _fake_tool_use_message(tool_input: dict) -> MagicMock:
    """Build a fake Anthropic message containing one tool_use block."""
    block = MagicMock()
    block.type = "tool_use"
    block.name = "report_analysis"
    block.input = tool_input

    message = MagicMock()
    message.content = [block]
    return message


@patch("app.providers.claude.Anthropic")
def test_analyze_image_returns_structured_result(mock_anthropic_cls):
    """A well-formed tool_use response is parsed into AnalysisResult."""
    fake_message = _fake_tool_use_message(
        {
            "ocr": "テスト文字",
            "description": "これはテスト画像です。",
            "tags": ["テスト", "画像"],
            "alt": "テスト用の画像",
        }
    )
    mock_client = MagicMock()
    mock_client.messages.create.return_value = fake_message
    mock_anthropic_cls.return_value = mock_client

    # Import after patch so the provider uses the mocked Anthropic.
    from app.providers.claude import ClaudeProvider

    provider = ClaudeProvider()
    result = provider.analyze_image(b"fake-image-bytes", "image/png")

    assert isinstance(result, AnalysisResult)
    assert result.ocr == "テスト文字"
    assert result.tags == ["テスト", "画像"]


@patch("app.providers.claude.Anthropic")
def test_analyze_image_raises_on_missing_tool_use(mock_anthropic_cls):
    """If no tool_use block is present, InvalidResponse is raised."""
    empty_message = MagicMock()
    empty_message.content = []  # no tool_use block
    mock_client = MagicMock()
    mock_client.messages.create.return_value = empty_message
    mock_anthropic_cls.return_value = mock_client

    from app.providers.claude import ClaudeProvider

    provider = ClaudeProvider()
    with pytest.raises(InvalidResponse):
        provider.analyze_image(b"fake-image-bytes", "image/png")


@patch("app.providers.claude.Anthropic")
def test_analyze_image_raises_on_bad_schema(mock_anthropic_cls):
    """A tool_use block missing required fields raises InvalidResponse."""
    bad_message = _fake_tool_use_message({"ocr": "only ocr, missing others"})
    mock_client = MagicMock()
    mock_client.messages.create.return_value = bad_message
    mock_anthropic_cls.return_value = mock_client

    from app.providers.claude import ClaudeProvider

    provider = ClaudeProvider()
    with pytest.raises(InvalidResponse):
        provider.analyze_image(b"fake-image-bytes", "image/png")

@patch("app.providers.claude.Anthropic")
def test_analyze_images_handles_multiple_pages(mock_anthropic_cls):
    """Multiple images are sent in a single request and parsed correctly."""
    fake_message = _fake_tool_use_message(
        {
            "ocr": "1ページ目\n2ページ目",
            "description": "2ページの文書です。",
            "tags": ["文書", "複数ページ"],
            "alt": "2ページの文書画像",
        }
    )
    mock_client = MagicMock()
    mock_client.messages.create.return_value = fake_message
    mock_anthropic_cls.return_value = mock_client

    from app.providers.claude import ClaudeProvider

    provider = ClaudeProvider()
    result = provider.analyze_images(
        [b"page1-bytes", b"page2-bytes"], "image/png"
    )

    assert isinstance(result, AnalysisResult)
    assert "1ページ目" in result.ocr
    # Verify the request included both images as content blocks.
    call_args = mock_client.messages.create.call_args
    content = call_args.kwargs["messages"][0]["content"]
    image_blocks = [b for b in content if b["type"] == "image"]
    assert len(image_blocks) == 2