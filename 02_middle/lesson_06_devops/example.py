"""
Урок Middle 6 — DevOps конфігурація

Цей файл демонструє pydantic-settings підхід до конфігурації.
Реальний Dockerfile та docker-compose.yml — у директорії поряд.

pip install pydantic-settings python-dotenv
"""
import os
from pathlib import Path


# ── pydantic-settings (без залежності — власна реалізація) ───────────────────
class Settings:
    """
    Конфігурація з ENV змінних.
    Реальний проєкт: from pydantic_settings import BaseSettings
    """
    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "LearnPython API")
        self.version: str = os.getenv("APP_VERSION", "1.0.0")
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-in-prod!")
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.cors_origins: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        self.jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    def __repr__(self) -> str:
        safe = {k: v for k, v in vars(self).items() if "secret" not in k.lower()}
        return f"Settings({safe})"

    def is_production(self) -> bool:
        return not self.debug and "sqlite" not in self.database_url


settings = Settings()
print("=== Конфігурація ===")
print(f"App: {settings.app_name} v{settings.version}")
print(f"Debug: {settings.debug}")
print(f"DB: {settings.database_url}")
print(f"Production: {settings.is_production()}")


# ── Безпечне читання .env ─────────────────────────────────────────────────────
def load_env_file(path: str = ".env") -> dict[str, str]:
    """Простий парсер .env файлу."""
    env_path = Path(path)
    if not env_path.exists():
        return {}
    env_vars: dict[str, str] = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars


# Демо .env файл
demo_env = Path(".env.example")
demo_env.write_text(
    "# Шаблон .env файлу (комітуй у git)\n"
    "SECRET_KEY=\n"
    "DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db\n"
    "DEBUG=false\n"
    "PORT=8000\n"
    "CORS_ORIGINS=http://localhost:3000,https://myapp.com\n"
)
print(f"\n.env.example створено: {demo_env.exists()}")
print(f"Вміст:\n{demo_env.read_text()}")


# ── Conventional commits приклади ─────────────────────────────────────────────
COMMIT_EXAMPLES = [
    ("feat(auth)",    "add JWT refresh token endpoint"),
    ("fix(db)",       "resolve N+1 query in user listing"),
    ("docs(api)",     "add OpenAPI examples for all endpoints"),
    ("test(users)",   "add integration tests for CRUD operations"),
    ("refactor(orm)", "migrate to SQLAlchemy 2.0 mapped_column syntax"),
    ("chore(deps)",   "update fastapi to 0.111.0"),
    ("ci",            "add pytest coverage threshold 80%"),
]

print("\n=== Conventional Commits приклади ===")
for type_scope, desc in COMMIT_EXAMPLES:
    print(f"  git commit -m \"{type_scope}: {desc}\"")


# ── Healthcheck endpoint (додати в main.py) ───────────────────────────────────
HEALTHCHECK_CODE = '''
@app.get("/health")
async def health_check():
    """Healthcheck для Docker та load balancer."""
    return {
        "status": "healthy",
        "version": settings.version,
        "timestamp": datetime.utcnow().isoformat(),
    }
'''
print(f"\n=== Healthcheck ендпоінт ===")
print(HEALTHCHECK_CODE)


# ── Makefile вміст ────────────────────────────────────────────────────────────
MAKEFILE_CONTENT = """.PHONY: install dev run test lint format build up down

install:
\tpip install -r requirements.txt

dev: install
\tpip install -r requirements-dev.txt

run:
\tuvicorn main:app --reload --port 8000

test:
\tpytest -v --tb=short

test-cov:
\tpytest --cov=. --cov-report=term-missing --cov-fail-under=80

lint:
\truff check . && mypy .

format:
\truff format . && isort .

build:
\tdocker build -t learn-python .

up:
\tdocker compose up -d

down:
\tdocker compose down
"""

makefile = Path("Makefile.example")
makefile.write_text(MAKEFILE_CONTENT)
print("Makefile.example створено")

# Cleanup
demo_env.unlink()
makefile.unlink()
