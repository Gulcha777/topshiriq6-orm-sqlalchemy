"""Vazifa 1: bazaga ulanishni tekshirish (connection string .env dan olinadi).

Ishga tushirish:  python -m app.connect_check
"""
from __future__ import annotations

from sqlalchemy import text

from app.database import make_engine


def check_connection(url: str | None = None) -> dict:
    engine = make_engine(url)
    with engine.connect() as conn:
        one = conn.execute(text("SELECT 1")).scalar_one()
        if engine.dialect.name == "sqlite":
            version = conn.execute(text("SELECT sqlite_version()")).scalar_one()
        else:
            version = conn.execute(text("SELECT version()")).scalar_one()
    return {
        "url": engine.url.render_as_string(hide_password=True),
        "dialect": engine.dialect.name,
        "server_version": str(version),
        "select_1": one,
    }


def main() -> None:
    info = check_connection()
    print("Ulanish muvaffaqiyatli")
    print(f"  Connection string : {info['url']}")
    print(f"  Dialect           : {info['dialect']}")
    print(f"  Server versiyasi  : {info['server_version']}")
    print(f"  SELECT 1 natijasi : {info['select_1']}")


if __name__ == "__main__":
    main()
