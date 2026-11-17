@echo off
cd /d "%~dp0"
pip install -q -r requirements.txt
if not exist .env copy .env.example .env

echo === 1. Ulanishni tekshirish ===
python -m app.connect_check || exit /b 1
echo.
echo === 2. Migratsiyalar ===
alembic upgrade head || exit /b 1
echo.
echo === 3. Seed ===
python -m app.seed || exit /b 1
echo.
echo === 4. Boglanishlar ===
python -m app.relationships_demo || exit /b 1
echo.
echo === 5. N+1 oldin/keyin ===
python -m app.n_plus_one || exit /b 1
echo.
echo === 6. Lazy / Eager / kesh ===
python -m app.lazy_eager
