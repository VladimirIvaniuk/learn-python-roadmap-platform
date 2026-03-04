"""
Урок 1 — Приклади: класи та об'єкти
"""
import math
from datetime import date


class BankAccount:
    """Банківський рахунок із журналом транзакцій."""

    bank_name = "MyBank"   # атрибут класу

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner
        self._balance = balance
        self._transactions: list[tuple[str, float]] = []

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            raise ValueError("Баланс не може бути від'ємним")
        self._balance = value

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError(f"Сума поповнення має бути > 0, отримано {amount}")
        self._balance += amount
        self._transactions.append(("deposit", amount))

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError(f"Сума зняття має бути > 0, отримано {amount}")
        if amount > self._balance:
            raise ValueError(f"Недостатньо коштів: {self._balance:.2f}")
        self._balance -= amount
        self._transactions.append(("withdraw", amount))

    def statement(self) -> str:
        lines = [f"Виписка: {self.owner} ({self.bank_name})"]
        for op, amt in self._transactions:
            sign = "+" if op == "deposit" else "-"
            lines.append(f"  {sign}{amt:.2f}")
        lines.append(f"  Баланс: {self._balance:.2f}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return f"Рахунок {self.owner}: {self._balance:.2f} грн"

    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self._balance})"


acc = BankAccount("Аліса", 1000)
acc.deposit(500)
acc.withdraw(200)
print(acc)
print(acc.statement())


class Point:
    """Точка на площині з магічними методами."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    @property
    def distance_to_origin(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @classmethod
    def origin(cls) -> "Point":
        return cls(0, 0)

    @staticmethod
    def distance(p1: "Point", p2: "Point") -> float:
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __lt__(self, other: "Point") -> bool:
        return self.distance_to_origin < other.distance_to_origin

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Point(x={self.x}, y={self.y})"


p1, p2 = Point(3, 4), Point(1, 1)
print(f"\np1={p1}, |p1|={p1.distance_to_origin:.2f}")
print(f"p1 + p2 = {p1 + p2}")
print(f"p1 < p2: {p1 < p2}")
print(f"Відстань: {Point.distance(p1, p2):.2f}")

points = [Point(3, 4), Point(1, 1), Point(5, 0), Point(0, 2)]
print(f"Sorted: {sorted(points)}")


class Temperature:
    """Температура з конвертацією."""

    def __init__(self, celsius: float = 0.0) -> None:
        self.celsius = celsius   # через setter!

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError(f"Нижче абсолютного нуля: {value}")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, f: float) -> None:
        self.celsius = (f - 32) * 5 / 9

    @property
    def kelvin(self) -> float:
        return self._celsius + 273.15

    def __repr__(self) -> str:
        return f"{self._celsius:.1f}°C / {self.fahrenheit:.1f}°F / {self.kelvin:.1f}K"


t = Temperature(100)
print(f"\nВода кипить: {t}")
t.fahrenheit = 32
print(f"Вода замерзає: {t}")
