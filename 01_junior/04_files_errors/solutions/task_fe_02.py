"""
Рішення — Урок 2 (Винятки)

Дивись після того, як спробував сам!
"""


# Завдання 1
def task1():
    try:
        divisor = int(input("Введіть число для ділення 100: "))
        result = 100 / divisor
        print(f"Результат: {result}")
    except ZeroDivisionError:
        print("Ділення на нуль неможливе")
    except ValueError:
        print("Введіть число")


# Завдання 2
def safe_divide(a: float, b: float) -> float | None:
    if b == 0:
        return None
    return a / b


# Завдання 3
class NegativeNumberError(Exception):
    pass


def sqrt_positive(n: float) -> float:
    if n < 0:
        raise NegativeNumberError("Число не може бути від'ємним")
    return n**0.5


# Перевірка
task1()

print(safe_divide(10, 2))   # 5.0
print(safe_divide(10, 0))   # None

try:
    print(sqrt_positive(9))
except NegativeNumberError as e:
    print(e)

try:
    sqrt_positive(-4)
except NegativeNumberError as e:
    print("Помилка:", e)
