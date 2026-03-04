"""
Розв'язки — Code Quality (Senior)
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeVar, Generic, Protocol, runtime_checkable

# ── Завдання 1 — Виправлення mypy помилок ────────────────────────────────────

# Проблемний код (для демонстрації):
# def process(items):
#     result = []
#     for item in items:
#         if item > 0:
#             result.append(item * 2)
#     return result

# Виправлений:
def process(items: list[int]) -> list[int]:
    """Повертає подвоєні позитивні елементи."""
    return [item * 2 for item in items if item > 0]

# Типобезпечний стек
T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

stack: Stack[int] = Stack()
stack.push(1)
stack.push(2)
print(f"Stack peek={stack.peek()}, pop={stack.pop()}, len={len(stack)}")

# ── Завдання 4 — Рефакторинг складної функції ────────────────────────────────
class OrderStatus(Enum):
    PENDING  = auto()
    PAID     = auto()
    SHIPPED  = auto()
    REFUNDED = auto()
    INVALID  = auto()

@dataclass
class Order:
    id: int
    status: OrderStatus
    amount: float
    user_id: int
    items: list[dict]

class OrderProcessingError(Exception):
    pass

# ─ До рефакторингу (висока цикломатична складність = 12):
def process_order_bad(order, user, payment, inventory):
    if order is None:
        return None
    if order["status"] == "pending":
        if user is not None and user.get("active"):
            if payment is not None:
                if payment.get("amount") >= order.get("total", 0):
                    if inventory is not None:
                        for item in order.get("items", []):
                            if inventory.get(item["id"], 0) < item.get("qty", 0):
                                return {"success": False, "error": "Out of stock"}
                        return {"success": True}
                    else:
                        return {"success": False, "error": "No inventory"}
                else:
                    return {"success": False, "error": "Insufficient payment"}
            else:
                return {"success": False, "error": "No payment"}
        else:
            return {"success": False, "error": "User not active"}
    else:
        return {"success": False, "error": "Order not pending"}

# ─ Після рефакторингу (складність = 2, Guard Clauses):
def _validate_order(order: dict) -> None:
    if order.get("status") != "pending":
        raise OrderProcessingError("Order not pending")

def _validate_user(user: dict | None) -> None:
    if user is None or not user.get("active"):
        raise OrderProcessingError("User not active")

def _validate_payment(payment: dict | None, total: float) -> None:
    if payment is None:
        raise OrderProcessingError("No payment")
    if payment.get("amount", 0) < total:
        raise OrderProcessingError("Insufficient payment")

def _validate_inventory(inventory: dict | None, items: list[dict]) -> None:
    if inventory is None:
        raise OrderProcessingError("No inventory")
    for item in items:
        if inventory.get(item["id"], 0) < item.get("qty", 0):
            raise OrderProcessingError(f"Out of stock: {item['id']}")

def process_order(order: dict, user: dict | None, payment: dict | None, inventory: dict | None) -> dict:
    """Обробляє замовлення — Guard Clauses замість вкладених if."""
    try:
        _validate_order(order)
        _validate_user(user)
        _validate_payment(payment, order.get("total", 0))
        _validate_inventory(inventory, order.get("items", []))
        return {"success": True}
    except OrderProcessingError as e:
        return {"success": False, "error": str(e)}

# Тест
order = {"status": "pending", "total": 100, "items": [{"id": "item1", "qty": 2}]}
user = {"active": True}
payment = {"amount": 100}
inventory = {"item1": 5}

print(process_order(order, user, payment, inventory))
print(process_order(order, None, payment, inventory))

# ── Завдання 5 (Challenge) — Code Review ─────────────────────────────────────
# Проблемний код (для code review):

# class UserManager:
#     users = []               # 1. mutable class attr
#     def addUser(self, n, e): # 2. camelCase
#         u = {"name": n, "email": e}
#         self.users.append(u) # 3. немає валідації
#         return u
#
# def getAdmins(users):        # 4. не типовано
#     result = []
#     for u in users:
#         if u.get("role") == "admin":
#             result.append(u)
#     return result

# Рефакторинг:
@dataclass
class AppUser:
    name: str
    email: str
    role: str = "user"

    def __post_init__(self):
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email!r}")
        if not self.name.strip():
            raise ValueError("Name cannot be empty")

class UserManager:
    def __init__(self) -> None:
        self._users: list[AppUser] = []

    def add_user(self, name: str, email: str, role: str = "user") -> AppUser:
        if any(u.email == email for u in self._users):
            raise ValueError(f"Email already exists: {email}")
        user = AppUser(name=name, email=email, role=role)
        self._users.append(user)
        return user

    def get_admins(self) -> list[AppUser]:
        return [u for u in self._users if u.role == "admin"]

    def __len__(self) -> int:
        return len(self._users)

mgr = UserManager()
mgr.add_user("Аліса", "alice@example.com", "admin")
mgr.add_user("Боб", "bob@example.com")
print(f"\nAdmins: {mgr.get_admins()}")
print(f"Total users: {len(mgr)}")
