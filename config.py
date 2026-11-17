"""Konfiguratsiya: connection string va sozlamalar .env faylidan o'qiladi."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE_URL = f"sqlite:///{BASE_DIR / 'shop.db'}"

# .env fayli bo'lsa o'qiladi; mavjud muhit o'zgaruvchilari ustun turadi.
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    database_url: str
    sql_echo: bool


def get_settings() -> Settings:
    """Sozlamalarni har safar muhit o'zgaruvchilaridan o'qiydi."""
    url = os.getenv("DATABASE_URL", "").strip() or DEFAULT_DATABASE_URL
    echo = os.getenv("SQL_ECHO", "0").strip().lower() in {"1", "true", "yes", "on"}
    return Settings(database_url=url, sql_echo=echo)
