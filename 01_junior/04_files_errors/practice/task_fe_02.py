"""
Практика — Урок 2 (Винятки)
Див. lesson_02_exceptions/task.md

Заповни TODO. Потім порівняй з solutions/task_fe_02.py
"""


def safe_divide(a: float, b: float) -> float | None:
    """Повертає a/b або None при b=0."""
    # TODO
    return None


class NegativeNumberError(Exception):
    """Виняток для від'ємних чисел."""
    pass


def sqrt_positive(n: float) -> float:
    """Повертає n**0.5. Якщо n < 0 — raise NegativeNumberError."""
    # TODO
    return 0.0


# Завдання 1 — ділення 100 на input, оброби 0 та ValueError
# TODO: try/except
