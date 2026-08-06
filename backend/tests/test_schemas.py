"""Tests for schema coercion of LLM output."""

from app.schemas import AnalysisResult


def test_tags_accepts_list():
    """A proper list of tags is kept as-is."""
    result = AnalysisResult(
        ocr="テスト",
        description="説明",
        tags=["タグ1", "タグ2"],
        alt="代替テキスト",
    )
    assert result.tags == ["タグ1", "タグ2"]


def test_tags_accepts_comma_separated_string():
    """A comma-separated string is split into a list.

    The model occasionally returns tags as a single string despite the
    tool schema asking for an array.
    """
    result = AnalysisResult(
        ocr="テスト",
        description="説明",
        tags="マンガ, 白黒, ホラー",
        alt="代替テキスト",
    )
    assert result.tags == ["マンガ", "白黒", "ホラー"]