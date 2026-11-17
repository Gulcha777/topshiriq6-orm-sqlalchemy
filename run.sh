#!/usr/bin/env bash
# Butun loyihani ketma-ket ishga tushiradi.
set -e
cd "$(dirname "$0")"

pip install -q -r requirements.txt
[ -f .env ] || cp .env.example .env

echo "=== 1. Ulanishni tekshirish ==="
python -m app.connect_check
echo
echo "=== 2. Migratsiyalar ==="
alembic upgrade head
echo
echo "=== 3. Seed ==="
python -m app.seed
echo
echo "=== 4. Bog'lanishlar ==="
python -m app.relationships_demo
echo
echo "=== 5. N+1 oldin/keyin ==="
python -m app.n_plus_one
echo
echo "=== 6. Lazy / Eager / kesh ==="
python -m app.lazy_eager
