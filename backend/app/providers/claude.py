"""Claude (Anthropic) provider: analyzes an image and returns structured data."""
"""https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python"""
"""https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview"""


import base64

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
                "description": "ファイル内の文字を抽出したテキスト（日本語）",
            },
            "description": {
                "type": "string",
                "description": "ファイルに何が写っている/書かれているかの説明（日本語）",
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
    "必ず report_analysis ツールを使って結果を返してください。"
    "OCR・説明・代替テキストはすべて日本語で記述してください。"
)


class ClaudeProvider:
    """Analyzes images using Anthropic's Claude vision + tool use."""

    def __init__(self) -> None:
        # The SDK reads the key from the argument (sourced from settings,
        # which itself comes from the environment — never hardcoded).
        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model
        self._max_tokens = settings.anthropic_max_tokens

    def analyze_image(self, image_bytes: bytes, media_type: str) -> AnalysisResult:
        """Analyze a single image and return structured results.

        Args:
            image_bytes: Raw bytes of the image.
            media_type: e.g. "image/png" or "image/jpeg".

        Raises:
            ProviderError: if the API call fails.
            InvalidResponse: if Claude's output can't be parsed into schema.
        """
        b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

        try:
            message = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=_SYSTEM_PROMPT,
                tools=[_ANALYSIS_TOOL],
                # Force Claude to use our tool (guarantees structured output).
                tool_choice={"type": "tool", "name": "report_analysis"},
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": "このファイルを解析してください。",
                            },
                        ],
                    }
                ],
            )
        except APIError as e:
            raise ProviderError(f"LLM API の呼び出しに失敗しました: {e}")

        # Extract the tool_use block that carries the structured arguments.
        # check the return value have been used the tool or not
       
        """
        Sample rtn from claude api
        [

            TextBlock(type="text", text="承知しました。画像を解析します。"),

            ToolUseBlock(
                type="tool_use",
                id="toolu_01A2b3C4d5E6f7G8h9",
                name="report_analysis",
                input={
                    "ocr": "営業中",
                    "description": "「営業中」と書かれた店舗の看板の画像です。赤地に白い文字で書かれています。",
                    "tags": ["看板", "営業中", "店舗", "サイン"],
                    "alt": "営業中と書かれた赤い看板"
                }
            )
        ]
        """
        tool_input = None
        for block in message.content:
            if block.type == "tool_use" and block.name == "report_analysis":
                tool_input = block.input
                break

        if tool_input is None:
            raise InvalidResponse("LLM から想定した形式の応答が得られませんでした。")

        try:
            # Validate against our schema; raises if fields are wrong/missing.
            return AnalysisResult.model_validate(tool_input)
        except Exception as e:
            raise InvalidResponse(f"LLM 応答の形式が不正です: {e}")