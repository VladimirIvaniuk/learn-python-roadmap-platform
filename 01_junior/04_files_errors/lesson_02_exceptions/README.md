# Урок 2 — Виключення та обробка помилок

## Що вивчимо
- Ієрархія виключень Python
- `try / except / else / finally`
- Множинні `except`, перехоплення різних типів
- `raise` — власне виключення
- Власні класи виключень
- `ExceptionGroup` (Python 3.11+)
- Принципи правильної обробки помилок

---

## Теорія

### 1. Ієрархія виключень

```
BaseException
├── SystemExit              ← sys.exit()
├── KeyboardInterrupt       ← Ctrl+C
├── GeneratorExit
└── Exception               ← усі "звичайні" помилки успадковуються тут
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   └── OverflowError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── TypeError
    ├── ValueError
    ├── AttributeError
    ├── NameError
    ├── OSError
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   └── TimeoutError
    ├── RuntimeError
    ├── StopIteration
    └── ...
```

---

### 2. `try / except / else / finally`

```python
try:
    # ← код що може кинути виключення
    result = 10 / 0
except ZeroDivisionError as e:
    # ← виконується якщо виникло ZeroDivisionError
    print(f"Ділення на нуль: {e}")
except (TypeError, ValueError) as e:
    # ← кілька типів в одному except
    print(f"Помилка типу або значення: {e}")
except Exception as e:
    # ← будь-яке інше виключення (використай як останній resort)
    print(f"Несподівана помилка: {type(e).__name__}: {e}")
else:
    # ← виконується тільки якщо НЕ було виключення
    print(f"Результат: {result}")
finally:
    # ← виконується ЗАВЖДИ (і при виключенні, і без)
    print("Завершено (cleanup код тут)")
```

**Практичний приклад:**
```python
import json
from pathlib import Path

def load_config(filepath: str) -> dict:
    """Завантажує JSON-конфіг з обробкою всіх можливих помилок."""
    path = Path(filepath)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Файл не знайдено: {filepath}. Використовую дефолтний конфіг.")
        return {}
    except PermissionError:
        print(f"Немає прав на читання: {filepath}")
        raise   # перекидаємо виключення далі
    else:
        # Успішно прочитали файл
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Невалідний JSON у {filepath}: {e}")
            return {}
```

---

### 3. `raise` — підняття виключень

```python
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("Ділник не може бути нулем")
    return a / b

def process_age(age: int) -> str:
    if not isinstance(age, int):
        raise TypeError(f"Вік має бути int, отримано {type(age).__name__}")
    if age < 0 or age > 150:
        raise ValueError(f"Некоректний вік: {age}. Допустимо 0-150.")
    return "дорослий" if age >= 18 else "неповнолітній"

# raise без аргументу — перекидає поточне виключення
def safe_parse(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        print(f"Не вдалось розібрати '{text}'")
        raise   # ← перекидаємо той самий ValueError далі

# raise ... from ... — chained exceptions
def fetch_user(user_id: int):
    try:
        return database.get(user_id)
    except DatabaseError as e:
        raise RuntimeError(f"Не вдалось отримати користувача {user_id}") from e
        # Зберігає оригінальне виключення в __cause__
```

---

### 4. Власні виключення

```python
# Базовий клас для всіх помилок застосунку
class AppError(Exception):
    """Базовий клас виключень Learn Python."""

    def __init__(self, message: str, code: str = "APP_ERROR"):
        super().__init__(message)
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {super().__str__()}"


class ValidationError(AppError):
    """Помилка валідації вхідних даних."""

    def __init__(self, field: str, message: str):
        super().__init__(f"Поле '{field}': {message}", code="VALIDATION_ERROR")
        self.field = field


class NotFoundError(AppError):
    """Ресурс не знайдено."""

    def __init__(self, resource: str, resource_id):
        super().__init__(f"{resource} з id={resource_id} не знайдено", code="NOT_FOUND")


class AuthError(AppError):
    """Помилка авторизації."""
    pass


# Використання
def get_user(user_id: int) -> dict:
    if user_id <= 0:
        raise ValidationError("user_id", "Має бути позитивним")
    user = db.get(user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user

# Обробка
try:
    user = get_user(-1)
except ValidationError as e:
    print(f"400 Bad Request: {e}")
    print(f"Поле: {e.field}")
except NotFoundError as e:
    print(f"404 Not Found: {e}")
except AppError as e:
    print(f"Загальна помилка: {e} (код: {e.code})")
```

---

### 5. `else` та `finally` — деталі

