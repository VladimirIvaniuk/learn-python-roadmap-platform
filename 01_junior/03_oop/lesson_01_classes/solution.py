"""
Розв'язки — Урок 1: Класи та об'єкти
"""
from datetime import date

# ── Завдання 1 — Book ─────────────────────────────────────────────────────────
class Book:
    def __init__(self, title: str, author: str, pages: int, year: int) -> None:
        self.title = title
        self.author = author
        self.pages = pages
        self.year = year

    def is_classic(self) -> bool:
        return self.year < 1970

    def __str__(self) -> str:
        return f"'{self.title}' — {self.author} ({self.year})"

    def __repr__(self) -> str:
        return f"Book(title={self.title!r}, author={self.author!r}, pages={self.pages}, year={self.year})"

b = Book("Кобзар", "Тарас Шевченко", 312, 1840)
print(str(b))
print(repr(b))
print(f"Класика: {b.is_classic()}")

# ── Завдання 2 — Rectangle ────────────────────────────────────────────────────
class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        if not Rectangle.is_valid(width, height):
            raise ValueError("Width and height must be > 0")
        self.width = width
        self.height = height

    @classmethod
    def square(cls, side: float) -> "Rectangle":
        return cls(side, side)

    @staticmethod
    def is_valid(width: float, height: float) -> bool:
        return width > 0 and height > 0

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rectangle):
            return NotImplemented
        return self.area() == other.area()

    def __lt__(self, other: "Rectangle") -> bool:
        if not isinstance(other, Rectangle):
            return NotImplemented
        return self.area() < other.area()

    def __repr__(self) -> str:
        return f"Rectangle({self.width}×{self.height})"

r1 = Rectangle(4, 6)
r2 = Rectangle(3, 8)
sq = Rectangle.square(5)

print(f"\n{r1}: area={r1.area()}, perimeter={r1.perimeter()}")
print(f"{r2}: area={r2.area()}")
print(f"{sq}: area={sq.area()}")
print(f"r1 == r2: {r1 == r2}")
print(f"r1 < r2: {r1 < r2}")
print(f"sorted: {sorted([r1, r2, sq])}")

# ── Завдання 3 — BankAccount ──────────────────────────────────────────────────
class BankAccount:
    def __init__(self, owner: str, balance: float = 0) -> None:
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

    @property
    def transactions(self) -> list[tuple[str, float]]:
        return list(self._transactions)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Сума поповнення має бути > 0")
        self._balance += amount
        self._transactions.append(("deposit", amount))

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Сума зняття має бути > 0")
        if amount > self._balance:
            raise ValueError(f"Недостатньо коштів: {self._balance:.2f}")
        self._balance -= amount
        self._transactions.append(("withdraw", amount))

    def __str__(self) -> str:
        return f"Рахунок {self.owner}: {self._balance:.2f} грн"

acc = BankAccount("Аліса", 1000)
acc.deposit(500)
acc.withdraw(200)
print(f"\n{acc}")
print(f"Транзакції: {acc.transactions}")

# ── Завдання 5 (Challenge) — Queue ───────────────────────────────────────────
class Queue:
    def __init__(self) -> None:
        self._items: list = []

    def enqueue(self, item) -> None:
        self._items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise ValueError("Queue is empty")
        return self._items.pop(0)

    def peek(self):
        if self.is_empty():
            raise ValueError("Queue is empty")
        return self._items[0]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, item) -> bool:
        return item in self._items

    def __repr__(self) -> str:
        return f"Queue({self._items})"

q: Queue = Queue()
q.enqueue(1)
q.enqueue(2)
q.enqueue(3)
print(f"\n{q}, len={len(q)}")
print(f"dequeue: {q.dequeue()}")
print(f"peek: {q.peek()}")
print(f"2 in q: {2 in q}")
