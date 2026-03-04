"""
Senior 1 — Приклади: SOLID, Repository, DI
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, TypeVar, Protocol

# ── SOLID: SRP + DIP ──────────────────────────────────────────────────────────
@dataclass
class User:
    id: int
    email: str
    username: str
    hashed_password: str
    is_active: bool = True

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email!r})"


# Abstractions (Ports)
class UserRepository(Protocol):
    def get_by_id(self, user_id: int) -> User | None: ...
    def get_by_email(self, email: str) -> User | None: ...
    def save(self, user: User) -> User: ...
    def delete(self, user_id: int) -> bool: ...

class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, plain: str, hashed: str) -> bool: ...

class EmailNotifier(Protocol):
    def send_welcome(self, email: str) -> None: ...


# Implementations (Adapters)
class InMemoryUserRepository:
    def __init__(self) -> None:
        self._store: dict[int, User] = {}
        self._next_id = 1

    def get_by_id(self, user_id: int) -> User | None:
        return self._store.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._store.values() if u.email == email), None)

    def save(self, user: User) -> User:
        if user.id == 0:
            user.id = self._next_id
            self._next_id += 1
        self._store[user.id] = user
        return user

    def delete(self, user_id: int) -> bool:
        if user_id in self._store:
            del self._store[user_id]
            return True
        return False

    def all(self) -> list[User]:
        return list(self._store.values())


class SimpleHasher:
    """Демо хешер (реальний — bcrypt)."""
    def hash(self, password: str) -> str:
        import hashlib
        return f"hashed:{hashlib.sha256(password.encode()).hexdigest()[:16]}"

    def verify(self, plain: str, hashed: str) -> bool:
        return self.hash(plain) == hashed


class ConsoleEmailNotifier:
    def send_welcome(self, email: str) -> None:
        print(f"  📧 Welcome email → {email}")


# Application Service (Business Logic)
class UserService:
    def __init__(
        self,
        repo: UserRepository,
        hasher: PasswordHasher,
        notifier: EmailNotifier,
    ) -> None:
        self._repo = repo
        self._hasher = hasher
        self._notifier = notifier

    def register(self, email: str, password: str) -> User:
        if self._repo.get_by_email(email):
            raise ValueError(f"Email {email} вже зайнятий")
        user = User(
            id=0,
            email=email,
            username=email.split("@")[0],
            hashed_password=self._hasher.hash(password),
        )
        saved = self._repo.save(user)
        self._notifier.send_welcome(email)
        return saved

    def authenticate(self, email: str, password: str) -> User:
        user = self._repo.get_by_email(email)
        if not user or not self._hasher.verify(password, user.hashed_password):
            raise ValueError("Невірний email або пароль")
        if not user.is_active:
            raise ValueError("Аккаунт деактивовано")
        return user


# DI Container
class Container:
    def __init__(self) -> None:
        self._repo = InMemoryUserRepository()
        self._hasher = SimpleHasher()
        self._notifier = ConsoleEmailNotifier()

    @property
    def user_service(self) -> UserService:
        return UserService(self._repo, self._hasher, self._notifier)

    @property
    def user_repo(self) -> InMemoryUserRepository:
        return self._repo


# Demo
container = Container()
service = container.user_service

print("=== SOLID + Repository + DI ===")
alice = service.register("alice@example.com", "pass1234")
print(f"Зареєстровано: {alice}")

try:
    service.register("alice@example.com", "other_pass")
except ValueError as e:
    print(f"Очікувана помилка: {e}")

user = service.authenticate("alice@example.com", "pass1234")
print(f"Авторизовано: {user}")

all_users = container.user_repo.all()
print(f"Всього користувачів: {len(all_users)}")


# ── Open/Closed — Strategy ────────────────────────────────────────────────────
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, price: float) -> float: ...
    @abstractmethod
    def description(self) -> str: ...

class NoDiscount(DiscountStrategy):
    def apply(self, p: float) -> float: return p
    def description(self) -> str: return "Без знижки"

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percent: float) -> None:
        self.percent = percent
    def apply(self, p: float) -> float:
        return round(p * (1 - self.percent / 100), 2)
    def description(self) -> str:
        return f"{self.percent}% знижка"

class BulkDiscount(DiscountStrategy):
    def __init__(self, qty: int, percent: float) -> None:
        self.qty = qty
        self.percent = percent
    def apply(self, p: float) -> float:
        return round(p * (1 - self.percent / 100), 2)
    def description(self) -> str:
        return f"Гуртова {self.percent}% (від {self.qty} шт)"

strategies = [NoDiscount(), PercentageDiscount(10), BulkDiscount(10, 20)]
price = 100.0

print("\n=== Strategy Pattern ===")
for strategy in strategies:
    print(f"  {strategy.description()}: {price} → {strategy.apply(price)}")
