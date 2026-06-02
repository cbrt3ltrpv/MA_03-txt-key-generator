from functools import lru_cache
from typing import Literal

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1", alias="OPENAI_MODEL")
    bot_run_mode: Literal["polling", "webhook"] = Field(
        default="polling",
        alias="BOT_RUN_MODE",
    )
    webhook_url: HttpUrl | None = Field(default=None, alias="WEBHOOK_URL")
    webhook_host: str = Field(default="0.0.0.0", alias="WEBHOOK_HOST")
    webhook_port: int = Field(default=8080, alias="WEBHOOK_PORT")
    max_revision_cycles: int = Field(default=3, ge=1, le=10, alias="MAX_REVISION_CYCLES")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()

