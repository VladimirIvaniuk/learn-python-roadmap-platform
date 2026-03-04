# Урок 2 — Успадкування та поліморфізм

## Що вивчимо
- Успадкування: `class Child(Parent)`
- `super()` — виклик батьківського методу
- Перевизначення (override) методів
- Поліморфізм — один інтерфейс, різна поведінка
- Множинне успадкування та MRO
- Абстрактні класи (`ABC`, `@abstractmethod`)
- `isinstance()` та `issubclass()`

---

## Теорія

### 1. Базове успадкування

```python
class Animal:
    """Базовий клас тварини."""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def speak(self) -> str:
        return "..."

    def info(self) -> str:
        return f"{self.__class__.__name__}: {self.name}, {self.age} років"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, age={self.age})"


class Dog(Animal):
    def __init__(self, name: str, age: int, breed: str):
        super().__init__(name, age)    # викликаємо конструктор батька
        self.breed = breed

    def speak(self) -> str:           # override
        return "Гав!"

    def fetch(self) -> str:
        return f"{self.name} приніс м'яч!"


class Cat(Animal):
    def speak(self) -> str:
        return "Няв!"

    def purr(self) -> str:
        return "Муррр..."


class Duck(Animal):
    def speak(self) -> str:
        return "Кря!"


# Використання
dog = Dog("Рекс", 3, "Лабрадор")
cat = Cat("Мурка", 5)

print(dog.speak())    # Гав!
print(cat.speak())    # Няв!
print(dog.info())     # Dog: Рекс, 3 років
print(dog.fetch())    # Рекс приніс м'яч!
print(repr(dog))      # Dog(name='Рекс', age=3)
```

---

### 2. Поліморфізм

Один і той самий код працює з різними типами об'єктів:

```python
animals = [Dog("Рекс", 3, "Лабрадор"), Cat("Мурка", 5), Duck("Дональд", 2)]

# Поліморфний виклик — кожен говорить по-своєму
for animal in animals:
    print(f"{animal.name}: {animal.speak()}")
# Рекс: Гав!
# Мурка: Няв!
# Дональд: Кря!

# Функція що приймає будь-яку тварину
def make_noise(animal: Animal) -> str:
    return f"{animal.name} каже: {animal.speak()}"

# Duck typing — Python не перевіряє тип, тільки наявність методу
class Robot:
    name = "R2D2"
    def speak(self):
        return "Бip-Бoп!"

print(make_noise(Robot()))   # R2D2 каже: Бip-Бoп! (не є Animal, але має speak)
```

---

### 3. `super()` та ланцюжок ініціалізації

```python
class Vehicle:
    def __init__(self, brand: str, year: int):
        self.brand = brand
        self.year = year

    def info(self) -> str:
        return f"{self.brand} ({self.year})"


class Car(Vehicle):
    def __init__(self, brand: str, year: int, doors: int = 4):
        super().__init__(brand, year)    # ← виклик Vehicle.__init__
        self.doors = doors

    def info(self) -> str:
        return f"{super().info()}, {self.doors} дверей"   # ← розширення


class ElectricCar(Car):
    def __init__(self, brand: str, year: int, range_km: int):
        super().__init__(brand, year)
        self.range_km = range_km

    def info(self) -> str:
        return f"{super().info()}, {self.range_km} км запас ходу"


tesla = ElectricCar("Tesla", 2024, 600)
print(tesla.info())
# Tesla (2024), 4 дверей, 600 км запас ходу
```

---

### 4. Абстрактні класи (ABC)

Абстрактний клас визначає **інтерфейс** — що повинен вміти клас, але не як.  
Створити об'єкт абстрактного класу неможливо.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    """Абстрактна фігура."""

    @abstractmethod
    def area(self) -> float:
        """Площа фігури."""
        ...

    @abstractmethod
    def perimeter(self) -> float:
        """Периметр фігури."""
        ...

    def describe(self) -> str:
        """Конкретний метод — доступний усім нащадкам."""
        return f"{self.__class__.__name__}: площа={self.area():.2f}, периметр={self.perimeter():.2f}"


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


# Спроба створити абстрактний клас
# shape = Shape()   # TypeError: Can't instantiate abstract class

shapes: list[Shape] = [Circle(5), Rectangle(4, 6)]
for shape in shapes:
    print(shape.describe())
# Circle: площа=78.54, периметр=31.42
# Rectangle: площа=24.00, периметр=20.00

# Загальна функція — приймає будь-яку Shape
def total_area(shapes: list[Shape]) -> float:
    return sum(s.area() for s in shapes)

print(f"Загальна площа: {total_area(shapes):.2f}")
```

---

### 5. Множинне успадкування та MRO

```python
class Flyable:
    def fly(self) -> str:
        return "Летить!"

class Swimmable:
    def swim(self) -> str:
        return "Пливе!"

