# 🚀 Middle Project: Async URL Shortener API

Фінальний проєкт Middle рівня — повноцінний REST API з async, ORM і тестами.

---

## 📋 Опис

URL shortener сервіс типу bit.ly/tinyurl зі статистикою кліків.

**Вхідний запит:** `POST /shorten { "url": "https://example.com/very/long/url" }`
**Результат:** `{ "short_code": "abc123", "short_url": "http://localhost:8000/abc123" }`
**Редирект:** `GET /abc123` → 302 redirect на оригінальний URL

---

## ✅ Вимоги

### Обов'язкові

#### Моделі (SQLAlchemy 2.0)

```python
class ShortURL(Base):
    id: Mapped[int]
    short_code: Mapped[str]      # унікальний, 6 символів
    original_url: Mapped[str]
    created_at: Mapped[datetime]
    expires_at: Mapped[datetime | None]
    is_active: Mapped[bool]
    click_count: Mapped[int]     # денормалізований лічильник

class Click(Base):
    id: Mapped[int]
    short_url_id: Mapped[int]    # FK → ShortURL
    clicked_at: Mapped[datetime]
    ip_address: Mapped[str]
    user_agent: Mapped[str]
```

#### API Endpoints

| Method | Path | Опис |
|--------|------|------|
| `POST` | `/shorten` | Створити короткий URL |
| `GET`  | `/{code}` | Редирект + записати клік |
| `GET`  | `/api/urls` | Список URLs (auth required) |
| `GET`  | `/api/urls/{code}/stats` | Статистика кліків |
| `DELETE` | `/api/urls/{code}` | Деактивувати URL |

#### Pydantic схеми

```python
class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_code: str | None = None  # користувацький код
    expires_in_days: int | None = Field(None, ge=1, le=365)

class URLResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    click_count: int
    created_at: datetime
    expires_at: datetime | None
```

#### Async

- `async_engine` + `AsyncSession` для всіх DB операцій
- `asyncio.gather` при паралельній роботі
- Background task для логування кліків (не блокуємо redirect)

#### Валідація і безпека

- Перевірка що URL не вказує на localhost/internal
- Rate limit: 10 скорочень на хвилину з однієї IP
- URL не може перевищувати 2048 символів
- Генерація `short_code`: `secrets.token_urlsafe(6)[:8]`

#### Тести (pytest)

- `test_shorten_url` — основний flow
- `test_redirect` — перевірка редиректу та збільшення лічильника
- `test_custom_code_conflict` — 409 Conflict
- `test_expired_url` — 410 Gone
- `test_rate_limit` — 429 Too Many Requests
- Мінімум **80% coverage**

### Додаткові (бонус)

- QR-код для short URL (бібліотека `qrcode`)
- Пагінація для `/api/urls`
- JWT автентифікація
- Alembic міграції
- Dockerfile + docker-compose
- `GET /api/urls/{code}/stats` з графіком кліків по годинах (список)

---

## 🗂 Структура проєкту

```
middle_project/
├── main.py             # FastAPI app + routes
├── models.py           # SQLAlchemy models
├── schemas.py          # Pydantic schemas
├── database.py         # async engine, session
├── services/
│   ├── shortener.py    # бізнес-логіка
│   └── analytics.py    # статистика
├── dependencies.py     # Depends functions
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── requirements.txt
└── README.md
```

---

## 🛠 Технічний стек

```txt
fastapi>=0.110
uvicorn[standard]
sqlalchemy[asyncio]>=2.0
aiosqlite          # для тестів
pydantic[email]>=2
pytest
pytest-asyncio
httpx              # для TestClient
pytest-cov
```

---

## 💡 Ключові моменти реалізації

```python
# Генерація унікального коду
import secrets, string

def generate_code(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

# Background task для кліків
@app.get("/{code}")
async def redirect(code: str, request: Request, bg: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    url = await get_url_by_code(db, code)
    if not url or not url.is_active:
        raise HTTPException(404)
    if url.expires_at and url.expires_at < datetime.utcnow():
        raise HTTPException(410, "Link expired")
    bg.add_task(record_click, db, url.id, request.client.host, request.headers.get("user-agent",""))
    return RedirectResponse(url.original_url, status_code=302)
```

---

## 🧪 Запуск

```bash
# Встановити
pip install -r requirements.txt

# Запустити
uvicorn main:app --reload

# Тести
pytest --cov=. --cov-report=term-missing -v

# Спробувати
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.python.org/3/library/asyncio.html"}'
```

---

## 📊 Критерії оцінки

| Критерій | Бали |
|----------|------|
| Всі endpoints | 20 |
| Async DB | 15 |
| Pydantic валідація | 10 |
| Background tasks | 10 |
| Rate limiting | 10 |
| Тести (≥80%) | 15 |
| Структура коду | 10 |
| Бонус | +10 |

**Прохідний бал: 70/90**
