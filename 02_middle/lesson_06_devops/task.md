# Завдання — DevOps

## Завдання 1 — Dockerfile
Напиши `Dockerfile` для твого FastAPI проєкту:
- Multi-stage build (builder → runtime)
- Не запускати від root
- `HEALTHCHECK` через `/health` ендпоінт
- `CMD` через `uvicorn` з правильними параметрами
Запусти контейнер і перевір `curl http://localhost:8000/health`.

## Завдання 2 — Docker Compose
Напиши `docker-compose.yml`:
- `web`: твій FastAPI
- `db`: PostgreSQL 16 з healthcheck і persistent volume
- `redis`: Redis 7 (опціонально)
- Налаштуй залежності (`depends_on`)
Перевір: `docker compose up` → API працює → `docker compose down -v` → дані видалені.

## Завдання 3 — pydantic-settings
Перенеси всі хардкоджені налаштування FastAPI до `Settings` класу.
Читай з `.env` файлу. Зроби так щоб `DATABASE_URL`, `SECRET_KEY`, `DEBUG`
можна було змінювати через ENV змінні без змін в коді.

## Завдання 4 — Makefile
Напиши `Makefile` з командами:
`install`, `dev`, `run`, `test`, `test-cov`, `lint`, `format`, `build`, `up`, `down`, `clean`.
Усі мають бути `.PHONY`.

## Завдання 5 (Challenge) — GitHub Actions
Напиши `.github/workflows/ci.yml` що:
1. Запускається на PR та push до main
2. Встановлює залежності з кешем pip
3. Запускає ruff check та mypy
4. Запускає pytest з coverage ≥ 80%
5. Деплоїть (echo "deploy") тільки при push до main
