from app.lazy_eager import count_queries, first_level_cache
from sqlalchemy.orm import joinedload, selectinload


def test_lazy_causes_n_plus_one(seeded):
    engine, factory = seeded
    assert count_queries(engine, factory, lambda s: s) == 21  # 1 + 20 foydalanuvchi


def test_joinedload_single_query(seeded):
    from app.models import User
    engine, factory = seeded
    assert count_queries(engine, factory, lambda s: s.options(joinedload(User.orders))) == 1


def test_selectinload_two_queries(seeded):
    from app.models import User
    engine, factory = seeded
    assert count_queries(engine, factory, lambda s: s.options(selectinload(User.orders))) == 2


def test_first_level_cache(seeded):
    engine, factory = seeded
    first, second = first_level_cache(engine, factory)
    assert (first, second) == (1, 0)
