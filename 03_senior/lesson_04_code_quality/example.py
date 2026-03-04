"""
Senior 4 — Приклади: якість коду, типізація, рефакторинг

Запуск: python example.py
mypy:   mypy example.py --strict
ruff:   ruff check example.py
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, TypeVar, Generic

T = TypeVar("T")


# ── Правильна типізація ────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Email:
    """Value Object — email з валідацією."""
    value: str

    def __post_init__(self) -> None:
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", self.value):
            raise ValueError(f"Invalid email: {self.value!r}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Password:
    """Value Object — пароль з вимогами."""
    raw: str

    def __post_init__(self) -> None:
        errors = []
        if len(self.raw) < 8:
            errors.append("Мінімум 8 символів")
        if not any(c.isupper() for c in self.raw):
            errors.append("Хоч одна велика літера")
        if not any(c.isdigit() for c in self.raw):
            errors.append("Хоч одна цифра")
        if errors:
            raise ValueError(f"Невалідний пароль: {'; '.join(errors)}")


# Generic Stack з типами
class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def peek(self) -> T | None:
        return self._items[-1] if self._items else None

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)


s: Stack[int] = Stack()
s.push(1)
s.push(2)
s.push(3)
print(f"Stack: peek={s.peek()}, pop={s.pop()}, len={len(s)}")


# ── Рефакторинг: CC → Guard Clauses ──────────────────────────────────────────
# ❌ До рефакторингу: глибоке вкладення (CC = 7)
def process_order_bad(order: dict) -> float | None:
    if order:
        if order.get("status") == "active":
            if order.get("items"):
                total = 0.0
                for item in order["items"]:
                    if item.get("price"):
                        if item.get("quantity"):
                            total += item["price"] * item["quantity"]
                return total
    return None

# ✅ Після рефакторингу: Guard Clauses (CC = 3)
def calculate_item_total(item: dict) -> float:
    price = item.get("price", 0.0)
    quantity = item.get("quantity", 0)
    return price * quantity

def process_order(order: dict) -> float | None:
    if not order:
        return None
    if order.get("status") != "active":
        return None
    items = order.get("items")
    if not items:
        return None
    return sum(calculate_item_total(item) for item in items)


order = {"status": "active", "items": [{"price": 10.0, "quantity": 3}, {"price": 25.0, "quantity": 1}]}
print(f"\nOrder total: {process_order(order)}")


# ── Proper Exception Hierarchy ────────────────────────────────────────────────
class AppError(Exception):
    def __init__(self, message: str, code: str = "APP_ERROR") -> None:
        super().__init__(message)
        self.code = code

class ValidationError(AppError):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"[{field}] {message}", "VALIDATION_ERROR")
        self.field = field

class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: int | str) -> None:
        super().__init__(f"{resource} id={resource_id} not found", "NOT_FOUND")


# ── Typed Protocol ────────────────────────────────────────────────────────────
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict[str, object]: ...

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Serializable": ...


@dataclass
class UserDTO:
    id: int
    email: str
    username: str

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "email": self.email, "username": self.username}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "UserDTO":
        return cls(id=int(data["id"]), email=str(data["email"]), username=str(data["username"]))


def serialize_all(items: list[Serializable]) -> list[dict[str, object]]:
    return [item.to_dict() for item in items]

users = [UserDTO(1, "alice@example.com", "alice"), UserDTO(2, "bob@example.com", "bob")]
print(f"\nSerialized: {serialize_all(users)}")
print(f"Is Serializable: {isinstance(users[0], Serializable)}")


# ── Validate типів через декоратор ────────────────────────────────────────────
import inspect, functools

def validate_args(func: Callable) -> Callable:
    """Перевіряє типи аргументів за анотаціями."""
    hints = {
        k: v for k, v in func.__annotations__.items()
        if k != "return"
    }

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = inspect.signature(func).bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            if name in hints:
                expected = hints[name]
                # Простий Union check
                origin = getattr(expected, "__origin__", None)
                if origin is not None:
                    types = expected.__args__
                    if not isinstance(value, types):
                        raise TypeError(f"'{name}': expected {expected}, got {type(value).__name__}")
                elif not isinstance(value, expected):
                    raise TypeError(f"'{name}': expected {expected.__name__}, got {type(value).__name__}")
        return func(*args, **kwargs)
    return wrapper

@validate_args
def greet(name: str, times: int) -> str:
    return (f"Hello {name}! " * times).strip()

print(f"\n{greet('Alice', 2)}")
try:
    greet("Alice", "2")  # type: ignore
except TypeError as e:
    print(f"TypeError: {e}")
