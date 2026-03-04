"""
Урок 4 — Приклади: функції
"""
from functools import wraps

# ── Базові функції ────────────────────────────────────────────────────────────
def square(n: int) -> int:
    """Повертає квадрат числа n."""
    return n ** 2

def greet(name: str, greeting: str = "Привіт", times: int = 1) -> str:
    """Повертає рядок привітання."""
    return (f"{greeting}, {name}! " * times).strip()

print(square(5))             # 25
print(greet("Іван"))         # Привіт, Іван!
print(greet("Іван", "Доброго ранку", 2))

# ── *args та **kwargs ─────────────────────────────────────────────────────────
def stats(*numbers: float) -> dict:
    """Повертає статистику по набору чисел."""
    if not numbers:
        return {}
    return {
        "count": len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "sum": sum(numbers),
        "avg": sum(numbers) / len(numbers),
    }

print(stats(3, 7, 2, 9, 1))
# {'count': 5, 'min': 1, 'max': 9, 'sum': 22, 'avg': 4.4}

def build_query(table: str, **conditions) -> str:
    """Будує SQL-подібний запит."""
    where = " AND ".join(f"{k}='{v}'" for k, v in conditions.items())
    return f"SELECT * FROM {table}" + (f" WHERE {where}" if where else "")

print(build_query("users"))
print(build_query("users", age=25, city="Kyiv"))

# ── Область видимості ─────────────────────────────────────────────────────────
def make_counter(start: int = 0):
    """Замикання — лічильник із станом."""
    count = start

    def increment(step: int = 1) -> int:
        nonlocal count
        count += step
        return count

    def reset() -> None:
        nonlocal count
        count = start

    return increment, reset

inc, rst = make_counter()
print(inc())     # 1
print(inc())     # 2
print(inc(5))    # 7
rst()
print(inc())     # 1 (після скидання)

# ── Lambda та sorted ─────────────────────────────────────────────────────────
students = [
    {"name": "Аліса", "grade": 92},
    {"name": "Боб",   "grade": 78},
    {"name": "Катя",  "grade": 88},
]

# Сортувати за оцінкою (спадання)
ranked = sorted(students, key=lambda s: s["grade"], reverse=True)
for i, s in enumerate(ranked, 1):
    print(f"  {i}. {s['name']}: {s['grade']}")

# ── Декоратор ────────────────────────────────────────────────────────────────
def log_call(func):
    """Декоратор: логує виклик і результат функції."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_str = ", ".join(map(str, args))
        print(f"→ Виклик: {func.__name__}({args_str})")
        result = func(*args, **kwargs)
        print(f"← Результат: {result}")
        return result
    return wrapper

@log_call
def add(a: int, b: int) -> int:
    """Додає два числа."""
    return a + b

add(3, 4)
# → Виклик: add(3, 4)
# ← Результат: 7
print(f"Назва функції після @wraps: {add.__name__}")   # add (не wrapper)
