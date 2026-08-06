"""Pydantic schemas for analysis results."""

from pydantic import BaseModel, Field, field_validator


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

    @field_validator("tags", mode="before")
    @classmethod
    def coerce_tags(cls, v):
        """Accept a comma-separated string as well as a list.

        The tool schema asks for an array, but the model occasionally
        returns a single comma-separated string. Normalising here keeps
        one bad generation from failing the whole request.
        """
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",") if tag.strip()]
        return v