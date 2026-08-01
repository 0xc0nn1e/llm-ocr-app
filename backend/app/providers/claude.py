"""Claude (Anthropic) provider: analyzes an image and returns structured data.

References:
    https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python
    https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
"""


import base64
import logging

from anthropic import Anthropic, APIError

from app.config import settings
from app.errors import ProviderError, InvalidResponse
from app.schemas import AnalysisResult

# The tool schema forces Claude to return structured fields instead of prose.
# Claude will call this "tool" with arguments matching our AnalysisResult.
_ANALYSIS_TOOL = {
    "name": "report_analysis",
    "description": "Report the OCR text, description, tags, and alt text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ocr": {
                "type": "string",
                "description": "ファイル内の文字を抽出したテキスト（日本語）。複数ページの場合はページごとに区切って記載してください。",
            },
            "description": {
                "type": "string",
                "description": "ファイルに何が写っている/書かれているかの説明（日本語）。複数ページがある場合は全体を総合して説明してください。",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "内容を表すキーワード（複数）",
            },
            "alt": {
                "type": "string",
                "description": "アクセシビリティ用の簡潔な代替テキスト（日本語）",
            },
        },
        "required": ["ocr", "description", "tags", "alt"],
    },
}

_SYSTEM_PROMPT = (
    "あなたは画像やドキュメントを解析するアシスタントです。"
    "アップロードされたファイルから文字を抽出（OCR）し、内容を説明してください。"
    "複数ページ・複数画像が提供された場合は、すべてのページを確認したうえで"
    "総合的に解析してください。"
    "必ず report_analysis ツールを使って結果を返してください。"
    "OCR・説明・代替テキストはすべて日本語で記述してください。"
)

logger = logging.getLogger(__name__)

class ClaudeProvider:
    """Analyzes images using Anthropic's Claude vision + tool use."""

    def __init__(self) -> None:
        # The SDK reads the key from the argument (sourced from settings,
        # which itself comes from the environment — never hardcoded).
        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model
        self._max_tokens = settings.anthropic_max_tokens

    def analyze_image(self, image_bytes: bytes, media_type: str) -> AnalysisResult:
        """Analyze a single image. Kept for backward compatibility; delegates
        to analyze_images with a single-item list.
        """
        return self.analyze_images([image_bytes], media_type)
    
    def analyze_images(
        self, images: list[bytes], media_type: str
    ) -> AnalysisResult:
        """Analyze one or more images (e.g. PDF pages) as a single document.

        Args:
            images: List of image bytes, in order (e.g. page 1, 2, 3...).
            media_type: e.g. "image/png" or "image/jpeg" (same for all).

        Raises:
            ProviderError: if the API call fails.
            InvalidResponse: if Claude's output can't be parsed into schema.
        """
        # Build one content block per image, followed by the instruction text.
        content = []
        for img in images:
            b64 = base64.standard_b64encode(img).decode("utf-8")
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": b64,
                    },
                }
            )
        instruction = (
            "このファイルを解析してください。"
            if len(images) == 1
            else f"この{len(images)}ページの文書を解析してください。"
        )
        content.append({"type": "text", "text": instruction})

        try:
            message = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=_SYSTEM_PROMPT,
                tools=[_ANALYSIS_TOOL],
                tool_choice={"type": "tool", "name": "report_analysis"},
                messages=[{"role": "user", "content": content}],
            )
        except APIError as e:
            logger.error("Anthropic API call failed: %s", e)
            raise ProviderError(
                "LLM API の呼び出しに失敗しました。時間をおいて再度お試しください。"
            )

        # Detect truncation: if the model hit the output limit, the tool
        # arguments will be incomplete (often an empty dict).
        if message.stop_reason == "max_tokens":
            logger.error(
                "LLM output truncated (stop_reason=max_tokens, limit=%s)",
                self._max_tokens,
            )
            raise InvalidResponse(
                "ファイルの内容が長すぎるため、解析結果を取得できませんでした。"
                "ページ数の少ないファイルでお試しください。"
            )

        tool_input = None
        for block in message.content:
            if block.type == "tool_use" and block.name == "report_analysis":
                tool_input = block.input
                break

        if tool_input is None:
            logger.error("No tool_use block in LLM response")
            raise InvalidResponse("LLM から想定した形式の応答が得られませんでした。")

        try:
            return AnalysisResult.model_validate(tool_input)
        except Exception as e:
            logger.error("Failed to validate LLM response: %s", e)
            raise InvalidResponse("LLM 応答の形式が不正です。")