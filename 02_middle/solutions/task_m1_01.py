"""
Рішення — Урок 1 (OOP advanced)

Дивись після того, як спробував сам!
"""
import math
from functools import wraps


# Завдання 1
class Fraction:
    def __init__(self, numerator: int, denominator: int) -> None:
        self.numerator = numerator
        self.denominator = denominator

    def __str__(self) -> str:
        return f"{self.numerator}/{self.denominator}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fraction):
            return False
        return self.numerator * other.denominator == other.numerator * self.denominator


# Завдання 2
def count_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.call_count = getattr(wrapper, "call_count", 0) + 1
        result = func(*args, **kwargs)
        if wrapper.call_count == 3:
            print("Функцію викликано 3 рази")
        return result
    return wrapper


@count_calls
def demo():
    pass


# Завдання 3
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError("Радіус не може бути від'ємним")
        self._radius = value

    @property
    def area(self) -> float:
        return math.pi * self._radius**2


# Перевірка
print(Fraction(1, 2) == Fraction(2, 4))
demo()
demo()
demo()
c = Circle(5)
print(c.area)
