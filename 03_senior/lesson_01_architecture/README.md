# Урок 1 — Архітектура: SOLID, Clean Architecture, DI

## Що вивчимо
- SOLID принципи з реальними Python прикладами
- Clean Architecture / Hexagonal Architecture
- Dependency Injection (DI) — вручну та через `dependency-injector`
- Repository Pattern та Unit of Work
- Separation of Concerns — розподіл відповідальностей
- Рефакторинг: до і після

---

## Теорія

### 1. SOLID принципи

#### S — Single Responsibility Principle
*Клас/функція має лише одну причину для змін.*

```python
# ❌ Порушення SRP — UserService робить все
class UserService:
    def register(self, email, password):
        # валідація
        if "@" not in email:
            raise ValueError("Bad email")
        # хешування
        hashed = hashlib.md5(password.encode()).hexdigest()
        # запис до БД
        self.db.execute("INSERT INTO users ...")
        # відправка email
        smtp.send(to=email, subject="Welcome!")
        # логування
        logger.info(f"User registered: {email}")

# ✅ SRP — кожен клас/модуль робить одне
class EmailValidator:
    def validate(self, email: str) -> None:
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError(f"Invalid email: {email}")

class PasswordHasher:
    def hash(self, password: str) -> str:
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

class UserRepository:
    def create(self, email: str, hashed_password: str) -> User: ...

class EmailNotifier:
    def send_welcome(self, email: str) -> None: ...

class UserRegistrationService:
    def __init__(self, validator, hasher, repo, notifier):
        self._validator = validator
        self._hasher = hasher
        self._repo = repo
        self._notifier = notifier

    def register(self, email: str, password: str) -> User:
        self._validator.validate(email)
        hashed = self._hasher.hash(password)
        user = self._repo.create(email, hashed)
        self._notifier.send_welcome(email)
        return user
```

#### O — Open/Closed Principle
*Відкритий для розширення, закритий для модифікації.*

```python
# ❌ Порушення — кожна нова знижка = модифікація функції
def calculate_discount(user_type: str, price: float) -> float:
    if user_type == "premium":
        return price * 0.9
    elif user_type == "vip":
        return price * 0.7
    elif user_type == "employee":   # ← нова умова = зміна коду
        return price * 0.5
    return price

# ✅ OCP — нова стратегія = новий клас, без змін у DiscountCalculator
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, price: float) -> float: ...

class NoDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price

class PremiumDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price * 0.9

class VIPDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price * 0.7

# Нова знижка — тільки новий клас, жоден існуючий не змінюється
class EmployeeDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price * 0.5

class DiscountCalculator:
    def __init__(self, strategy: DiscountStrategy):
        self._strategy = strategy

    def calculate(self, price: float) -> float:
        return self._strategy.apply(price)
```

#### L — Liskov Substitution Principle
*Підклас повинен бути повноцінним замінником батьківського класу.*

```python
# ❌ Порушення — Square ламає контракт Rectangle
class Rectangle:
    def set_width(self, w): self.width = w
    def set_height(self, h): self.height = h
    def area(self): return self.width * self.height

class Square(Rectangle):
    def set_width(self, w):   # ← порушення — змінює обидва!
        self.width = self.height = w
    def set_height(self, h):
        self.width = self.height = h

def test_rectangle(r: Rectangle):
    r.set_width(5)
    r.set_height(10)
    assert r.area() == 50   # провалиться для Square!

# ✅ LSP — Square не успадковує від Rectangle
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Rectangle(Shape):
    def __init__(self, w, h): self.w, self.h = w, h
    def area(self): return self.w * self.h

class Square(Shape):
    def __init__(self, side): self.side = side
    def area(self): return self.side ** 2
```

#### I — Interface Segregation Principle
*Клієнт не повинен залежати від методів, які не використовує.*

```python
# ❌ Порушення — один великий інтерфейс
class Animal(ABC):
    @abstractmethod
    def fly(self): ...
    @abstractmethod
    def swim(self): ...
    @abstractmethod
    def run(self): ...

class Dog(Animal):
    def run(self): return "Run!"
    def swim(self): return "Swim!"
    def fly(self): raise NotImplementedError("Dogs can't fly!")  # ← порушення

# ✅ ISP — маленькі спеціалізовані інтерфейси
class Runnable(Protocol):
    def run(self) -> str: ...

class Swimmable(Protocol):
    def swim(self) -> str: ...

class Flyable(Protocol):
    def fly(self) -> str: ...

class Dog:
    def run(self) -> str: return "Run!"
    def swim(self) -> str: return "Swim!"
```

