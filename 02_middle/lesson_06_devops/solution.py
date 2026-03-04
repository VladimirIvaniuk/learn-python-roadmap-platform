"""
Розв'язки — DevOps (Middle)
Файли конфігурації написані у вигляді Python-рядків з поясненнями.
"""

# ── Завдання 1 — Dockerfile для FastAPI ──────────────────────────────────────
DOCKERFILE = """
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Безпечний не-root користувач
RUN addgroup --system app && adduser --system --group app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

EXPOSE 8000
USER app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# ── Завдання 2 — docker-compose.yml ──────────────────────────────────────────
DOCKER_COMPOSE = """
version: "3.9"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - .:/app
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
"""

# ── Завдання 3 — pydantic-settings конфіг ────────────────────────────────────
SETTINGS_PY = """
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "My FastAPI App"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "sqlite:///./db.sqlite3"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
"""

# ── Завдання 4 — Makefile ────────────────────────────────────────────────────
MAKEFILE = """
.PHONY: help install dev test lint format migrate docker-up docker-down

help:
\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \\
\t awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

install: ## Install dependencies
\tpip install -r requirements.txt

dev: ## Run dev server with hot reload
\tuvicorn main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests with coverage
\tpytest --cov=. --cov-report=term-missing -v

lint: ## Lint with ruff
\truff check .

format: ## Format with ruff
\truff format .

migrate: ## Run alembic migrations
\talembic upgrade head

docker-up: ## Start containers
\tdocker compose up -d --build

docker-down: ## Stop containers
\tdocker compose down
"""

# ── Завдання 5 (Challenge) — GitHub Actions CI ───────────────────────────────
CI_YAML = """
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Lint
        run: ruff check .

      - name: Test
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/testdb
        run: pytest --cov=. --cov-report=xml -q

      - name: Upload coverage
        uses: codecov/codecov-action@v4
"""

# ── Демонстрація ──────────────────────────────────────────────────────────────
configs = {
    "Dockerfile":             DOCKERFILE,
    "docker-compose.yml":     DOCKER_COMPOSE,
    "settings.py":            SETTINGS_PY,
    "Makefile":               MAKEFILE,
    ".github/workflows/ci.yml": CI_YAML,
}

for name, content in configs.items():
    lines = content.strip().splitlines()
    print(f"\n{'─'*60}")
    print(f"  {name}  ({len(lines)} lines)")
    print(f"{'─'*60}")
    for line in lines[:5]:
        print(f"  {line}")
    print("  ...")
