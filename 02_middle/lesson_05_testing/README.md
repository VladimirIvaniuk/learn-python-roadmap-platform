# Урок 5 — Тестування: pytest та FastAPI

## Що вивчимо
- Чому тести це інвестиція, а не трата часу
- pytest: фікстури, параметризація, маркери
- Мокування: `unittest.mock`, `pytest-mock`
- Тестування FastAPI через `TestClient` та `httpx.AsyncClient`
- Тестування з БД: `SQLite in-memory`, тестові фікстури
- Покриття коду: `pytest-cov`
- TDD підхід — коротко

---

## Теорія

### 1. Навіщо тести?

```
Без тестів:              З тестами:
├── Зміна коду          ├── Зміна коду
├── "Здається OK"       ├── pytest → всі зелені ✅
├── Deploy              ├── Deploy
└── Баги у продакшені   └── Впевненість у змінах
```

**Піраміда тестів:**
```
        /\
       /E2E\           ← мало, дорогі
      /------\
     /Інтеграційні\    ← середньо
    /──────────────\
   /   Unit тести   \  ← багато, дешеві, швидкі
  /──────────────────\
```

---

### 2. pytest — основи

```python
# tests/test_math.py

def add(a, b):
    return a + b

# Проста перевірка
def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_add_floats():
    assert abs(add(0.1, 0.2) - 0.3) < 1e-10

# Очікуємо виключення
import pytest

def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("ділення на нуль")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError, match="ділення на нуль"):
        divide(10, 0)

def test_divide_value_error():
    with pytest.raises(TypeError):
        divide("10", 2)
```

```bash
pytest tests/             # запуск всіх тестів
pytest -v                 # verbose
pytest -k "test_add"      # тільки тести з "test_add" в назві
pytest -x                 # зупинитись на першій помилці
pytest --tb=short         # короткий traceback
```

---

### 3. Фікстури — `@pytest.fixture`

```python
import pytest
from typing import Generator

# Фікстура — shared код між тестами
@pytest.fixture
def sample_user() -> dict:
    return {"id": 1, "name": "Аліса", "email": "alice@example.com", "active": True}

@pytest.fixture
def inactive_user() -> dict:
    return {"id": 2, "name": "Боб", "email": "bob@example.com", "active": False}

def test_user_is_active(sample_user):
    assert sample_user["active"] is True

def test_inactive_user(inactive_user):
    assert inactive_user["active"] is False

# Фікстура зі scope — виконується раз для всієї сесії тестів
@pytest.fixture(scope="session")
def db_engine():
    from sqlalchemy import create_engine
    from models import Base
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

# Фікстура з teardown (cleanup)
@pytest.fixture
def db_session(db_engine) -> Generator:
    from sqlalchemy.orm import Session
    with Session(db_engine) as session:
        yield session
        session.rollback()   # відкат після кожного тесту

# conftest.py — фікстури доступні у всій директорії тестів
```

---

### 4. Параметризація

```python
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (100, -50, 50),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected

# Параметризація для виключень
@pytest.mark.parametrize("username, expected_error", [
    ("", "Ім'я не може бути порожнім"),
    ("ab", "Мінімум 3 символи"),
    ("a" * 51, "Максимум 50 символів"),
    ("Invalid Name!", "Тільки літери"),
])
def test_invalid_username(username, expected_error):
    with pytest.raises(ValueError, match=expected_error):
        validate_username(username)

# Маркери — групування тестів
@pytest.mark.slow
def test_expensive_operation():
    ...

@pytest.mark.integration
def test_database_connection():
    ...

# Запуск тільки "slow" тестів:
# pytest -m slow
# Пропустити "slow":
# pytest -m "not slow"
```

---

### 5. Мокування

```python
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import pytest

# Базове мокування
def send_email(to: str, subject: str) -> bool:
    # імітація відправки
    return True

def register_user(email: str, email_sender):
    user = {"email": email, "id": 1}
    email_sender.send(to=email, subject="Вітаємо!")
    return user

def test_register_user_sends_email():
    mock_sender = Mock()
    user = register_user("test@example.com", mock_sender)

    # Перевіряємо що mock викликали з правильними аргументами
    mock_sender.send.assert_called_once_with(
        to="test@example.com",
        subject="Вітаємо!"
    )
    assert user["email"] == "test@example.com"

# patch — заміна під час тесту
@patch("mymodule.send_email")
def test_with_patch(mock_send_email):
    mock_send_email.return_value = True
    result = process_registration("test@example.com")
    assert mock_send_email.called

# Контекстний менеджер
def test_with_context_patch():
    with patch("mymodule.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 3, 1, 12, 0)
        result = get_current_time()
        assert result == "12:00"

# AsyncMock — для async функцій
@pytest.mark.asyncio
async def test_async_function():
    mock_db = AsyncMock()
    mock_db.get.return_value = {"id": 1, "name": "Аліса"}

    result = await get_user(1, db=mock_db)
    assert result["name"] == "Аліса"
    mock_db.get.assert_awaited_once_with(User, 1)
```

---

### 6. Тестування FastAPI

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from main import app
from core.database import get_db
from models import Base

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db(test_engine):
    with Session(test_engine) as session:
        yield session
        session.rollback()

@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# tests/test_users.py
def test_create_user(client):
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "password" not in data   # пароль не витікає!

def test_create_user_duplicate(client):
    payload = {"username": "alice", "email": "alice@example.com", "password": "pass1234"}
    client.post("/api/auth/register", json=payload)   # перший раз
    response = client.post("/api/auth/register", json=payload)  # другий раз
    assert response.status_code == 409   # Conflict

def test_get_user_not_found(client):
    response = client.get("/api/users/99999")
    assert response.status_code == 404

def test_protected_endpoint_without_token(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401

def test_login(client, db):
    # Спочатку реєструємо
    client.post("/api/auth/register", json={
        "username": "logintest", "email": "login@test.com", "password": "pass1234"
    })
    # Потім логінимось
    response = client.post("/api/auth/login", json={
        "email": "login@test.com", "password": "pass1234"
    })
    assert response.status_code == 200
    assert "token" in response.json()
```

---

### 7. Покриття коду

```bash
# Встановлення
pip install pytest-cov

# Запуск з покриттям
pytest --cov=. --cov-report=term-missing

# Генерація HTML звіту
pytest --cov=. --cov-report=html

# Мінімальне покриття (CI/CD)
pytest --cov=. --cov-fail-under=80
```

**Що означає 80% coverage:**
- Не панацея — 100% coverage ≠ відсутність багів
- Вказує на ділянки без тестів
- Не тестуй геттери/сеттери — фокус на бізнес-логіку

---

## Що маєш вміти після уроку
- [ ] Написати pytest тест з фікстурою і `assert`
- [ ] Параметризувати тест через `@pytest.mark.parametrize`
- [ ] Замокати зовнішній виклик через `patch`
- [ ] Написати тест FastAPI ендпоінту через `TestClient`
- [ ] Запустити тести з покриттям і прочитати звіт

---

## Що далі
`task.md`. Потім — **Урок 6: DevOps**.
