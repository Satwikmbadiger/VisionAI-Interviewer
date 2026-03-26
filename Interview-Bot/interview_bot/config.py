from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    model: str = "openai/gpt-oss-120b"
    db_path: Path = Path.home() / ".interview_bot" / "interview_bot.sqlite3"
    log_level: str = "INFO"


def load_settings() -> Settings:
    # Load .env if present (non-fatal)
    load_dotenv(override=False)
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    model = os.getenv("INTERVIEW_BOT_MODEL", "openai/gpt-oss-120b").strip()
    log_level = os.getenv("INTERVIEW_BOT_LOG_LEVEL", "INFO").strip().upper()
    db_path = Path(os.getenv("INTERVIEW_BOT_DB", "")).expanduser() if os.getenv("INTERVIEW_BOT_DB") else None

    if not api_key:
        raise RuntimeError(
            "Missing GROQ_API_KEY. Set it as an environment variable or in a .env file."
        )

    return Settings(
        groq_api_key=api_key,
        model=model or "openai/gpt-oss-120b",
        db_path=db_path if db_path is not None else Settings.db_path,
        log_level=log_level or "INFO",
    )


