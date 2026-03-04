# Урок 5 — Безпека: OWASP Top 10 у Python/FastAPI

## Що вивчимо
- OWASP Top 10 2021 — найпоширеніші вразливості
- SQL Injection та захист через параметризовані запити
- JWT безпека: алгоритми, термін дії, refresh tokens
- Хешування паролів: bcrypt, argon2
- XSS, CSRF захист
- Секрети та змінні середовища
- Dependency scanning

---

## Теорія

### 1. OWASP Top 10 і Python

```
A01 Broken Access Control   → Перевіряй permissions, не тільки authentication
A02 Cryptographic Failures  → bcrypt, не MD5/SHA1 для паролів
A03 Injection              → SQLAlchemy ORM, ніяких f-strings у SQL
A04 Insecure Design        → Принцип мінімальних привілеїв
A05 Security Misconfiguration → DEBUG=False, SECRET_KEY з env
A06 Vulnerable Components  → pip audit, dependabot
A07 Auth/Session Failures  → JWT термін дії, invalidation
A08 Data Integrity Failures → Перевіряй підпис JWT, CSRF токени
A09 Logging/Monitoring     → Логуй security events
A10 SSRF                   → Whitelist URL для зовнішніх запитів
```

---

### 2. SQL Injection

```python
# ❌ ВРАЗЛИВО — SQL Injection!
async def get_user_bad(username: str, db: Session) -> User:
    # Якщо username = "' OR '1'='1"  → витікають усі дані!
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query).fetchone()

# ❌ Теж вразливо з SQLAlchemy
result = db.execute(text(f"SELECT * FROM users WHERE id = {user_id}"))

# ✅ Безпечно — параметризовані запити
from sqlalchemy import text, select

async def get_user_safe_raw(username: str, db: Session) -> User:
    result = db.execute(
        text("SELECT * FROM users WHERE username = :username"),
        {"username": username}   # ← параметр, не f-string
    )
    return result.fetchone()

# ✅ Ще краще — ORM (автоматично безпечний)
async def get_user_orm(username: str, db: Session) -> User | None:
    return db.execute(
        select(User).where(User.username == username)  # безпечно!
    ).scalar_one_or_none()

# ✅ Валідація вхідних даних (Pydantic)
from pydantic import BaseModel, field_validator

class SearchParams(BaseModel):
    query: str
    page: int = 1

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        # Дозволяємо тільки алфавіт, цифри, пробіли
        import re
        if not re.match(r'^[\w\s\-]+$', v):
            raise ValueError("Query contains invalid characters")
        return v.strip()
```

---

### 3. Безпечне зберігання паролів

```python
# ❌ MD5/SHA1 — не для паролів!
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()  # НІКОЛИ!
hashed = hashlib.sha256(password.encode()).hexdigest()  # Теж ні для паролів!

# Чому MD5/SHA1 недостатньо?
# 1. Дуже швидкі → GPU brute force → мільярди спроб/секунду
# 2. Rainbow tables — преобчислені хеші популярних паролів
# 3. Однакові паролі → однакові хеші (без salt)

# ✅ bcrypt — повільний за дизайном (1000-5000 хешів/секунду)
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)  # 12 = ~0.3с на хеш
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# Перевірка
hashed = hash_password("my_password_123")
print(verify_password("my_password_123", hashed))  # True
print(verify_password("wrong_password", hashed))   # False

# ✅ Або passlib (абстракція над bcrypt/argon2)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Якщо потрібно оновити схему — passlib автоматично
```

---

### 4. JWT безпека

