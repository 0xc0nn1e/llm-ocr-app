from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    # Reads values from environment variables (injected by docker compose
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    port: int = 8000

    anthropic_api_key: str = ""


settings = Settings()