"""
Урок 2 — Приклади: успадкування та поліморфізм
"""
import math
from abc import ABC, abstractmethod


# ── Базовий клас + нащадки ─────────────────────────────────────────────────────
class Animal:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def speak(self) -> str:
        return "..."

    def info(self) -> str:
        return f"{self.__class__.__name__}: {self.name}, {self.age} р."

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"


class Dog(Animal):
    def __init__(self, name: str, age: int, breed: str) -> None:
        super().__init__(name, age)
        self.breed = breed

    def speak(self) -> str:
        return "Гав!"

    def fetch(self) -> str:
        return f"{self.name} приніс м'яч!"

    def info(self) -> str:
        return f"{super().info()}, {self.breed}"


class Cat(Animal):
    def speak(self) -> str:
        return "Няв!"

    def purr(self) -> str:
        return "Муррр..."


class Duck(Animal):
    def speak(self) -> str:
        return "Кря!"


# Поліморфізм
animals: list[Animal] = [
    Dog("Рекс", 3, "Лабрадор"),
    Cat("Мурка", 5),
    Duck("Дональд", 2),
]

print("=== Зоопарк ===")
for a in animals:
    print(f"  {a.info()} → {a.speak()}")

# isinstance
for a in animals:
    if isinstance(a, Dog):
        print(a.fetch())
    elif isinstance(a, Cat):
        print(a.purr())


# ── Абстрактні класи ───────────────────────────────────────────────────────────
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def describe(self) -> str:
        return f"{self.__class__.__name__}: S={self.area():.2f}, P={self.perimeter():.2f}"


class Circle(Shape):
    def __init__(self, r: float) -> None:
        self.r = r

    def area(self) -> float:
        return math.pi * self.r ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.r


class Rectangle(Shape):
    def __init__(self, w: float, h: float) -> None:
        self.w = w
        self.h = h

    def area(self) -> float:
        return self.w * self.h

    def perimeter(self) -> float:
        return 2 * (self.w + self.h)


shapes: list[Shape] = [Circle(5), Rectangle(4, 6), Circle(3)]
print("\n=== Фігури ===")
for s in shapes:
    print(f"  {s.describe()}")

print(f"Найбільша: {max(shapes, key=lambda s: s.area()).describe()}")
print(f"Загальна площа: {sum(s.area() for s in shapes):.2f}")


# ── Mixin паттерн ──────────────────────────────────────────────────────────────
import json


class JsonMixin:
    def to_json(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> "JsonMixin":
        return cls(**json.loads(s))


class LogMixin:
    def log(self, msg: str) -> None:
        print(f"[{self.__class__.__name__}] {msg}")


class ApiUser(LogMixin, JsonMixin):
    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email

    def __repr__(self) -> str:
        return f"ApiUser({self.name!r})"


print("\n=== Mixin ===")
u = ApiUser("Аліса", "alice@example.com")
print(u.to_json())
u.log("Авторизувався")
u2 = ApiUser.from_json('{"name": "Боб", "email": "bob@example.com"}')
print(u2)
