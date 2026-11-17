from sqlalchemy import func, select

from app.models import Category, Order, OrderItem, Product, User
from app.seed import clear_all, seed


def test_seed_counts(seeded):
    _, factory = seeded
    with factory() as s:
        assert s.scalar(select(func.count(User.id))) == 20
        assert s.scalar(select(func.count(Category.id))) == 6
        assert s.scalar(select(func.count(Product.id))) == 30
        assert s.scalar(select(func.count(Order.id))) == 60
        assert s.scalar(select(func.count(OrderItem.id))) > 60


def test_seed_is_idempotent(seeded):
    _, factory = seeded
    with factory() as s:
        assert seed(s) is False
        assert s.scalar(select(func.count(User.id))) == 20


def test_seed_is_deterministic(engine, factory):
    with factory() as s:
        seed(s)
        first = [(o.user_id, o.total) for o in s.scalars(select(Order).order_by(Order.id))]
        clear_all(s)
        seed(s)
        second = [(o.user_id, o.total) for o in s.scalars(select(Order).order_by(Order.id))]
    assert first == second


def test_every_product_has_category(seeded):
    _, factory = seeded
    with factory() as s:
        assert all(p.categories for p in s.scalars(select(Product)))
