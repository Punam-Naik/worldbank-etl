import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

from dotenv import load_dotenv


# Project root: F:\sdrf-funds-etl
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """
    Centralized application configuration.
    frozen=True prevents accidental modification after loading.
    """

    wb_base_url: str
    wb_country: str
    wb_indicator: str

    wb_start_year: int
    wb_end_year: int
    wb_page_size: int

    wb_timeout_seconds: int
    wb_max_retries: int
    wb_backoff_factor: float

    app_env: str
    log_level: str


def load_settings(
    env: Optional[Mapping[str, str]] = None
) -> Settings:
    """
    Load and validate application settings.

    If env is not supplied, values are loaded from the
    operating system environment and project .env file.
    """

    if env is None:
        load_dotenv(PROJECT_ROOT / ".env")
        env = os.environ

    def get_required(name: str) -> str:
        value = env.get(name)

        if value is None or not value.strip():
            raise ValueError(
                f"Required configuration missing: {name}"
            )

        return value.strip()

    def get_int(name: str, default: int) -> int:
        try:
            return int(env.get(name, str(default)))
        except ValueError as exc:
            raise ValueError(
                f"{name} must be an integer"
            ) from exc

    def get_float(name: str, default: float) -> float:
        try:
            return float(env.get(name, str(default)))
        except ValueError as exc:
            raise ValueError(
                f"{name} must be a number"
            ) from exc

    settings = Settings(
        wb_base_url=get_required("WB_BASE_URL").rstrip("/"),
        wb_country=get_required("WB_COUNTRY").upper(),
        wb_indicator=get_required("WB_INDICATOR"),

        wb_start_year=get_int("WB_START_YEAR", 2000),
        wb_end_year=get_int("WB_END_YEAR", 2024),
        wb_page_size=get_int("WB_PAGE_SIZE", 100),

        wb_timeout_seconds=get_int("WB_TIMEOUT_SECONDS", 30),
        wb_max_retries=get_int("WB_MAX_RETRIES", 3),
        wb_backoff_factor=get_float("WB_BACKOFF_FACTOR", 1.0),

        app_env=env.get("APP_ENV", "development").lower(),
        log_level=env.get("LOG_LEVEL", "INFO").upper()
    )

    # Configuration validation

    if settings.wb_start_year > settings.wb_end_year:
        raise ValueError(
            "WB_START_YEAR cannot be greater than WB_END_YEAR"
        )

    if settings.wb_page_size <= 0:
        raise ValueError("WB_PAGE_SIZE must be greater than zero")

    if settings.wb_timeout_seconds <= 0:
        raise ValueError(
            "WB_TIMEOUT_SECONDS must be greater than zero"
        )

    if settings.wb_max_retries < 0:
        raise ValueError("WB_MAX_RETRIES cannot be negative")

    if settings.wb_backoff_factor < 0:
        raise ValueError(
            "WB_BACKOFF_FACTOR cannot be negative"
        )

    if settings.app_env not in {
        "development", "testing", "production"
    }:
        raise ValueError("Invalid APP_ENV")

    if settings.log_level not in {
        "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    }:
        raise ValueError("Invalid LOG_LEVEL")

    return settings
