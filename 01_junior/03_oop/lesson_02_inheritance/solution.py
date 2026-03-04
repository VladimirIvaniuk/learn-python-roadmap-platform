"""
Розв'язки — Урок 2: Успадкування
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import math

# ── Завдання 1 — Ієрархія тварин ─────────────────────────────────────────────
class Animal:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def speak(self) -> str:
        raise NotImplementedError

    def move(self) -> str:
        return f"{self.name} переміщується"

    def __str__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r}, age={self.age})"

class Dog(Animal):
    def __init__(self, name: str, age: int, breed: str) -> None:
        super().__init__(name, age)
        self.breed = breed

    def speak(self) -> str:
        return "Гав!"

    def fetch(self) -> str:
        return f"{self.name} приніс м'яч"

class Cat(Animal):
    def __init__(self, name: str, age: int, indoor: bool = True) -> None:
        super().__init__(name, age)
        self.indoor = indoor

    def speak(self) -> str:
        return "Мяу~"

    def purr(self) -> str:
        return f"{self.name}: мурмурмур..."

class Duck(Animal):
    def speak(self) -> str:
        return "Кря-кря!"

    def move(self) -> str:
        return f"{self.name} летить"

animals: list[Animal] = [
    Dog("Рекс", 3, "Вівчарка"),
    Cat("Мурка", 5),
    Duck("Дональд", 2),
]

for a in animals:
    print(f"{a}: {a.speak()}, {a.move()}")

# ── Завдання 2 — Абстрактні фігури ───────────────────────────────────────────
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def describe(self) -> str:
        return (f"{type(self).__name__}: "
                f"площа={self.area():.2f}, периметр={self.perimeter():.2f}")

class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius

class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

class Triangle(Shape):
    def __init__(self, a: float, b: float, c: float) -> None:
        self.a, self.b, self.c = a, b, c

    def area(self) -> float:
        s = self.perimeter() / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def perimeter(self) -> float:
        return self.a + self.b + self.c

shapes: list[Shape] = [Circle(5), Rectangle(4, 6), Triangle(3, 4, 5)]
for s in shapes:
    print(s.describe())

total_area = sum(s.area() for s in shapes)
print(f"Загальна площа: {total_area:.2f}")
print(f"Найбільша: {max(shapes, key=lambda s: s.area()).describe()}")

# ── Завдання 4 — Mixins ──────────────────────────────────────────────────────
import json

class SerializableMixin:
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict):
        obj = cls.__new__(cls)
        obj.__dict__.update(data)
        return obj

class LogMixin:
    def log(self, action: str, level: str = "INFO") -> None:
        print(f"[{level}] {type(self).__name__}.{action}")

@dataclass
class User(SerializableMixin, LogMixin):
    name: str
    email: str
    age: int

u = User("Іван", "ivan@example.com", 30)
print(f"\n{u.to_json()}")
u.log("created")
u2 = User.from_dict({"name": "Оля", "email": "ola@example.com", "age": 25})
print(f"from_dict: {u2}")
