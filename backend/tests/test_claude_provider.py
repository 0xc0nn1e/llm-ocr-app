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