#### D — Dependency Inversion Principle
*Залежи від абстракцій, а не від конкретних реалізацій.*

```python
# ❌ Порушення — UserService жорстко залежить від MySQL
class UserService:
    def __init__(self):
        self.db = MySQLDatabase("localhost", "mydb")  # конкретна реалізація!

    def get_user(self, id): return self.db.query(...)

# ✅ DIP — залежимо від інтерфейсу
class UserRepository(Protocol):
    def get_by_id(self, id: int) -> User | None: ...
    def save(self, user: User) -> User: ...

class UserService:
    def __init__(self, repo: UserRepository):  # ← інтерфейс
        self._repo = repo

    def get_user(self, id: int) -> User | None:
        return self._repo.get_by_id(id)

# Можна підставити будь-яку реалізацію
service = UserService(MySQLUserRepository(conn))
service = UserService(PostgreSQLUserRepository(conn))
service = UserService(InMemoryUserRepository())   # для тестів!
```

---

### 2. Clean Architecture

```
┌─────────────────────────────────────────┐
│           Frameworks & Drivers          │ ← FastAPI, SQLAlchemy, Redis
├─────────────────────────────────────────┤
│         Interface Adapters             │ ← Routers, Repositories
├─────────────────────────────────────────┤
│           Use Cases (Services)          │ ← Бізнес-логіка
├─────────────────────────────────────────┤
│           Entities (Domain)             │ ← Моделі, правила
└─────────────────────────────────────────┘
     Залежності тільки ВСЕРЕДИНУ ↑
```

```python
# domain/entities.py — нічого не імпортує з зовнішнього
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    email: str
    username: str
    is_active: bool = True
    created_at: datetime = None

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

# application/ports.py — інтерфейси (абстракції)
from abc import ABC, abstractmethod

class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...

# application/services.py — бізнес-логіка
class UserService:
    def __init__(self, repo: UserRepositoryPort, hasher, notifier):
        self._repo = repo
        self._hasher = hasher
        self._notifier = notifier

    async def register(self, email: str, password: str) -> User:
        if await self._repo.get_by_email(email):
            raise ValueError(f"Email {email} вже зайнятий")

        user = User(id=0, email=email, username=email.split("@")[0])
        saved_user = await self._repo.save(user)
        await self._notifier.send_welcome(email)
        return saved_user

# infrastructure/adapters.py — конкретні реалізації
class SQLAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, session): self._session = session

    async def get_by_id(self, id: int) -> User | None:
        row = await self._session.get(UserModel, id)
        return self._to_domain(row) if row else None

    async def save(self, user: User) -> User: ...

    def _to_domain(self, model: UserModel) -> User:
        return User(id=model.id, email=model.email, ...)
```

---

### 3. Dependency Injection Container

```python
# Вручну (простий підхід)
class Container:
    def __init__(self, db_session):
        self._db = db_session

    @property
    def user_repo(self) -> UserRepositoryPort:
        return SQLAlchemyUserRepository(self._db)

    @property
    def user_service(self) -> UserService:
        return UserService(
            repo=self.user_repo,
            hasher=BcryptHasher(),
            notifier=SmtpNotifier(),
        )

# FastAPI integration
async def get_container(db: AsyncSession = Depends(get_db)) -> Container:
    return Container(db)

@app.post("/users/")
async def create_user(
    data: UserCreate,
    container: Container = Depends(get_container),
):
    return await container.user_service.register(data.email, data.password)
```

---

## Що маєш вміти після уроку
- [ ] Пояснити кожен SOLID принцип і навести приклад порушення та виправлення
- [ ] Рефакторити "God Object" у декілька класів за SRP
- [ ] Реалізувати Repository Pattern з абстрактним інтерфейсом
- [ ] Написати DI Container і пояснити навіщо він
- [ ] Намалювати (або описати словами) шари Clean Architecture

---

## Що далі
`task.md`. Потім — **Урок 2: Design Patterns**.
