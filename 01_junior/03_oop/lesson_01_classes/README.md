# Урок 1 — Класи та об'єкти

## Що вивчимо
- Що таке клас і об'єкт (instance)
- `__init__` — конструктор, `self`
- Атрибути об'єкта та класу
- Методи: звичайні, `@classmethod`, `@staticmethod`
- `__str__` та `__repr__` — рядкове представлення
- Порівняння об'єктів: `__eq__`, `__lt__`
- Інкапсуляція: публічні, `_захищені`, `__приватні` атрибути
- `@property` — атрибути з логікою

---

## Теорія

### 1. Клас і об'єкт

**Клас** — це шаблон (blueprint). **Об'єкт** — конкретний екземпляр класу.

```
Клас "Автомобіль"         Об'єкти
┌─────────────────┐      ┌──────────────────┐
│ Атрибути:       │  →   │ Toyota, 2020, red│
│   brand         │      │ BMW,    2022, blue│
│   year          │      │ Ford,   2019, grey│
│   color         │      └──────────────────┘
│ Методи:         │
│   start()       │
│   stop()        │
└─────────────────┘
```

```python
class BankAccount:
    """Банківський рахунок."""

    bank_name = "MyBank"   # атрибут КЛАСУ — shared між усіма екземплярами

    def __init__(self, owner: str, balance: float = 0.0):
        # атрибути ЕКЗЕМПЛЯРА — унікальні для кожного об'єкта
        self.owner = owner
        self._balance = balance      # _ = захищений (конвенція, не примус)
        self._transactions = []

    def deposit(self, amount: float) -> None:
        """Поповнити рахунок."""
        if amount <= 0:
            raise ValueError("Сума поповнення має бути позитивною")
        self._balance += amount
        self._transactions.append(("deposit", amount))

    def withdraw(self, amount: float) -> None:
        """Зняти кошти."""
        if amount <= 0:
            raise ValueError("Сума зняття має бути позитивною")
        if amount > self._balance:
            raise ValueError(f"Недостатньо коштів: маєш {self._balance}, намагаєшся зняти {amount}")
        self._balance -= amount
        self._transactions.append(("withdraw", amount))

    def get_balance(self) -> float:
        return self._balance

# Використання
acc = BankAccount("Аліса", 1000)
acc.deposit(500)
acc.withdraw(200)
print(acc.get_balance())    # 1300.0
print(BankAccount.bank_name)  # MyBank
print(acc.bank_name)          # MyBank  (доступно і через екземпляр)
```

---

### 2. `__str__` та `__repr__`

```python
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        """Для людини — print(), str()."""
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        """Для розробника — repr(), у консолі."""
        return f"Point(x={self.x}, y={self.y})"

    def __eq__(self, other) -> bool:
        """Порівняння =="""
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __lt__(self, other) -> bool:
        """Порівняння < — дозволяє sorted()"""
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x ** 2 + self.y ** 2) < (other.x ** 2 + other.y ** 2)

p1 = Point(3, 4)
p2 = Point(3, 4)
p3 = Point(1, 1)

print(str(p1))     # (3, 4)
print(repr(p1))    # Point(x=3, y=4)
print(p1)          # (3, 4)  ← використовує __str__

print(p1 == p2)    # True
print(p1 == p3)    # False
print(sorted([p1, p3, Point(5, 0)]))  # сортування через __lt__
```

---

### 3. `@classmethod` та `@staticmethod`

```python
from datetime import date

class User:
    def __init__(self, name: str, birth_year: int):
        self.name = name
        self.birth_year = birth_year

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Альтернативний конструктор."""
        return cls(data["name"], data["birth_year"])

    @classmethod
    def from_string(cls, s: str) -> "User":
        """Парсинг з рядка 'Аліса:1998'."""
        name, year = s.split(":")
        return cls(name, int(year))

    @staticmethod
    def is_valid_name(name: str) -> bool:
        """Утиліта — не потребує self або cls."""
        return bool(name) and name.replace(" ", "").isalpha()

    @property
    def age(self) -> int:
        """Обчислюваний атрибут."""
        return date.today().year - self.birth_year

# Використання
u1 = User("Аліса", 1998)
u2 = User.from_dict({"name": "Боб", "birth_year": 1995})
u3 = User.from_string("Катя:2000")

print(u1.age)                      # 28 (у 2026)
print(User.is_valid_name("Аліса")) # True
print(User.is_valid_name("123"))   # False
```

