"""
Розв'язки — Architecture (Senior)
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable
import hashlib, uuid

# ─────────────── Сутності (Entities) ─────────────────────────────────────────
@dataclass
class User:
    name: str
    email: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hashed_password: str = ""
    is_active: bool = True

    def __post_init__(self):
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")

# ─────────────── Інтерфейси (Ports) ──────────────────────────────────────────
@runtime_checkable
class UserRepository(Protocol):
    def find_by_id(self, user_id: str) -> User | None: ...
    def find_by_email(self, email: str) -> User | None: ...
    def save(self, user: User) -> None: ...
    def delete(self, user_id: str) -> None: ...

@runtime_checkable
class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, hashed: str) -> bool: ...

@runtime_checkable
class EmailNotifier(Protocol):
    def send_welcome(self, user: User) -> None: ...

# ─────────────── Адаптери (конкретні реалізації) ──────────────────────────────
class InMemoryUserRepository:
    def __init__(self):
        self._store: dict[str, User] = {}

    def find_by_id(self, user_id: str) -> User | None:
        return self._store.get(user_id)

    def find_by_email(self, email: str) -> User | None:
        return next((u for u in self._store.values() if u.email == email), None)

    def save(self, user: User) -> None:
        self._store[user.id] = user

    def delete(self, user_id: str) -> None:
        self._store.pop(user_id, None)

    def all(self) -> list[User]:
        return list(self._store.values())

class Sha256PasswordHasher:
    def hash(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify(self, password: str, hashed: str) -> bool:
        return self.hash(password) == hashed

class ConsoleEmailNotifier:
    def send_welcome(self, user: User) -> None:
        print(f"[Email] → {user.email}: Ласкаво просимо, {user.name}!")

# ─────────────── Use Case (Application Service) ───────────────────────────────
class UserService:
    """Orchestrates business logic; depends only on abstractions."""
    def __init__(
        self,
        repo: UserRepository,
        hasher: PasswordHasher,
        notifier: EmailNotifier,
    ) -> None:
        self._repo = repo
        self._hasher = hasher
        self._notifier = notifier

    def register(self, name: str, email: str, password: str) -> User:
        if self._repo.find_by_email(email):
            raise ValueError(f"Email already registered: {email}")
        user = User(name=name, email=email)
        user.hashed_password = self._hasher.hash(password)
        self._repo.save(user)
        self._notifier.send_welcome(user)
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self._repo.find_by_email(email)
        if not user:
            raise ValueError("User not found")
        if not self._hasher.verify(password, user.hashed_password):
            raise ValueError("Incorrect password")
        return user

    def deactivate(self, user_id: str) -> None:
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        user.is_active = False
        self._repo.save(user)

# ─────────────── DI Container ─────────────────────────────────────────────────
class Container:
    def __init__(self) -> None:
        self._repo     = InMemoryUserRepository()
        self._hasher   = Sha256PasswordHasher()
        self._notifier = ConsoleEmailNotifier()

    @property
    def user_service(self) -> UserService:
        return UserService(self._repo, self._hasher, self._notifier)

# ─────────────── Завдання 2 — Кілька backends ─────────────────────────────────
class JsonFileRepository:
    """Persistence via JSON file — same interface as InMemoryUserRepository."""
    def __init__(self, path: str = "/tmp/users.json"):
        import json, pathlib
        self._path = pathlib.Path(path)
        if not self._path.exists():
            self._path.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        import json
        return json.loads(self._path.read_text(encoding="utf-8"))

    def _dump(self, data: list[dict]) -> None:
        import json
        self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def save(self, user: User) -> None:
        data = [u for u in self._load() if u["id"] != user.id]
        data.append({"id": user.id, "name": user.name, "email": user.email})
        self._dump(data)

    def find_by_id(self, user_id: str) -> User | None:
        row = next((u for u in self._load() if u["id"] == user_id), None)
        return User(**row) if row else None

    def find_by_email(self, email: str) -> User | None:
        row = next((u for u in self._load() if u["email"] == email), None)
        return User(**row) if row else None

    def delete(self, user_id: str) -> None:
        self._dump([u for u in self._load() if u["id"] != user_id])

# ─────────────── Завдання 3 — Strategy Pattern ────────────────────────────────
@runtime_checkable
class DiscountStrategy(Protocol):
    def apply(self, price: float) -> float: ...

class NoDiscount:
    def apply(self, price: float) -> float:
        return price

class PercentDiscount:
    def __init__(self, percent: float) -> None:
        self.percent = percent
    def apply(self, price: float) -> float:
        return price * (1 - self.percent / 100)

class BulkDiscount:
    def __init__(self, min_qty: int, percent: float) -> None:
        self.min_qty = min_qty
        self.percent = percent
    def apply_to_order(self, price: float, qty: int) -> float:
        if qty >= self.min_qty:
            return price * qty * (1 - self.percent / 100)
        return price * qty

# ─────────────── Демонстрація ─────────────────────────────────────────────────
if __name__ == "__main__":
    container = Container()
    svc = container.user_service

    alice = svc.register("Аліса", "alice@example.com", "Secret123!")
    print(f"\nЗареєстровано: {alice.name}")

    auth_user = svc.authenticate("alice@example.com", "Secret123!")
    print(f"Аутентифіковано: {auth_user.name}")

    svc.deactivate(alice.id)
    print(f"Активний: {container._repo.find_by_id(alice.id).is_active}")

    discounts: list[DiscountStrategy] = [
        NoDiscount(), PercentDiscount(10), PercentDiscount(25),
    ]
    for d in discounts:
        print(f"{type(d).__name__}: 100.0 → {d.apply(100.0):.2f}")
