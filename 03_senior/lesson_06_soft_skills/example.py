"""
Senior 6 — Soft Skills: Code Review Simulator & PR Template

Цей файл містить приклади коду для code review практики.
"""


# ══════════════════════════════════════════════════════════════════════════════
# ЧАСТИНА 1: Код для code review (знайди проблеми!)
# ══════════════════════════════════════════════════════════════════════════════

# --- v1: Оригінальний (з проблемами) ---
class UserManager:
    def __init__(self):
        self.data = []
        self.db = None

    def doLogin(self, e, p):  # camelCase, незрозумілі імена
        for u in self.data:
            if u['email'] == e and u['p'] == p:  # 'p' замість 'password'
                return True
        return False  # немає жодного логування, немає обробки None

    def getAllUsersData(self):  # повертає все, немає пагінації
        return self.data

    def checkIfUserExists(self, email):  # занадто довга назва
        for u in self.data:
            if u['email'] == email:
                return True
        return False


# --- v2: Після code review і рефакторингу ---
from dataclasses import dataclass, field
from typing import Iterator
import logging
import hashlib
import hmac

logger = logging.getLogger(__name__)


@dataclass
class User:
    id: int
    email: str
    username: str
    _password_hash: str = field(repr=False)
    is_active: bool = True

    def verify_password(self, plain: str) -> bool:
        return hmac.compare_digest(
            hashlib.sha256(plain.encode()).hexdigest(),
            self._password_hash
        )


class UserRepository:
    def __init__(self) -> None:
        self._store: dict[int, User] = {}
        self._next_id = 1

    def find_by_email(self, email: str) -> User | None:
        return next((u for u in self._store.values() if u.email == email), None)

    def exists(self, email: str) -> bool:
        return self.find_by_email(email) is not None

    def save(self, user: User) -> User:
        if user.id == 0:
            user.id = self._next_id
            self._next_id += 1
        self._store[user.id] = user
        return user

    def list(self, *, page: int = 1, per_page: int = 20) -> list[User]:
        items = list(self._store.values())
        start = (page - 1) * per_page
        return items[start:start + per_page]


class AuthService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def login(self, email: str, password: str) -> User:
        user = self._repo.find_by_email(email)
        if not user:
            logger.warning("Login attempt for unknown email: %s", email)
            raise ValueError("Invalid credentials")
        if not user.verify_password(password):
            logger.warning("Failed login for user: %s", email)
            raise ValueError("Invalid credentials")
        if not user.is_active:
            raise ValueError("Account is deactivated")
        logger.info("Successful login: %s", email)
        return user


# Demo
repo = UserRepository()
auth = AuthService(repo)

# Додаємо тестового юзера
test_user = User(
    id=0,
    email="alice@example.com",
    username="alice",
    _password_hash=hashlib.sha256(b"pass1234").hexdigest(),
)
repo.save(test_user)

print("=== Code Review: Before → After ===")
print("\nДо рефакторингу:")
print("  - camelCase назви (порушення PEP 8)")
print("  - незрозумілі параметри: e, p")
print("  - немає типів")
print("  - немає логування")
print("  - повертає всі дані без пагінації")

print("\nПісля рефакторингу:")
try:
    user = auth.login("alice@example.com", "pass1234")
    print(f"  ✅ Login success: {user.email}")
    user2 = auth.login("alice@example.com", "wrong_pass")
except ValueError as e:
    print(f"  ❌ Expected error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# ЧАСТИНА 2: PR Template та ADR
# ══════════════════════════════════════════════════════════════════════════════

PR_TEMPLATE = """
## Опис PR

### Що змінено
- [описати зміни bullet-points]

### Чому / Посилання на issue
Closes #___

### Тип змін
- [ ] Bugfix
- [ ] New feature
- [ ] Refactoring
- [ ] Docs

### Як тестував
- [ ] Unit тести
- [ ] Integration тести
- [ ] Manual testing в dev

### Checklist
- [ ] Тести написані та проходять
- [ ] mypy --strict проходить
- [ ] ruff check --fix не знаходить помилок
- [ ] Документацію оновлено (якщо потрібно)
- [ ] Немає secrets у коді
"""

ADR_TEMPLATE = """
# ADR-{number}: {title}

**Дата:** {date}
**Статус:** [Proposed | Accepted | Deprecated | Superseded]

## Контекст
[Опиши проблему або потребу що спонукала до рішення]

## Рішення
[Яке рішення обрано]

## Причини
[Чому саме це рішення]
- Перевага 1
- Перевага 2

## Альтернативи що розглядались
- **Варіант A**: [опис і чому відхилено]
- **Варіант B**: [опис і чому відхилено]

## Наслідки
### Позитивні
- ...

### Негативні / Компроміси
- ...
"""

print("\n=== PR Template ===")
print(PR_TEMPLATE[:500])

print("\n=== Interview Prep: Python Questions ===")
questions = [
    ("GIL", "Global Interpreter Lock — м'ютекс що дозволяє тільки 1 потоку виконувати Python bytecode одночасно. Обхід: multiprocessing, asyncio (I/O)"),
    ("Mutable default arg", "def f(lst=[]): lst.append(1) — список shared між всіма викликами! Завжди: def f(lst=None): if lst is None: lst = []"),
    ("__new__ vs __init__", "__new__ створює об'єкт (повертає instance), __init__ ініціалізує. __new__ використовується для Singleton, metaclass, immutable types"),
    ("Generator vs Iterator", "Generator — функція з yield, легко написати. Iterator — клас з __iter__/__next__. Generator автоматично є ітератором"),
    ("@functools.wraps", "Зберігає __name__, __doc__, __wrapped__ декорованої функції. Без нього help() і debugging показуватимуть wrapper замість оригінальної функції"),
]

for q, a in questions:
    print(f"\n  Q: {q}")
    print(f"  A: {a}")
