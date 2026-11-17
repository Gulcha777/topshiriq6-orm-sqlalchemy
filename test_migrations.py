import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

from app.config import BASE_DIR
from app.models import Base


def alembic_config(url: str) -> Config:
    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BASE_DIR / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


@pytest.fixture()
def db_url(tmp_path):
    return f"sqlite:///{tmp_path / 'test.db'}"


def test_three_separate_migrations():
    script = ScriptDirectory.from_config(alembic_config("sqlite://"))
    revisions = [r.revision for r in script.walk_revisions()]
    assert sorted(revisions) == ["0001", "0002", "0003"]
    assert script.get_current_head() == "0003"


def test_0001_creates_initial_schema(db_url):
    command.upgrade(alembic_config(db_url), "0001")
    insp = inspect(create_engine(db_url))
    assert {"users", "orders", "order_items", "products", "categories",
            "product_categories"} <= set(insp.get_table_names())
    assert "phone" not in [c["name"] for c in insp.get_columns("users")]
    assert insp.get_indexes("orders") == []


def test_0002_adds_phone_column(db_url):
    command.upgrade(alembic_config(db_url), "0002")
    insp = inspect(create_engine(db_url))
    cols = {c["name"]: c for c in insp.get_columns("users")}
    assert "phone" in cols and cols["phone"]["nullable"] is True


def test_0003_creates_indexes(db_url):
    command.upgrade(alembic_config(db_url), "head")
    insp = inspect(create_engine(db_url))
    assert {i["name"] for i in insp.get_indexes("orders")} == {"ix_orders_user_id"}
    assert {i["name"] for i in insp.get_indexes("order_items")} == {
        "ix_order_items_order_id", "ix_order_items_product_id"}
    assert {i["name"] for i in insp.get_indexes("products")} == {"ix_products_name"}


def test_models_match_migrations(db_url):
    """Modellar bilan migratsiyalar natijasi orasida farq bo'lmasligi kerak."""
    command.upgrade(alembic_config(db_url), "head")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn, opts={"compare_type": True})
        assert compare_metadata(ctx, Base.metadata) == []


def test_downgrade_to_base(db_url):
    cfg = alembic_config(db_url)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "0002")
    insp = inspect(create_engine(db_url))
    assert insp.get_indexes("orders") == []
    command.downgrade(cfg, "0001")
    assert "phone" not in [c["name"] for c in inspect(create_engine(db_url)).get_columns("users")]
    command.downgrade(cfg, "base")
    assert set(inspect(create_engine(db_url)).get_table_names()) <= {"alembic_version"}


def test_upgrade_is_repeatable(db_url):
    cfg = alembic_config(db_url)
    command.upgrade(cfg, "head")
    command.upgrade(cfg, "head")  # xatosiz, hech narsa o'zgarmaydi
