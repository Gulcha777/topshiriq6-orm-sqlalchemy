import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import make_engine, make_session_factory  # noqa: E402
from app.models import Base  # noqa: E402
from app.seed import seed  # noqa: E402


@pytest.fixture()
def engine():
    eng = make_engine("sqlite://", echo=False)
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def factory(engine):
    return make_session_factory(engine)


@pytest.fixture()
def session(factory):
    with factory() as s:
        yield s


@pytest.fixture()
def seeded(engine, factory):
    with factory() as s:
        seed(s)
    return engine, factory
