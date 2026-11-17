"""Vazifa 2: bog'lanishlar (One-to-Many va Many-to-Many) namoyishi.

Alohida xotiradagi (in-memory) SQLite bazada ishlaydi, shuning uchun asosiy bazaga tegmaydi.
Ishga tushirish:  python -m app.relationships_demo
"""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from app.database import make_engine, make_session_factory
from app.models import Base, Category, Order, OrderItem, Product, User


def main() -> None:
    engine = make_engine("sqlite://")
    Base.metadata.create_all(engine)
    with make_session_factory(engine)() as session:
        electronics = Category(name="Elektronika")
        sport = Category(name="Sport")
        laptop = Product(name="Noutbuk", price=Decimal("7500000"), categories=[electronics])
        headset = Product(name="Quloqchin", price=Decimal("350000"), categories=[electronics, sport])
        user = User(full_name="Aziz Karimov", email="aziz@example.com")

        # One-to-Many: User -> Order -> OrderItem
        order = Order(user=user)
        order.items.append(OrderItem(product=laptop, quantity=1, unit_price=laptop.price))
        order.items.append(OrderItem(product=headset, quantity=2, unit_price=headset.price))
        session.add_all([user, order])
        session.commit()

        print("One-to-Many:")
        print(f"  {user.full_name} buyurtmalari: {[o.id for o in user.orders]}")
        print(f"  Buyurtma #{order.id} qatorlari: {[i.product.name for i in order.items]}")
        print(f"  Buyurtma summasi: {order.total}")

        print("Many-to-Many:")
        for p in session.scalars(select(Product).order_by(Product.id)):
            print(f"  {p.name}: kategoriyalar = {sorted(c.name for c in p.categories)}")
        print(f"  Elektronika mahsulotlari: {sorted(p.name for p in electronics.products)}")

        # cascade="all, delete-orphan": foydalanuvchi o'chsa, buyurtmalari ham o'chadi
        session.delete(user)
        session.commit()
        left = session.scalars(select(OrderItem)).all()
        print(f"Cascade: foydalanuvchi o'chirilgach OrderItem qolgani: {len(left)}")


if __name__ == "__main__":
    main()