```python
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt   # pip install PyJWT

SECRET_KEY = "very-secret-key"   # повинен бути в ENV!
ALGORITHM = "HS256"

# ✅ Правильне створення JWT
def create_access_token(subject: str | int, expires_delta: timedelta = timedelta(hours=1)) -> str:
    payload = {
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + expires_delta,
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(subject: str | int) -> str:
    payload = {
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
        "type": "refresh",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Токен закінчився")
    except jwt.InvalidTokenError:
        raise ValueError("Невалідний токен")

    if payload.get("type") != token_type:
        raise ValueError(f"Очікується {token_type} токен")

    return payload

# ❌ Поширені помилки з JWT
# 1. Алгоритм "none" — дозволяє підробити токен!
# jwt.decode(token, "", algorithms=["none"])  # НІКОЛИ!

# 2. Зберігання чутливих даних у payload
# JWT ПІДПИСАНИЙ, але не ЗАШИФРОВАНИЙ — декодується без ключа!
import base64, json

def decode_jwt_payload_unsafe(token: str) -> dict:
    """Демонстрація: payload видно без ключа!"""
    _, payload_b64, _ = token.split(".")
    padding = 4 - len(payload_b64) % 4
    payload_b64 += "=" * padding
    return json.loads(base64.b64decode(payload_b64))

# Ніколи не клади в JWT: паролі, SSN, кредитні картки, секрети

# 3. Відсутня інвалідація при logout
class TokenBlacklist:
    """Простий blacklist (продакшн — Redis з TTL)"""
    _revoked: set[str] = set()

    @classmethod
    def revoke(cls, token: str) -> None:
        cls._revoked.add(token)

    @classmethod
    def is_revoked(cls, token: str) -> bool:
        return token in cls._revoked

def logout(token: str) -> None:
    TokenBlacklist.revoke(token)

def verify_token_with_blacklist(token: str) -> dict:
    if TokenBlacklist.is_revoked(token):
        raise ValueError("Токен відкликано")
    return verify_token(token)
```

---

### 5. Захист від інших атак

```python
# XSS (Cross-Site Scripting) — в FastAPI
# FastAPI автоматично екранує JSON, але в шаблонах — будь обережний
from markupsafe import escape   # якщо використовуєш Jinja2

@app.get("/search")
async def search(q: str):
    # ❌ НЕ вставляй user input напряму в HTML
    return f"<p>Результати для {q}</p>"

    # ✅ Або автоматично через Jinja2 escape, або JSON API
    return {"results": [], "query": q}   # JSON API — безпечний

# CORS — правильне налаштування
from fastapi.middleware.cors import CORSMiddleware

# ❌ В продакшені
app.add_middleware(CORSMiddleware, allow_origins=["*"])  # занадто широко!

# ✅ Тільки потрібні origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com", "https://www.myapp.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
)

# Security Headers
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Rate Limiting для Auth ендпоінтів
@app.post("/auth/login")
@limiter.limit("5/minute")   # max 5 спроб на хвилину
async def login(credentials: LoginRequest):
    ...

# Input validation — завжди через Pydantic
class FileUpload(BaseModel):
    filename: str
    content_type: str

    @field_validator("filename")
    @classmethod
    def safe_filename(cls, v: str) -> str:
        import re
        # Заборона path traversal
        if ".." in v or "/" in v or "\\" in v:
            raise ValueError("Invalid filename")
        # Тільки безпечні символи
        if not re.match(r'^[\w\-. ]+$', v):
            raise ValueError("Filename contains invalid characters")
        return v

    @field_validator("content_type")
    @classmethod
    def allowed_content_type(cls, v: str) -> str:
        allowed = {"image/jpeg", "image/png", "image/gif", "application/pdf"}
        if v not in allowed:
            raise ValueError(f"File type {v} not allowed")
        return v
```

---

### 6. Секрети та конфігурація

```python
# ❌ НІКОЛИ не хардкодь секрети!
DATABASE_URL = "postgresql://admin:mysecretpassword@db.prod.com/mydb"
SECRET_KEY = "super-secret-key-123"
API_KEY = "sk-1234567890abcdef"

# ✅ Тільки через ENV змінні
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str         # обов'язкове
    secret_key: str           # обов'язкове
    api_key: str | None = None  # необов'язкове

    class Config:
        env_file = ".env"

# .gitignore завжди містить:
# .env
# *.key
# secrets.json

# Перевірка що секрети не потрапили в git
# pip install detect-secrets
# detect-secrets scan . --baseline .secrets.baseline
```

---

## Що маєш вміти після уроку
- [ ] Пояснити різницю SQL injection через raw SQL vs ORM
- [ ] Використати `bcrypt` для хешування та перевірки паролів
- [ ] Реалізувати JWT з терміном дії та типом токена
- [ ] Налаштувати CORS тільки для потрібних origins
- [ ] Перенести всі секрети в ENV змінні

---

## Що далі
`task.md`. Потім — **Урок 6: Soft Skills**.
