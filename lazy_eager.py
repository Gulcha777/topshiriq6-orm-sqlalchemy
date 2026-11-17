"""Lazy va Eager loading hamda 1-daraja kesh (Session identity map) namoyishi.

Ishga tushirish:  python -m app.lazy_eager
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload, subqueryload

from app.database import make_engine, make_session_factory
from app.models import Order, User
from app.sql_counter import QueryCounter


def count_queries(engine, factory, load_orders) -> int:
    """Foydalanuvchilarni yuklab, har birining buyurtmalariga murojaat qiladi."""
    with factory() as session, QueryCounter(engine) as qc:
        users = session.scalars(load_orders(select(User))).unique().all()
        for user in users:
            _ = [o.id for o in user.orders]
    return qc.count


def first_level_cache(engine, factory) -> tuple[int, int]:
    """session.get() ni ikki marta chaqirish: 2-chaqiruv SQL yubormaydi (identity map)."""
    with factory() as session:
        with QueryCounter(engine) as first:
            u1 = session.get(User, 1)
        with QueryCounter(engine) as second:
            u2 = session.get(User, 1)
        assert u1 is u2  # xuddi shu Python ob'ekti
    return first.count, second.count


def main() -> None:
    engine = make_engine(echo=False)
    factory = make_session_factory(engine)

    print("Foydalanuvchilar va ularning buyurtmalari (har bir User.orders ga murojaat):")
    variants = {
        "lazy (standart)        ": lambda s: s,
        "joinedload             ": lambda s: s.options(joinedload(User.orders)),
        "selectinload           ": lambda s: s.options(selectinload(User.orders)),
        "subqueryload           ": lambda s: s.options(subqueryload(User.orders)),
    }
    for title, fn in variants.items():
        print(f"  {title}: {count_queries(engine, factory, fn)} ta SQL so'rov")

    print()
    print("1-daraja kesh (Session identity map):")
    a, b = first_level_cache(engine, factory)
    print(f"  session.get(User, 1) 1-chaqiruv: {a} ta so'rov")
    print(f"  session.get(User, 1) 2-chaqiruv: {b} ta so'rov (keshdan olindi)")


if __name__ == "__main__":
    main()
