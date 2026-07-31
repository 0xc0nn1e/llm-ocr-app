"""Pydantic schemas for analysis results."""

from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    """Structured result of analyzing an image or document."""

    ocr: str = Field(description="Text extracted from the file (Japanese).")
    description: str = Field(
        description="Explanation of what the file shows or says (Japanese)."
    )
    tags: list[str] = Field(description="Keywords describing the content.")
    alt: str = Field(
        description="Concise alt text for accessibility (Japanese)."
    )