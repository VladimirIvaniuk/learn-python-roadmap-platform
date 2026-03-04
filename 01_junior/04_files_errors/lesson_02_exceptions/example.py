"""
Урок 2 — Приклади: виключення та обробка помилок
"""
import time
import functools
from contextlib import contextmanager


# ── Власні виключення ─────────────────────────────────────────────────────────
class AppError(Exception):
    def __init__(self, message: str, code: str = "APP_ERROR") -> None:
        super().__init__(message)
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {super().__str__()}"


class ValidationError(AppError):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"Поле '{field}': {message}", "VALIDATION_ERROR")
        self.field = field


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id) -> None:
        super().__init__(f"{resource} id={resource_id} не знайдено", "NOT_FOUND")


# ── try/except/else/finally ───────────────────────────────────────────────────
def safe_divide(a: float, b: float) -> float | None:
    try:
        result = a / b
    except ZeroDivisionError:
        print("  Ділення на нуль!")
        return None
    except TypeError as e:
        print(f"  Невірний тип: {e}")
        return None
    else:
        return result
    finally:
        pass   # cleanup якщо потрібно

print("safe_divide:")
print(f"  10/2 = {safe_divide(10, 2)}")
print(f"  10/0 = {safe_divide(10, 0)}")


# ── Raise та валідація ────────────────────────────────────────────────────────
def create_user(name: str, email: str, password: str) -> dict:
    errors = []
    if not name or not name.replace(" ", "").isalpha():
        errors.append(ValidationError("name", "Тільки літери та пробіли"))
    if not email or "@" not in email:
        errors.append(ValidationError("email", "Невалідний email"))
    if len(password) < 8:
        errors.append(ValidationError("password", "Мінімум 8 символів"))

    if errors:
        # Виводимо всі помилки
        raise ExceptionGroup("Помилки валідації", errors)

    return {"name": name, "email": email}


print("\ncreate_user:")
try:
    user = create_user("", "bad-email", "123")
except* ValidationError as eg:
    for exc in eg.exceptions:
        print(f"  ❌ {exc}")

try:
    user = create_user("Аліса", "alice@example.com", "secure123")
    print(f"  ✅ Користувач створений: {user}")
except* ValidationError:
    pass


# ── Retry декоратор ───────────────────────────────────────────────────────────
def retry(times: int = 3, delay: float = 0.0, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        raise
                    print(f"  Спроба {attempt} провалилась: {e}. Повторюємо...")
                    if delay > 0:
                        time.sleep(delay)
        return wrapper
    return decorator


_call_count = 0

@retry(times=3, exceptions=(ValueError,))
def flaky_function():
    global _call_count
    _call_count += 1
    if _call_count < 3:
        raise ValueError(f"Ще не готово (спроба {_call_count})")
    return "Успіх!"

print("\nRetry:")
print(f"  {flaky_function()}")


# ── Context manager для вимірювання ──────────────────────────────────────────
class Timer:
    def __enter__(self) -> "Timer":
        self._t = time.perf_counter()
        return self

    def __exit__(self, *args) -> bool:
        print(f"  Виконано за {time.perf_counter() - self._t:.4f}с")
        return False   # не пригнічуємо виключення

@contextmanager
def timer(label: str = ""):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"  {label}: {elapsed:.4f}с")

print("\nTimers:")
with Timer():
    _ = [x**2 for x in range(100_000)]

with timer("comprehension"):
    _ = [x**2 for x in range(100_000)]


# ── Raise from (chaining) ─────────────────────────────────────────────────────
def fetch_from_db(user_id: int) -> dict:
    raw_data = None   # імітація
    try:
        return raw_data["user"]   # TypeError
    except TypeError as e:
        raise NotFoundError("User", user_id) from e

print("\nChained exception:")
try:
    fetch_from_db(42)
except NotFoundError as e:
    print(f"  {e}")
    print(f"  Причина: {e.__cause__}")