---

### 4. Інкапсуляція та `@property`

```python
class Temperature:
    """Температура з конвертацією Celsius ↔ Fahrenheit."""

    def __init__(self, celsius: float = 0.0):
        self._celsius = celsius    # _ конвенційно "захищений"

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError(f"Температура нижче абсолютного нуля: {value}")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9/5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = (value - 32) * 5/9

    def __repr__(self) -> str:
        return f"Temperature({self._celsius}°C / {self.fahrenheit:.1f}°F)"

t = Temperature(100)
print(t)                    # Temperature(100°C / 212.0°F)
t.fahrenheit = 32
print(t.celsius)            # 0.0

# try:
#     t.celsius = -300   # ValueError!
# except ValueError as e:
#     print(e)
```

---

### 5. Магічні методи — `__len__`, `__contains__`, `__iter__`

```python
class Playlist:
    def __init__(self, name: str):
        self.name = name
        self._songs = []

    def add(self, song: str) -> None:
        self._songs.append(song)

    def __len__(self) -> int:
        return len(self._songs)

    def __contains__(self, song: str) -> bool:
        return song in self._songs

    def __iter__(self):
        return iter(self._songs)

    def __getitem__(self, index):
        return self._songs[index]

    def __repr__(self) -> str:
        return f"Playlist('{self.name}', {len(self)} songs)"

pl = Playlist("Ранковий")
pl.add("Bohemian Rhapsody")
pl.add("Hotel California")
pl.add("Stairway to Heaven")

print(len(pl))                      # 3
print("Hotel California" in pl)     # True
print(pl[0])                        # Bohemian Rhapsody

for song in pl:
    print(f"  🎵 {song}")
```

---

### 6. Приватні атрибути та `name mangling`

```python
class Secret:
    def __init__(self):
        self.public = "публічний"
        self._protected = "захищений (конвенція)"
        self.__private = "справді приватний (name mangling)"

    def reveal(self):
        return self.__private

s = Secret()
print(s.public)                   # публічний
print(s._protected)               # захищений (конвенція, але некрасиво)
# print(s.__private)              # AttributeError!
print(s._Secret__private)         # "справді приватний" — обходиться через mangling
print(s.reveal())                 # публічний метод для доступу
```

---

### Типові помилки

```python
# ❌ Забули self у методі
class Counter:
    def __init__(self):
        self.count = 0

    def increment():          # Забули self!
        self.count += 1       # TypeError при виклику

# ❌ Плутанина атрибута класу та екземпляра
class Dog:
    tricks = []               # НЕБЕЗПЕЧНО — shared між усіма собаками!

    def learn_trick(self, trick):
        self.tricks.append(trick)

d1 = Dog()
d2 = Dog()
d1.learn_trick("roll over")
print(d2.tricks)              # ["roll over"]  — несподівано!

# ✅ Правильно
class Dog:
    def __init__(self):
        self.tricks = []      # унікальний для кожного екземпляра

# ❌ __eq__ без isinstance перевірки
class Num:
    def __init__(self, v):
        self.v = v
    def __eq__(self, other):
        return self.v == other.v  # AttributeError якщо other не Num!

# ✅ Правильно
    def __eq__(self, other):
        if not isinstance(other, Num):
            return NotImplemented
        return self.v == other.v
```

---

### У реальному проєкті

```python
# Pydantic (FastAPI використовує для валідації)
from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Мінімум 3 символи")
        return v.lower()

# SQLAlchemy model
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username!r})"
```

---

## Що маєш вміти після уроку
- [ ] Написати клас з `__init__`, методами, `__str__`, `__repr__`
- [ ] Пояснити різницю між атрибутом класу та екземпляра
- [ ] Створити `@classmethod` як альтернативний конструктор
- [ ] Використати `@property` + setter з валідацією
- [ ] Пояснити різницю `_protected` vs `__private`

---

## Що далі
Виконай завдання з `task.md`. Потім — **Урок 2: Успадкування**.
