# Урок 6 — DevOps: Docker, Git Flow, CI/CD

## Що вивчимо
- Docker: образи, контейнери, `Dockerfile`
- Docker Compose: мульти-контейнерні застосунки
- Git: branch стратегії, conventional commits
- GitHub Actions: CI/CD pipeline
- Управління змінними середовища (`pydantic-settings`)
- `Makefile` — автоматизація команд
- Розгортання: Render / Railway / VPS

---

## Теорія

### 1. Docker — контейнеризація

**Чому Docker:**
```
Без Docker:           З Docker:
"У мене працює!"  →  Однаково скрізь
Python 3.10 тут  →   Python 3.12 скрізь
"Яка бібліотека?"  →  requirements.txt + lock
Важко масштабувати →  docker compose scale web=3
```

**Dockerfile для FastAPI:**
```dockerfile
# Dockerfile
FROM python:3.12-slim

# Безпека: не запускаємо від root
RUN useradd --create-home appuser
WORKDIR /app

# Спочатку лише залежності (кешується, якщо requirements не змінились)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Потім код
COPY --chown=appuser:appuser . .
USER appuser

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Збірка
docker build -t learn-python:latest .

# Запуск
docker run -p 8000:8000 --env-file .env learn-python:latest

# Перевірка
docker logs <container_id>
docker exec -it <container_id> bash
```

---

### 2. Docker Compose

```yaml
# docker-compose.yml
version: "3.9"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:secret@db:5432/appdb
      - SECRET_KEY=${SECRET_KEY}   # з .env файлу
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./:/app   # для розробки — hot reload
    command: uvicorn main:app --host 0.0.0.0 --reload

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

```bash
docker compose up -d          # запустити у фоні
docker compose logs -f web    # логи сервісу web
docker compose down           # зупинити
docker compose down -v        # зупинити + видалити volumes
docker compose exec web bash  # shell у контейнері
```

---

### 3. Змінні середовища та `pydantic-settings`

```python
# core/config.py
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    # Назви у UPPER_CASE відповідають ENV змінним
    app_name: str = "LearnPython API"
    debug: bool = False
    secret_key: str
    database_url: str = "sqlite+aiosqlite:///./app.db"
    redis_url: str = "redis://localhost:6379"
    allowed_hosts: list[str] = ["*"]
    cors_origins: list[str] = ["http://localhost:3000"]
    jwt_expire_minutes: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Singleton
settings = Settings()

# Використання
from core.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)
```

```bash
# .env файл (НЕ комітимо в git!)
SECRET_KEY=super-secret-change-me
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
DEBUG=false
JWT_EXPIRE_MINUTES=120

# .env.example (комітимо — шаблон без значень)
SECRET_KEY=
DATABASE_URL=
DEBUG=false
```

---

### 4. Git Flow та Conventional Commits

```
main     ─────●──────────────────────●─── (релізи)
              │                      ↑
develop  ─────●──●──●──●─────────────●─── (інтеграція)
              │  │  │  │
feature  ─────●──●  │  │     ← feature/auth-jwt
                 ●──●  │     ← feature/user-profile
                       ●──●  ← bugfix/login-error
```

**Conventional Commits — стандарт:**
```bash
git commit -m "feat(auth): add JWT refresh token"
git commit -m "fix(api): handle null email in registration"
git commit -m "docs: add API usage examples"
git commit -m "refactor(db): migrate to SQLAlchemy 2.0"
git commit -m "test(users): add integration tests for CRUD"
git commit -m "chore: update dependencies"
git commit -m "perf(queries): add index on users.email"

# Формат: type(scope): description
# type: feat, fix, docs, style, refactor, test, chore, perf, ci
# scope: необов'язково — модуль/компонент
```

**Branch naming:**
```bash
feature/JWT-authentication
bugfix/fix-login-crash
hotfix/critical-security-patch
release/v2.1.0
chore/update-docker-base-image
```

---

### 5. GitHub Actions — CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Run linters
        run: |
          ruff check .
          mypy .

      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost/testdb
          SECRET_KEY: test-secret
        run: pytest --cov=. --cov-report=xml --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v4

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        run: curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK }}"
```

---

### 6. `Makefile` — автоматизація

```makefile
# Makefile
.PHONY: install dev test lint format build up down clean

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	uvicorn main:app --reload --port 8000

test:
	pytest -v --tb=short

test-cov:
	pytest --cov=. --cov-report=html && open htmlcov/index.html

lint:
	ruff check . && mypy .

format:
	ruff format . && isort .

build:
	docker build -t learn-python .

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf .coverage htmlcov .mypy_cache .ruff_cache
```

```bash
make dev     # встановити dev залежності
make test    # запустити тести
make up      # підняти Docker Compose
```

---

### 7. `requirements.txt` та `pyproject.toml`

```toml
# pyproject.toml (сучасний підхід)
[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.12"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = ["slow: повільні тести", "integration: інтеграційні тести"]

[tool.coverage.report]
exclude_lines = ["if TYPE_CHECKING:", "raise NotImplementedError"]
```

---

## Що маєш вміти після уроку
- [ ] Написати `Dockerfile` для FastAPI і запустити контейнер
- [ ] Написати `docker-compose.yml` з web + db
- [ ] Налаштувати `pydantic-settings` для конфіга через ENV
- [ ] Писати коміти в форматі Conventional Commits
- [ ] Написати GitHub Actions CI pipeline з тестами

---

## Що далі
Вітаємо — ти завершив Middle рівень! Далі — **Senior рівень**.
