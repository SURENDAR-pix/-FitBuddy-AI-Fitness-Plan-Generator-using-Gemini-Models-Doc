from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "FitBuddy – AI Fitness Plan Generator"
    debug: bool = True

    database_url: str = (
        f"sqlite:///{(BASE_DIR / 'fitbuddy.db').as_posix()}"
    )

    gemini_api_key: str = ""

    # Current Gemini model used by FitBuddy
    workout_model: str = "gemini-3.8-flash"
    tip_model: str = "gemini-3.8-flash"

    admin_password: str = "change-me"

    session_secret: str = "change-this-session-secret"

    max_feedback_length: int = 1000

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()