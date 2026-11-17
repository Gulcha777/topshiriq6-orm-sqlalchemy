"""Vazifa 3: N+1 muammosini aniqlash va bartaraf etish (oldin/keyin).

Ishga tushirish:  python -m app.n_plus_one
Natija: konsolga hisobot va docs/sql_log_oldin.txt, docs/sql_log_keyin.txt fayllari.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.config import BASE_DIR
from app.database import make_engine, make_session_factory
from app.models import Order, OrderItem
from app.sql_counter import QueryCounter, detect_n_plus_one, format_log, normalize

Row = tuple[int, str, int, Decimal, list[str]]


def _row(order: Order) -> Row:
    """Hisobot qatori: buyurtma, mijoz, qatorlar soni, summa, mahsulotlar nomi."""
    names = sorted(item.product.name for item in order.items)
    return (order.id, order.user.full_name, len(order.items), order.total, names)


def report_lazy(session: Session) -> list[Row]:
    """OLDIN: standart (lazy) yuklash. Har buyurtma uchun alohida so'rovlar ketadi."""
    orders = session.scalars(select(Order).order_by(Order.id)).all()  # 1 ta so'rov
    return [_row(o) for o in orders]  # o.user, o.items, item.product -> N ta qo'shimcha so'rov


def report_eager(session: Session) -> list[Row]:
    """KEYIN: kerakli bog'lanishlar oldindan (eager) yuklanadi."""
    stmt = (
        select(Order)
        .options(
            joinedload(Order.user),  # Many-to-One: JOIN bilan
            selectinload(Order.items).joinedload(OrderItem.product),  # One-to-Many: IN bilan
        )
        .order_by(Order.id)
    )
    orders = session.scalars(stmt).all()
    return [_row(o) for o in orders]


def run_measured(engine, session_factory, func):
    """Funksiyani toza sessiyada bajarib, so'rovlar sonini o'lchaydi."""
    with session_factory() as session, QueryCounter(engine) as qc:
        result = func(session)
    return result, qc


def main() -> None:
    engine = make_engine(echo=False)
    factory = make_session_factory(engine)

    before_rows, before = run_measured(engine, factory, report_lazy)
    after_rows, after = run_measured(engine, factory, report_eager)

    if not before_rows:
        print("Baza bo'sh. Avval: alembic upgrade head  va  python -m app.seed")
        return
    assert before_rows == after_rows, "Ikkala usul bir xil natija berishi kerak"

    docs = Path(BASE_DIR) / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "sql_log_oldin.txt").write_text(format_log(before.statements), encoding="utf-8")
    (docs / "sql_log_keyin.txt").write_text(format_log(after.statements), encoding="utf-8")

    print(f"Buyurtmalar soni: {len(before_rows)}")
    print()
    print("=== OLDIN (lazy loading) ===")
    print(f"SQL so'rovlar soni: {before.count}")
    print("N+1 belgisi (bir xil SQL ko'p marta takrorlangan):")
    for sql, n in detect_n_plus_one(before.statements)[:3]:
        print(f"  {n:>3} marta: {sql[:95]}...")
    print()
    print("=== KEYIN (joinedload + selectinload) ===")
    print(f"SQL so'rovlar soni: {after.count}")
    for i, (sql, _) in enumerate(after.statements, 1):
        print(f"  [{i}] {normalize(sql)[:95]}...")
    print()
    print(f"Kamayish: {before.count} -> {after.count} ta so'rov "
          f"({before.count / after.count:.0f} baravar kam)")


if __name__ == "__main__":
    main()