class Duck(Animal, Flyable, Swimmable):
    def speak(self) -> str:
        return "Кря!"

duck = Duck("Дональд", 2)
print(duck.speak())   # Кря!
print(duck.fly())     # Летить!
print(duck.swim())    # Пливе!

# MRO — порядок пошуку методів
print(Duck.__mro__)
# (<class 'Duck'>, <class 'Animal'>, <class 'Flyable'>, <class 'Swimmable'>, <class 'object'>)
```

**Diamond problem та `super()`:**
```python
class A:
    def hello(self):
        print("A.hello")
        super().hello()   # викликає наступний у MRO

class B(A):
    def hello(self):
        print("B.hello")
        super().hello()

class C(A):
    def hello(self):
        print("C.hello")
        super().hello()

class D(B, C):
    def hello(self):
        print("D.hello")
        super().hello()

# MRO: D → B → C → A → object
D().hello()
# D.hello
# B.hello
# C.hello
# A.hello
```

---

### 6. `isinstance()` та `issubclass()`

```python
dog = Dog("Рекс", 3, "Лабрадор")
cat = Cat("Мурка", 5)

print(isinstance(dog, Dog))      # True
print(isinstance(dog, Animal))   # True  — нащадок теж є Animal
print(isinstance(dog, Cat))      # False

print(issubclass(Dog, Animal))   # True
print(issubclass(Cat, Animal))   # True
print(issubclass(Dog, Cat))      # False

# Практичне застосування
def process_animal(animal):
    if isinstance(animal, Dog):
        print(animal.fetch())
    elif isinstance(animal, Cat):
        print(animal.purr())
    print(animal.speak())
```

---

### Mixin паттерн

```python
class JsonMixin:
    """Mixin для серіалізації в JSON."""
    import json as _json

    def to_json(self) -> str:
        return self._json.dumps(self.__dict__, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str):
        data = cls._json.loads(json_str)
        return cls(**data)


class LogMixin:
    """Mixin для логування."""
    def log(self, message: str) -> None:
        print(f"[{self.__class__.__name__}] {message}")


class ApiUser(LogMixin, JsonMixin):
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

u = ApiUser("Аліса", "alice@example.com")
print(u.to_json())                 # {"name": "Аліса", "email": "alice@example.com"}
u.log("Авторизувався")             # [ApiUser] Авторизувався
```

---

### Типові помилки

```python
# ❌ Забули super().__init__()
class Child(Parent):
    def __init__(self, x, y, z):
        self.z = z
        # Забули! super().__init__(x, y)
        # self.x, self.y не визначені

# ❌ Перевизначили метод і забули про батьківську логіку
class LoggedBankAccount(BankAccount):
    def deposit(self, amount):
        # ПОВНІСТЮ замінили батьківський метод!
        self._balance += amount    # немає перевірки amount > 0

# ✅ Правильно
    def deposit(self, amount):
        super().deposit(amount)    # батьківська перевірка + операція
        print(f"Logged: deposit {amount}")

# ❌ Перевірка типу через type() замість isinstance()
if type(dog) == Animal:     # False для Dog (нащадка)!
    pass
if isinstance(dog, Animal): # ✅ True для Dog та всіх нащадків
    pass
```

---

### У реальному проєкті

```python
# Репозиторій з абстрактним інтерфейсом (Repository Pattern)
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> dict | None: ...

    @abstractmethod
    async def create(self, data: dict) -> dict: ...

    @abstractmethod
    async def update(self, user_id: int, data: dict) -> dict | None: ...

class SQLUserRepository(UserRepository):
    def __init__(self, db):
        self.db = db

    async def get_by_id(self, user_id: int) -> dict | None:
        return self.db.query(User).get(user_id)

    async def create(self, data: dict) -> dict:
        user = User(**data)
        self.db.add(user)
        self.db.commit()
        return user

class InMemoryUserRepository(UserRepository):
    """Для тестів — без БД."""
    def __init__(self):
        self._data: dict[int, dict] = {}
        self._next_id = 1

    async def get_by_id(self, user_id: int) -> dict | None:
        return self._data.get(user_id)

    async def create(self, data: dict) -> dict:
        user = {"id": self._next_id, **data}
        self._data[self._next_id] = user
        self._next_id += 1
        return user
```

---

## Що маєш вміти після уроку
- [ ] Написати ієрархію класів (Animal → Dog, Cat)
- [ ] Правильно використати `super().__init__()`
- [ ] Пояснити різницю override та overload
- [ ] Написати абстрактний клас з `@abstractmethod`
- [ ] Використати `isinstance()` для поліморфної диспетчеризації
- [ ] Прочитати MRO через `ClassName.__mro__`

---

## Що далі
Виконай завдання з `task.md`. Потім — **Модуль 4: Файли та виключення**.