```python
def read_file_safe(path: str) -> str | None:
    f = None
    try:
        f = open(path, encoding="utf-8")
        return f.read()
    except FileNotFoundError:
        return None
    finally:
        if f:
            f.close()   # виконається завжди, навіть при return!

# Важливо: finally з return замінює попередній return
def tricky():
    try:
        return "try"
    finally:
        return "finally"   # ← повертає "finally"!

print(tricky())   # "finally"  — finally перекрив try

# else — тільки якщо success
def connect_db():
    try:
        conn = create_connection()
    except ConnectionError as e:
        log.error(f"Не вдалось підключитись: {e}")
        raise
    else:
        # Виконується тільки при успішному підключенні
        log.info("Підключено до БД")
        return conn
```

---

### 6. ExceptionGroup (Python 3.11+)

```python
# Декілька виключень одночасно
def validate_form(data: dict) -> None:
    errors = []
    if not data.get("name"):
        errors.append(ValueError("Ім'я обов'язкове"))
    if not data.get("email") or "@" not in data["email"]:
        errors.append(ValueError("Email невалідний"))
    if errors:
        raise ExceptionGroup("Помилки валідації форми", errors)

try:
    validate_form({"name": "", "email": "bad-email"})
except* ValueError as eg:
    for exc in eg.exceptions:
        print(f"  - {exc}")
```

---

### 7. `warnings` — некритичні попередження

```python
import warnings

def old_function(x):
    warnings.warn(
        "old_function() застаріла. Використовуй new_function()",
        DeprecationWarning,
        stacklevel=2,
    )
    return new_function(x)

# Фільтрація warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("error", category=UserWarning)  # перетворити на помилку
```

---

### Принципи правильної обробки помилок

```python
# ✅ Принцип 1: Перехоплюй конкретні типи, не Exception
try:
    value = int(user_input)
except ValueError:   # конкретно — неправильний формат числа
    value = 0

# ❌ Не роби це — прихована помилка
try:
    value = int(user_input)
except Exception:    # занадто широко!
    value = 0        # захоплює і KeyboardInterrupt, і SystemExit, і MemoryError

# ✅ Принцип 2: Не мовчи про помилки — логуй
import logging
logger = logging.getLogger(__name__)

try:
    result = risky_operation()
except SomeError as e:
    logger.exception("risky_operation() провалилась")  # логує + traceback
    result = default_value

# ✅ Принцип 3: Перекидай якщо не знаєш що робити
def process(data):
    try:
        return transform(data)
    except TransformError:
        logger.warning("Трансформація провалилась")
        raise   # нехай виклики вище вирішують

# ✅ Принцип 4: Fail Fast — краще впасти рано з зрозумілою помилкою
def create_user(email: str, password: str):
    if not email:
        raise ValueError("Email не може бути порожнім")
    if len(password) < 8:
        raise ValueError("Пароль мінімум 8 символів")
    # ... далі без зайвих перевірок
```

---

### Типові помилки

```python
# ❌ Пустий except — "поглинає" всі помилки мовчки
try:
    risky()
except:         # пуста! перехоплює навіть SystemExit, KeyboardInterrupt
    pass        # проблема "зникає" безслідно

# ❌ Занадто широкий except
try:
    result = complex_operation()
except Exception as e:
    print(e)    # що робити далі? невідомо

# ❌ Логіка у finally
try:
    data = fetch()
except NetworkError:
    data = []
finally:
    process(data)   # ❌ якщо fetch() кинула NameError, data не визначена!

# ✅ Правильно — ініціалізувати data до try
data = []
try:
    data = fetch()
except NetworkError:
    pass
process(data)

# ❌ print замість raise при критичній помилці
def save_to_db(user):
    try:
        db.insert(user)
    except DatabaseError as e:
        print(f"Помилка: {e}")  # виконання продовжується! користувач не збережений
```

---

### У реальному проєкті

```python
# FastAPI exception handlers
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc)},
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"error": f"Шлях {request.url.path} не знайдено"},
    )

# Декоратор для retry логіки
import time, functools

def retry(times: int = 3, delay: float = 1.0, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        raise
                    print(f"Спроба {attempt} провалилась: {e}. Повторюємо...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(times=3, delay=2.0, exceptions=(ConnectionError, TimeoutError))
def fetch_data(url: str) -> dict:
    return requests.get(url, timeout=5).json()
```

---

## Що маєш вміти після уроку
- [ ] Написати `try/except/else/finally` з конкретними типами виключень
- [ ] Підняти власне виключення через `raise` з зрозумілим повідомленням
- [ ] Створити ієрархію власних виключень
- [ ] Пояснити навіщо `finally` (cleanup, закриття ресурсів)
- [ ] Написати декоратор `retry`

---

## Що далі
Виконай завдання з `task.md`. Потім — **Рівень Middle!**
