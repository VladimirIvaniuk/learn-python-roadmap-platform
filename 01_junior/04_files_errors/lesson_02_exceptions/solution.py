"""
Розв'язки — Урок 2: Виключення
"""
import time
from contextlib import contextmanager
from functools import wraps

# ── Завдання 1 — safe_calculator() ───────────────────────────────────────────
def safe_calculator(a_str: str, op: str, b_str: str) -> float | str:
    try:
        a = float(a_str)
        b = float(b_str)
    except ValueError:
        return "Помилка: введіть числа"

    match op:
        case "+": return a + b
        case "-": return a - b
        case "*": return a * b
        case "/":
            if b == 0:
                raise ZeroDivisionError("Ділення на нуль неможливе")
            return a / b
        case _:
            raise ValueError(f"Невідомий оператор: {op!r}")

for expr in [("10", "+", "5"), ("10", "/", "0"), ("abc", "+", "1"), ("5", "^", "2")]:
    try:
        print(f"  {expr}: {safe_calculator(*expr)}")
    except (ZeroDivisionError, ValueError) as e:
        print(f"  {expr}: ❌ {e}")

# ── Завдання 2 — Ієрархія виключень ──────────────────────────────────────────
class AppError(Exception):
    def __init__(self, message: str, code: int = 0) -> None:
        super().__init__(message)
        self.code = code

class ValidationError(AppError): pass
class NotFoundError(AppError): pass
class AuthError(AppError): pass

def get_user(user_id: int) -> dict:
    users = {1: {"name": "Аліса"}, 2: {"name": "Боб"}}
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValidationError(f"Некоректний ID: {user_id}", code=400)
    if user_id not in users:
        raise NotFoundError(f"Користувача #{user_id} не знайдено", code=404)
    return users[user_id]

for uid in [1, 99, -1, "x"]:
    try:
        user = get_user(uid)
        print(f"\n  ✓ #{uid}: {user['name']}")
    except AppError as e:
        print(f"  ✗ #{uid}: [{e.code}] {e}")

# ── Завдання 3 — retry декоратор ─────────────────────────────────────────────
def retry(times: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Повторює виклик функції times разів при виникненні exceptions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    print(f"  [retry] спроба {attempt}/{times} failed: {e}")
                    if attempt < times:
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator

call_count = 0

@retry(times=3, delay=0, exceptions=(ValueError,))
def flaky_function() -> str:
    global call_count
    call_count += 1
    if call_count < 3:
        raise ValueError("Ще не готово")
    return "Успіх!"

print(f"\nflaky_function: {flaky_function()}")

# ── Завдання 4 — Timer контекст-менеджер ─────────────────────────────────────
class Timer:
    """Вимірює час виконання блоку коду."""
    def __init__(self, name: str = "block") -> None:
        self.name = name
        self.elapsed: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *exc_info) -> bool:
        self.elapsed = time.perf_counter() - self._start
        print(f"  [{self.name}] {self.elapsed:.4f}с")
        return False

@contextmanager
def timer(name: str = "block"):
    """Контекст-менеджер через генератор."""
    t0 = time.perf_counter()
    yield
    elapsed = time.perf_counter() - t0
    print(f"  [{name}] {elapsed:.4f}с")

with Timer("list comp") as t:
    total = sum(i**2 for i in range(100_000))
print(f"  result={total}, elapsed={t.elapsed:.4f}с")

with timer("timer()"):
    total2 = sum(i**2 for i in range(100_000))

# ── Завдання 5 (Challenge) — Валідатор форми з ExceptionGroup ─────────────────
def validate_user_form(data: dict) -> None:
    """Перевіряє форму і збирає ВСІ помилки в ExceptionGroup."""
    errors: list[Exception] = []

    if len(data.get("name", "")) < 2:
        errors.append(ValidationError("Ім'я занадто коротке", code=400))
    if "@" not in data.get("email", ""):
        errors.append(ValidationError("Некоректний email", code=400))
    pw = data.get("password", "")
    if len(pw) < 8:
        errors.append(ValidationError("Пароль коротший за 8 символів", code=400))
    if pw.isalpha():
        errors.append(ValidationError("Пароль не містить цифр", code=400))

    if errors:
        raise ExceptionGroup("Помилки валідації форми", errors)

bad_data = {"name": "A", "email": "no-at", "password": "short"}
try:
    validate_user_form(bad_data)
except ExceptionGroup as eg:
    print(f"\nОтримано {len(eg.exceptions)} помилки:")
    for exc in eg.exceptions:
        print(f"  [код {exc.code}] {exc}")
