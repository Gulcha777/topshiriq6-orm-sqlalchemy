"""Engine va Session yaratish."""
from __future__ import annotations

import warnings

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


def make_engine(url: str | None = None, echo: bool | None = None) -> Engine:
    """Connection string bo'yicha Engine yaratadi (standart: .env dagi DATABASE_URL)."""
    settings = get_settings()
    url = url or settings.database_url
    echo = settings.sql_echo if echo is None else echo
    engine = create_engine(url, echo=echo)

    if engine.dialect.name == "sqlite":
        # SQLite'da tashqi kalitlar standart holda o'chiq turadi, yoqib qo'yamiz.
        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _record):  # pragma: no cover
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        # SQLite Decimal'ni to'g'ridan-to'g'ri saqlamaydi; SQLAlchemy ogohlantirishi shart emas.
        warnings.filterwarnings(
            "ignore", message=r".*does \*not\* support Decimal objects natively.*"
        )
    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
