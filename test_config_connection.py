from app.config import DEFAULT_DATABASE_URL, get_settings
from app.connect_check import check_connection


def test_settings_read_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///custom.db")
    monkeypatch.setenv("SQL_ECHO", "1")
    s = get_settings()
    assert s.database_url == "sqlite:///custom.db"
    assert s.sql_echo is True


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SQL_ECHO", raising=False)
    s = get_settings()
    assert s.database_url == DEFAULT_DATABASE_URL
    assert s.sql_echo is False


def test_connection_ok():
    info = check_connection("sqlite://")
    assert info["select_1"] == 1
    assert info["dialect"] == "sqlite"


def test_password_is_hidden():
    info = check_connection("sqlite://")
    assert "password" not in info["url"].lower()
