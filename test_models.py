from decimal import Decimal

import pytest
from sqlalchemy import select, inspect
from sqlalchemy.exc import IntegrityError

from app.models import Category, Order, OrderItem, Product, User, Base


def make_user(email="a@example.com"):
    return User(full_name="Test User", email=email)


def test_all_tables_exist(engine):
    names = set(inspect(engine).get_table_names())
    assert {"users", "categories", "products", "product_categories", "orders", "order_items"} <= names


def test_one_to_many_user_orders(session):
    user = make_user()
    user.orders.append(Order())
    user.orders.append(Order())
    session.add(user)
    session.commit()
    assert len(session.get(User, user.id).orders) == 2
    assert all(o.user is user for o in user.orders)


def test_one_to_many_order_items_and_total(session):
    p1 = Product(name="A", price=Decimal("10.50"))
    p2 = Product(name="B", price=Decimal("4.00"))
    order = Order(user=make_user())
    order.items.append(OrderItem(product=p1, quantity=2, unit_price=p1.price))
    order.items.append(OrderItem(product=p2, quantity=3, unit_price=p2.price))
    session.add(order)
    session.commit()
    assert order.total == Decimal("33.00")


def test_many_to_many_products_categories(session):
    c1, c2 = Category(name="C1"), Category(name="C2")
    p = Product(name="P", price=Decimal("1"), categories=[c1, c2])
    session.add(p)
    session.commit()
    assert sorted(c.name for c in p.categories) == ["C1", "C2"]
    assert c1.products == [p] and c2.products == [p]


def test_many_to_many_removal(session):
    c = Category(name="C")
    p = Product(name="P", price=Decimal("1"), categories=[c])
    session.add(p)
    session.commit()
    p.categories.remove(c)
    session.commit()
    assert c.products == []


def test_cascade_delete_user_removes_orders_and_items(session):
    p = Product(name="P", price=Decimal("5"))
    user = make_user()
    order = Order(user=user)
    order.items.append(OrderItem(product=p, quantity=1, unit_price=p.price))
    session.add(user)
    session.commit()
    session.delete(user)
    session.commit()
    assert session.scalars(select(Order)).all() == []
    assert session.scalars(select(OrderItem)).all() == []
    assert session.scalars(select(Product)).all() == [p]  # mahsulot saqlanadi


def test_email_is_unique(session):
    session.add_all([make_user("same@example.com"), make_user("same@example.com")])
    with pytest.raises(IntegrityError):
        session.commit()


def test_quantity_must_be_positive(session):
    p = Product(name="P", price=Decimal("5"))
    order = Order(user=make_user())
    order.items.append(OrderItem(product=p, quantity=0, unit_price=p.price))
    session.add(order)
    with pytest.raises(IntegrityError):
        session.commit()


def test_price_non_negative(session):
    session.add(Product(name="P", price=Decimal("-1")))
    with pytest.raises(IntegrityError):
        session.commit()


def test_foreign_key_enforced(session):
    session.add(Order(user_id=999))
    with pytest.raises(IntegrityError):
        session.commit()


def test_phone_is_optional(session):
    u = make_user()
    session.add(u)
    session.commit()
    assert u.phone is None


def test_order_default_status(session):
    o = Order(user=make_user())
    session.add(o)
    session.commit()
    assert o.status == "new"
