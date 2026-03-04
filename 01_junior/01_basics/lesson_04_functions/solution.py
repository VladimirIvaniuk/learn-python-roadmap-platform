"""
Розв'язки — Урок 4: Функції
"""
from functools import wraps

# ── Завдання 1 — Базові функції ───────────────────────────────────────────────
def square(n: int) -> int:
    """Повертає квадрат числа n."""
    return n ** 2

def is_even(n: int) -> bool:
    """Перевіряє чи число парне."""
    return n % 2 == 0

def max_of_two(a, b):
    """Повертає більше з двох чисел без вбудованого max."""
    return a if a >= b else b

print(square(7))          # 49
print(is_even(4))         # True
print(max_of_two(3, 10))  # 10

# ── Завдання 2 — greet з повторенням ─────────────────────────────────────────
def greet(name: str, greeting: str = "Привіт", times: int = 1) -> str:
    """Повертає рядок привітання times разів."""
    return (" ".join(f"{greeting}, {name}!") if times == 1
            else " ".join([f"{greeting}, {name}!"] * times))

# Більш елегантно:
def greet(name: str, greeting: str = "Привіт", times: int = 1) -> str:
    unit = f"{greeting}, {name}!"
    return " ".join([unit] * times)

print(greet("Іван"))            # Привіт, Іван!
print(greet("Іван", times=3))   # Привіт, Іван! Привіт, Іван! Привіт, Іван!

# ── Завдання 3 — stats() ─────────────────────────────────────────────────────
def stats(*numbers: float) -> dict:
    """Повертає статистику по довільному набору чисел."""
    if not numbers:
        return {}
    return {
        "count": len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "sum": sum(numbers),
        "avg": round(sum(numbers) / len(numbers), 4),
    }

print(stats(3, 7, 2, 9, 1))

# ── Завдання 4 — Замикання (closure) ─────────────────────────────────────────
def make_multiplier(factor: int):
    """Повертає функцію що множить аргумент на factor."""
    def multiplier(x: int | float) -> int | float:
        return x * factor
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)
power_of_10 = make_multiplier(10)

print(double(5))       # 10
print(triple(5))       # 15
print(power_of_10(7))  # 70

# ── Завдання 5 (Challenge) — Декоратор логування ─────────────────────────────
def log_call(func):
    """Логує виклик і результат функції."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = ", ".join(map(repr, args))
        kwargs_repr = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        all_args = ", ".join(filter(None, [args_repr, kwargs_repr]))
        print(f"→ Виклик: {func.__name__}({all_args})")
        result = func(*args, **kwargs)
        print(f"← Результат: {result!r}")
        return result
    return wrapper

@log_call
def add(a: int, b: int) -> int:
    """Додає два числа."""
    return a + b

@log_call
def greet_user(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

add(3, 4)
greet_user("Аліса", greeting="Привіт")
print(f"Ім'я функції: {add.__name__}")  # add (не wrapper)
print(f"Документація: {add.__doc__}")
