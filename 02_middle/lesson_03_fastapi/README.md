# Урок 3 — FastAPI: REST API від A до Z

## Що вивчимо
- Маршрути: GET, POST, PUT, DELETE, path/query/body параметри
- Pydantic: валідація, серіалізація, `model_validator`, `field_validator`
- Залежності (`Depends`): авторизація, БД-сесії
- Middleware: CORS, логування, rate limiting
- Обробка помилок: `HTTPException`, власні exception handlers
- Фонові задачі: `BackgroundTasks`
- OpenAPI документація: теги, опис, приклади

---

## Теорія

### 1. Структура застосунку

```
my_api/
├── main.py              ← Ініціалізація FastAPI, middleware, startup
├── routers/
│   ├── users.py         ← /api/users маршрути
│   └── items.py         ← /api/items маршрути
├── models/
│   ├── schemas.py       ← Pydantic схеми (вхід/вихід)
│   └── database.py      ← SQLAlchemy моделі
├── services/
│   └── user_service.py  ← Бізнес-логіка
├── core/
│   ├── config.py        ← Налаштування (pydantic-settings)
│   └── security.py      ← JWT, хешування паролів
└── tests/
    └── test_users.py
```

---

### 2. Параметри маршрутів

```python
from fastapi import FastAPI, Path, Query, Body, Header, Cookie
from typing import Annotated

app = FastAPI(title="My API", version="1.0")

# Path параметри — частина URL
@app.get("/users/{user_id}")
async def get_user(
    user_id: Annotated[int, Path(gt=0, description="ID користувача")]
):
    return {"user_id": user_id}

# Query параметри — після ?
@app.get("/users/")
async def list_users(
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    search: str | None = None,
    active: bool = True,
):
    return {"page": page, "per_page": per_page, "search": search}

# Body — JSON тіло запиту
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@app.post("/users/", status_code=201)
async def create_user(user: UserCreate):
    # user.username, user.email — вже перевірені Pydantic!
    return {"id": 1, **user.model_dump(exclude={"password"})}
```

---

### 3. Pydantic — глибоке занурення

```python
from pydantic import BaseModel, EmailStr, field_validator, model_validator, Field
from datetime import datetime
from typing import Annotated

# Annotation-based валідація
PositiveInt = Annotated[int, Field(gt=0)]
NonEmptyStr = Annotated[str, Field(min_length=1, max_length=100)]

class UserCreate(BaseModel):
    username: NonEmptyStr
    email: EmailStr
    age: PositiveInt
    password: str = Field(min_length=8, exclude=True)  # не потрапить у output

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("Тільки літери, цифри та _")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль має містити хоч одну цифру")
        return v

class UserDB(UserCreate):
    id: int
    created_at: datetime
    is_active: bool = True

class UserResponse(BaseModel):
    """Те що повертаємо клієнту — без password!"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}   # SQLAlchemy model → Pydantic

# @model_validator — валідація всього об'єкта
class DateRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def check_dates(self) -> "DateRange":
        if self.end <= self.start:
            raise ValueError("end має бути після start")
        return self
```

---

### 4. Залежності — `Depends`

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Проста залежність — пагінація
class Pagination:
    def __init__(self, page: int = 1, per_page: int = 20):
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page

def get_pagination(page: int = 1, per_page: int = 20) -> Pagination:
    return Pagination(page, per_page)

@app.get("/items/")
async def get_items(pagination: Pagination = Depends(get_pagination)):
    items = db.all()[pagination.offset:pagination.offset + pagination.per_page]
    return {"items": items, "page": pagination.page}

# Ланцюг залежностей — авторизація
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = verify_jwt(token)   # кидає HTTPException якщо невалідний
    user = db.query(User).get(payload["sub"])
    if not user:
        raise HTTPException(401, "Користувач не знайдений")
    return user

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, "Потрібні права адміна")
    return user

@app.delete("/users/{user_id}", dependencies=[Depends(require_admin)])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404)
    db.delete(user)
    db.commit()
    return {"deleted": user_id}
```

---

### 5. Middleware

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time, logging

logger = logging.getLogger(__name__)

# CORS — дозволяємо запити з браузерів
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# GZip стиснення відповідей
app.add_middleware(GZipMiddleware, minimum_size=500)

# Власний middleware — логування запитів
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(f"{request.method} {request.url.path} → {response.status_code} ({elapsed:.0f}ms)")
        response.headers["X-Process-Time"] = str(elapsed)
        return response

app.add_middleware(LoggingMiddleware)
```

---

### 6. Обробка помилок

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Власні виключення
class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "ERROR"):
        self.message = message
        self.status_code = status_code
        self.code = code

class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: int):
        super().__init__(f"{resource} id={resource_id} не знайдено", 404, "NOT_FOUND")

# Handlers
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "code": exc.code},
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Помилки валідації",
            "details": [
                {"field": ".".join(str(e) for e in err["loc"][1:]), "message": err["msg"]}
                for err in exc.errors()
            ]
        }
    )
```

---

### 7. Фонові задачі та lifecycle

```python
from fastapi import BackgroundTasks
from contextlib import asynccontextmanager

# Lifecycle — startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Ініціалізація БД...")
    await init_db()
    print("Сервер готовий!")
    yield
    # Shutdown
    print("Закриваємо з'єднання...")
    await close_db()

app = FastAPI(lifespan=lifespan)

# Background tasks — виконуються ПІСЛЯ відповіді
def send_welcome_email(email: str, username: str):
    # Важко: це sync функція — не блокуємо response
    send_email(email, f"Вітаємо, {username}!")

@app.post("/users/")
async def create_user(user: UserCreate, background_tasks: BackgroundTasks):
    new_user = await user_service.create(user)
    background_tasks.add_task(send_welcome_email, user.email, user.username)
    return new_user   # відповідь іде одразу, email відправляється у фоні
```

---

### Типові помилки

```python
# ❌ Sync функція в async endpoint — блокує event loop
@app.get("/slow")
async def slow_endpoint():
    time.sleep(5)   # БЛОКУЄ! Використовуй await asyncio.sleep(5)

# ❌ БД-сесія без Depends
db_session = SessionLocal()   # глобальна сесія — race conditions!

@app.get("/users/{id}")
async def get_user(user_id: int):
    return db_session.get(User, user_id)

# ✅ Через Depends — кожен запит отримує свою сесію
@app.get("/users/{id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.get(User, user_id)

# ❌ Повертаємо SQLAlchemy об'єкт напряму
@app.get("/users/{id}")
async def get_user(user_id: int):
    return db.get(User, user_id)   # LazyLoadingError при серіалізації!

# ✅ Перетворюємо через Pydantic response_model
@app.get("/users/{id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.get(User, user_id)
```

---

## Що маєш вміти після уроку
- [ ] Написати CRUD ендпоінти з path/query/body параметрами
- [ ] Написати Pydantic схему з `@field_validator`
- [ ] Реалізувати авторизацію через JWT + `Depends`
- [ ] Написати middleware для логування
- [ ] Обробити ValidationError та повернути зрозуміле повідомлення

---

## Що далі
`task.md`. Потім — **Урок 4: Бази даних**.
