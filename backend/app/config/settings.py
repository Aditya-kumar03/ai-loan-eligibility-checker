import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "AI Loan Eligibility Checker"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: str = "*"

    # Anthropic Claude API Configuration
    CLAUDE_API_KEY: str = Field(default="")
    CLAUDE_MODEL: str = "claude-3-7-sonnet-20250219"

    # Google Sheets Audit Integration Configuration
    GOOGLE_SHEETS_ID: str = Field(default="")
    GOOGLE_SERVICE_ACCOUNT_EMAIL: str = Field(default="")
    GOOGLE_PRIVATE_KEY: str = Field(default="")

    @property
    def cors_origins(self) -> List[str]:
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_claude_configured(self) -> bool:
        return bool(self.CLAUDE_API_KEY and len(self.CLAUDE_API_KEY.strip()) > 10)

    @property
    def is_google_sheets_configured(self) -> bool:
        return bool(self.GOOGLE_SHEETS_ID and self.GOOGLE_SERVICE_ACCOUNT_EMAIL and self.GOOGLE_PRIVATE_KEY)

settings = Settings()
