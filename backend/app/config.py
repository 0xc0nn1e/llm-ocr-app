from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    # Reads values from environment variables (injected by docker compose
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    port: int = 8000

    anthropic_api_key: str = ""

    # Max upload size in bytes (default 10 MB). Override via MAX_FILE_SIZE env.
    max_file_size: int = 10 * 1024 * 1024

    # Claude model to use. Override via ANTHROPIC_MODEL env if needed.
    anthropic_model: str = "claude-sonnet-4-6"
    anthropic_max_tokens: int = 2048

settings = Settings()