"""
Рішення — Урок 4

Дивись після того, як спробував сам!
"""


def square(n: int) -> int:
    return n * n


def greet(name: str, time_of_day: str = "день") -> str:
    return f"Добрий {time_of_day}, {name}!"


def is_even(n: int) -> bool:
    return n % 2 == 0


def max_of_two(a: int, b: int) -> int:
    if a > b:
        return a
    return b


# Перевірка
print(square(5))  # 25
print(greet("Марія", "вечір"))  # Добрий вечір, Марія!
print(is_even(4))  # True
print(is_even(7))  # False
print(max_of_two(10, 20))  # 20
