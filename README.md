# Topshiriq №6: ORM orqali ma'lumotlar bazasi bilan ishlash

SQLAlchemy 2.0 (Python) yordamida ma'lumotlar bazasiga ulanish, entity'lar va ular orasidagi bog'lanishlarni sozlash, Alembic migratsiyalari hamda N+1 muammosini aniqlash va bartaraf etish.

## Nimalar bajarilgan

| Vazifa | Mazmuni | Qayerda |
|---|---|---|
| 1 | ORM loyihasini ulash, connection string va sozlamalarni `.env` orqali boshqarish | `app/config.py`, `app/database.py`, `app/connect_check.py`, `.env.example` |
| 2 | 5 ta entity (User, Product, Order, OrderItem, Category), One-to-Many va Many-to-Many bog'lanishlar | `app/models.py`, `app/relationships_demo.py` |
| 3 | 3 ta alohida migratsiya, seed ma'lumotlar, SQL logda N+1 ni aniqlash va tuzatish | `migrations/versions/`, `app/seed.py`, `app/n_plus_one.py` |
| Qo'shimcha | Lazy/Eager loading va 1-daraja kesh namoyishi, Talaba-Kurs-O'qituvchi ER diagrammasi | `app/lazy_eager.py`, `app/research_models.py` |

## ER diagramma

![ER diagramma](docs/er_diagram.png)

Bog'lanishlar:

- `User` 1 : N `Order` (One-to-Many)
- `Order` 1 : N `OrderItem` (One-to-Many)
- `Product` 1 : N `OrderItem` (One-to-Many)
- `Product` N : M `Category` (Many-to-Many, `product_categories` oraliq jadvali orqali)

Talaba-Kurs-O'qituvchi domeni uchun diagramma: `docs/er_talaba_kurs_oqituvchi.png`.

## Texnologiyalar

- Python 3.10 va undan yuqori
- SQLAlchemy 2.0 (ORM)
- Alembic (migratsiyalar)
- python-dotenv (`.env` sozlamalari)
- SQLite (standart) yoki PostgreSQL
- pytest (testlar)

## Loyiha tuzilmasi

```
.
├── app/
│   ├── config.py             # .env dan sozlamalarni o'qish
│   ├── database.py           # Engine va Session
│   ├── models.py             # ORM entity'lar va bog'lanishlar
│   ├── connect_check.py      # Vazifa 1: ulanishni tekshirish
│   ├── relationships_demo.py # Vazifa 2: bog'lanishlar namoyishi
│   ├── seed.py               # Vazifa 3: seed ma'lumotlar
│   ├── sql_counter.py        # SQL so'rovlarni sanash va N+1 ni aniqlash
│   ├── n_plus_one.py         # Vazifa 3: N+1 oldin/keyin
│   ├── lazy_eager.py         # Lazy, Eager va kesh namoyishi
│   ├── research_models.py    # Talaba-Kurs-O'qituvchi modellari
│   └── er_diagram.py         # ER diagramma generatori
├── migrations/versions/      # 0001, 0002, 0003 migratsiyalari
├── tests/                    # pytest testlari
├── docs/                     # ER diagrammalar va SQL log fayllari
├── alembic.ini
├── requirements.txt
├── .env.example
├── run.sh / run.bat          # hammasini ketma-ket ishga tushirish
└── test.sh / test.bat        # testlarni ishga tushirish
```

## Ishga tushirish

```bash
# 1. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 2. Sozlamalar faylini yaratish
cp .env.example .env          # Windows: copy .env.example .env

# 3. Bazaga ulanishni tekshirish (Vazifa 1)
python -m app.connect_check

# 4. Migratsiyalarni bajarish (Vazifa 3)
alembic upgrade head

# 5. Seed ma'lumotlarni qo'shish
python -m app.seed

# 6. Bog'lanishlar namoyishi (Vazifa 2)
python -m app.relationships_demo

# 7. N+1 muammosi: oldin va keyin (Vazifa 3)
python -m app.n_plus_one

# 8. Lazy/Eager loading va kesh
python -m app.lazy_eager
```

Yoki hammasini birdaniga: `./run.sh` (Windows: `run.bat`).

### PostgreSQL bilan ishlatish

`requirements.txt` ichida `psycopg2-binary` qatorini oching, so'ng `.env` faylida yozing:

```
DATABASE_URL=postgresql+psycopg2://foydalanuvchi:parol@localhost:5432/shop_db
```

Boshqa hech narsani o'zgartirish shart emas: kod va migratsiyalar ikkala bazada ishlaydi.

## Migratsiyalar

| Fayl | Nima qiladi |
|---|---|
| `0001_initial_schema.py` | Boshlang'ich sxema: 6 ta jadval |
| `0002_add_user_phone.py` | `users` jadvaliga yangi `phone` ustunini qo'shadi |
| `0003_add_indexes.py` | 4 ta indeks yaratadi (`orders.user_id`, `order_items.order_id`, `order_items.product_id`, `products.name`) |

Orqaga qaytarish: `alembic downgrade -1`. Hozirgi holat: `alembic current`.

## N+1 muammosi

Barcha buyurtmalar bo'yicha hisobot (buyurtma, mijoz, mahsulotlar, summa) tayyorlanganda:

| Usul | SQL so'rovlar soni |
|---|---|
| Oldin: standart (lazy) yuklash | 111 |
| Keyin: `joinedload` + `selectinload` | 2 |

Sabab: har bir buyurtma uchun `order.items` va har bir qator uchun `item.product` alohida SELECT bilan yuklangan. Yechim: kerakli bog'lanishlarni so'rov bilan birga oldindan yuklash:

```python
select(Order).options(
    joinedload(Order.user),
    selectinload(Order.items).joinedload(OrderItem.product),
)
```

To'liq SQL loglar: `docs/sql_log_oldin.txt` va `docs/sql_log_keyin.txt`.

## Testlar

```bash
python -m pytest -q        # yoki ./test.sh
```

37 ta test: konfiguratsiya, modellar va cheklovlar, bog'lanishlar, cascade, seed, migratsiyalar (oldinga, orqaga, modellar bilan mosligi), N+1 aniqlash va eager loading.
