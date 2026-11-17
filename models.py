"""ORM modellar (entity'lar).

Bog'lanishlar:
  User 1 --- N Order           (One-to-Many)
  Order 1 --- N OrderItem      (One-to-Many)
  Product 1 --- N OrderItem    (One-to-Many)
  Product N --- M Category     (Many-to-Many, product_categories jadvali orqali)
  Order N --- M Product        (OrderItem assotsiatsiya ob'ekti orqali)
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Cheklov nomlari bir xil bo'lishi uchun (migratsiyalar bilan mos kelishi uchun).
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Many-to-Many: Product <-> Category uchun oraliq jadval
product_categories = Table(
    "product_categories",
    Base.metadata,
    Column(
        "product_id",
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    # 0002-migratsiya orqali qo'shilgan ustun
    phone: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # One-to-Many: bitta foydalanuvchining ko'p buyurtmasi
    orders: Mapped[list[Order]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, full_name={self.full_name!r})"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)

    # Many-to-Many
    products: Mapped[list[Product]] = relationship(
        secondary=product_categories, back_populates="categories"
    )

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name={self.name!r})"


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (CheckConstraint("price >= 0", name="price_non_negative"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    # 0003-migratsiya orqali indeks qo'shilgan ustun
    name: Mapped[str] = mapped_column(String(120), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(default=0, server_default="0")

    # Many-to-Many
    categories: Mapped[list[Category]] = relationship(
        secondary=product_categories, back_populates="products"
    )
    # One-to-Many
    order_items: Mapped[list[OrderItem]] = relationship(back_populates="product")

    def __repr__(self) -> str:
        return f"Product(id={self.id}, name={self.name!r})"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="new", server_default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Many-to-One (teskari tomoni User.orders)
    user: Mapped[User] = relationship(back_populates="orders")
    # One-to-Many
    items: Mapped[list[OrderItem]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    @property
    def total(self) -> Decimal:
        """Buyurtma umumiy summasi."""
        return sum((i.quantity * i.unit_price for i in self.items), Decimal("0"))

    def __repr__(self) -> str:
        return f"Order(id={self.id}, user_id={self.user_id}, status={self.status!r})"


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (CheckConstraint("quantity > 0", name="quantity_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )
    quantity: Mapped[int] = mapped_column(default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="order_items")

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price

    def __repr__(self) -> str:
        return f"OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id})"
