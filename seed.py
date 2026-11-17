"""Seed ma'lumotlar: foydalanuvchilar, kategoriyalar, mahsulotlar va buyurtmalar.

Ishga tushirish:  python -m app.seed          (bo'sh bazaga)
                  python -m app.seed --reset  (avval hammasini o'chirib)
Ma'lumotlar tasodifiy, lekin urug' (seed) qat'iy bo'lgani uchun har safar bir xil chiqadi.
"""
from __future__ import annotations

import random
import sys
from decimal import Decimal

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.database import make_engine, make_session_factory
from app.models import Category, Order, OrderItem, Product, User, product_categories

CATEGORIES = ["Elektronika", "Kitoblar", "Kiyim", "Uy-ro'zg'or", "Sport", "Oziq-ovqat"]

# (nomi, narxi, asosiy kategoriya indeksi, qo'shimcha kategoriya indeksi yoki None)
PRODUCTS = [
    ("Noutbuk", "7500000.00", 0, None),
    ("Smartfon", "4200000.00", 0, None),
    ("Quloqchin", "350000.00", 0, 4),
    ("Sichqoncha", "120000.00", 0, None),
    ("Klaviatura", "210000.00", 0, None),
    ("Monitor", "2100000.00", 0, None),
    ("Python dasturlash kitobi", "95000.00", 1, None),
    ("SQL asoslari kitobi", "88000.00", 1, None),
    ("Ingliz tili darsligi", "76000.00", 1, None),
    ("Algoritmlar kitobi", "110000.00", 1, 0),
    ("Futbolka", "85000.00", 2, 4),
    ("Kurtka", "560000.00", 2, None),
    ("Krossovka", "430000.00", 2, 4),
    ("Jinsi shim", "320000.00", 2, None),
    ("Choynak", "98000.00", 3, None),
    ("Kosa to'plami", "145000.00", 3, None),
    ("Pichoq to'plami", "175000.00", 3, None),
    ("Qozon", "390000.00", 3, 5),
    ("Futbol to'pi", "130000.00", 4, None),
    ("Yoga gilami", "99000.00", 4, None),
    ("Gantel", "160000.00", 4, None),
    ("Velosiped", "2800000.00", 4, None),
    ("Guruch 5 kg", "78000.00", 5, None),
    ("Yog' 1 l", "24000.00", 5, 3),
    ("Choy 500 g", "42000.00", 5, None),
    ("Shakar 1 kg", "14000.00", 5, None),
    ("Planshet", "3100000.00", 0, None),
    ("Powerbank", "190000.00", 0, None),
    ("Ryukzak", "240000.00", 2, 4),
    ("Termos", "115000.00", 3, 4),
]

USERS = [
    ("Aziz Karimov", "aziz.karimov"), ("Dilnoza Rahimova", "dilnoza.rahimova"),
    ("Sardor Yusupov", "sardor.yusupov"), ("Malika Abdullayeva", "malika.abdullayeva"),
    ("Jasur Tursunov", "jasur.tursunov"), ("Nigora Ergasheva", "nigora.ergasheva"),
    ("Bobur Mirzayev", "bobur.mirzayev"), ("Zilola Sodiqova", "zilola.sodiqova"),
    ("Otabek Nazarov", "otabek.nazarov"), ("Shahnoza Qodirova", "shahnoza.qodirova"),
    ("Humoyun Ismoilov", "humoyun.ismoilov"), ("Madina Hasanova", "madina.hasanova"),
    ("Timur Saidov", "timur.saidov"), ("Feruza Normatova", "feruza.normatova"),
    ("Anvar Olimov", "anvar.olimov"), ("Gulnora Umarova", "gulnora.umarova"),
    ("Rustam Boboyev", "rustam.boboyev"), ("Sevara Aliyeva", "sevara.aliyeva"),
    ("Doston Xolmatov", "doston.xolmatov"), ("Lola Komilova", "lola.komilova"),
]

STATUSES = ["new", "paid", "shipped", "delivered"]


def is_seeded(session: Session) -> bool:
    return (session.scalar(select(func.count(User.id))) or 0) > 0


def clear_all(session: Session) -> None:
    session.execute(delete(OrderItem))
    session.execute(delete(Order))
    session.execute(delete(product_categories))
    session.execute(delete(Product))
    session.execute(delete(Category))
    session.execute(delete(User))
    session.commit()


def seed(session: Session, orders_count: int = 60, rng_seed: int = 42) -> bool:
    """Bazani to'ldiradi. Baza bo'sh bo'lmasa hech narsa qilmaydi va False qaytaradi."""
    if is_seeded(session):
        return False
    rng = random.Random(rng_seed)

    categories = [Category(name=n) for n in CATEGORIES]
    session.add_all(categories)

    products = []
    for name, price, main_cat, extra_cat in PRODUCTS:
        p = Product(name=name, price=Decimal(price), stock=rng.randint(5, 100))
        p.categories.append(categories[main_cat])
        if extra_cat is not None:
            p.categories.append(categories[extra_cat])
        products.append(p)
    session.add_all(products)

    users = [
        User(
            full_name=full_name,
            email=f"{email}@example.com",
            phone=f"+99890{rng.randint(1000000, 9999999)}" if i % 4 else None,
        )
        for i, (full_name, email) in enumerate(USERS)
    ]
    session.add_all(users)

    for _ in range(orders_count):
        order = Order(user=rng.choice(users), status=rng.choice(STATUSES))
        for product in rng.sample(products, k=rng.randint(1, 4)):
            order.items.append(
                OrderItem(
                    product=product,
                    quantity=rng.randint(1, 3),
                    unit_price=product.price,
                )
            )
        session.add(order)

    session.commit()
    return True


def main() -> None:
    engine = make_engine()
    with make_session_factory(engine)() as session:
        if "--reset" in sys.argv:
            clear_all(session)
        if seed(session):
            print(
                "Seed bajarildi: "
                f"{session.scalar(select(func.count(User.id)))} foydalanuvchi, "
                f"{session.scalar(select(func.count(Category.id)))} kategoriya, "
                f"{session.scalar(select(func.count(Product.id)))} mahsulot, "
                f"{session.scalar(select(func.count(Order.id)))} buyurtma, "
                f"{session.scalar(select(func.count(OrderItem.id)))} buyurtma qatori"
            )
        else:
            print("Baza bo'sh emas, seed o'tkazib yuborildi (qaytadan to'ldirish: --reset).")


if __name__ == "__main__":
    main()
