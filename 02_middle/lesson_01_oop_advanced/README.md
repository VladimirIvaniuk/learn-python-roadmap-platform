# Урок 1 — Поглиблене ООП: dunder, декоратори, ABC

## Що вивчимо
- Повний список dunder-методів та де їх застосовувати
- Написання декораторів: з аргументами, для класів
- `functools.wraps`, `functools.lru_cache`, `functools.cached_property`
- `@property` розширено: computed fields, lazy loading
- `__slots__` — оптимізація пам'яті
- `dataclasses` — декларативні дата-класи
- Protocol (structural subtyping) vs ABC (nominal)

---

## Теорія

### 1. Повний огляд dunder-методів

```python
class Vector:
    """Вектор у 2D просторі — демонстрація dunder."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    # ── Рядкове представлення ─────────────────────────────────────────────
    def __str__(self) -> str:
        return f"Vector({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Vector(x={self.x!r}, y={self.y!r})"

    # ── Арифметика ────────────────────────────────────────────────────────
    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector":
        return self.__mul__(scalar)   # scalar * vector

    def __neg__(self) -> "Vector":
        return Vector(-self.x, -self.y)

    def __abs__(self) -> float:
        import math
        return math.sqrt(self.x**2 + self.y**2)

    # ── Порівняння ────────────────────────────────────────────────────────
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __lt__(self, other: "Vector") -> bool:
        return abs(self) < abs(other)

    # ── Контейнер ────────────────────────────────────────────────────────
    def __len__(self) -> int:
        return 2   # завжди 2 компоненти

    def __getitem__(self, index: int) -> float:
        return (self.x, self.y)[index]

    def __iter__(self):
        yield self.x
        yield self.y

    # ── Bool ──────────────────────────────────────────────────────────────
    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0   # нульовий вектор = False

    # ── Хешування (якщо є __eq__, Python вимикає __hash__!) ──────────────
    def __hash__(self) -> int:
        return hash((self.x, self.y))


v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(v1 + v2)           # Vector(4, 6)
print(v1 * 2)            # Vector(6, 8)
print(3 * v1)            # Vector(9, 12)
print(abs(v1))           # 5.0
print(list(v1))          # [3, 4]
print(bool(Vector(0,0))) # False
print({v1, v2})          # можна в set через __hash__
```

---

### 2. Декоратори — повна версія

```python
import functools, time, logging

# Декоратор БЕЗ аргументів
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__}: {elapsed:.4f}с")
        return result
    return wrapper

# Декоратор З аргументами (фабрика декораторів)
def retry(times: int = 3, delay: float = 0.5, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

# Декоратор-клас (збергіє стан)
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        return self.func(*args, **kwargs)

@CountCalls
def add(a, b):
    return a + b

add(1, 2)
add(3, 4)
print(add.call_count)   # 2

# Декоратор і для функцій, і для методів класу (universal)
def log(func=None, *, level="INFO"):
    def decorator(f):
        logger = logging.getLogger(f.__module__)
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            logger.log(getattr(logging, level), f"Виклик {f.__name__}")
            return f(*args, **kwargs)
        return wrapper

    if func is not None:   # @log без ()
        return decorator(func)
    return decorator       # @log() з ()

@log                    # без аргументів
def greet(): pass

@log(level="DEBUG")     # з аргументами
def process(): pass
```

---

### 3. `functools` — корисні утиліти

```python
from functools import lru_cache, cached_property, partial, reduce

# lru_cache — мемоізація (кешування результатів)
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(50))    # миттєво завдяки кешу
print(fibonacci.cache_info())   # CacheInfo(hits=48, misses=51, ...)

# cached_property — обчислюється один раз, потім кешується
class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    @cached_property
    def area(self) -> float:
        import math
        print("  Обчислюю площу...")   # виконується тільки раз!
        return math.pi * self.radius ** 2

c = Circle(5)
print(c.area)   # Обчислюю площу... + результат
print(c.area)   # Тільки результат (з кешу)

# partial — часткове застосування функції
def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)
print(square(5))   # 25
print(cube(3))     # 27

# reduce — згортка
from functools import reduce
product = reduce(lambda a, b: a * b, [1, 2, 3, 4, 5])   # 120
```

---

### 4. `dataclasses` — дата-класи

```python
from dataclasses import dataclass, field, asdict, astuple
from typing import ClassVar

@dataclass
class Point:
    x: float
    y: float = 0.0   # значення за замовчуванням

    def distance_to_origin(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

p = Point(3, 4)
print(p)            # Point(x=3, y=4.0)
print(p == Point(3, 4.0))  # True  — автоматичний __eq__

@dataclass(frozen=True)  # незмінний (immutable) + __hash__
class Config:
    host: str = "localhost"
    port: int = 8000
    debug: bool = False

cfg = Config(port=9000)
# cfg.port = 8080   # FrozenInstanceError!
print(hash(cfg))    # можна в set/dict

@dataclass(order=True)   # додає __lt__, __le__, __gt__, __ge__
class Student:
    # порівнювальне поле (зазвичай перше)
    grade: float
    name: str
    # не в __init__ але обчислюється:
    tags: list[str] = field(default_factory=list)
    _db_count: ClassVar[int] = 0   # змінна класу, не поля

students = [Student(92, "Аліса"), Student(78, "Боб"), Student(88, "Катя")]
print(sorted(students))   # сортує по grade

# Конвертація
print(asdict(Point(3, 4)))    # {"x": 3, "y": 4.0}
print(astuple(Point(3, 4)))   # (3, 4.0)
```

---

### 5. `__slots__` — оптимізація пам'яті

```python
import sys

class RegularPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SlottedPoint:
    __slots__ = ("x", "y")   # забороняє __dict__, фіксує атрибути

    def __init__(self, x, y):
        self.x = x
        self.y = y

rp = RegularPoint(1, 2)
sp = SlottedPoint(1, 2)

print(sys.getsizeof(rp))   # ~48 байт (+ __dict__ ~232 байт)
print(sys.getsizeof(sp))   # ~56 байт (менше на ~200 байт!)

# ❌ Не можна додавати нові атрибути
# sp.z = 3   # AttributeError: 'SlottedPoint' object has no attribute 'z'
```

---

### 6. Protocol — структурна типізація (Duck Typing з типами)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> str: ...
    def resize(self, factor: float) -> None: ...

class Circle:
    def __init__(self, r: float) -> None:
        self.r = r
    def draw(self) -> str:
        return f"⭕ Circle(r={self.r})"
    def resize(self, factor: float) -> None:
        self.r *= factor

class Square:
    def __init__(self, side: float) -> None:
        self.side = side
    def draw(self) -> str:
        return f"⬛ Square(side={self.side})"
    def resize(self, factor: float) -> None:
        self.side *= factor

# Функція з Protocol (Duck Typing + type hints)
def render(shapes: list[Drawable]) -> None:
    for s in shapes:
        print(s.draw())

render([Circle(5), Square(3)])   # працює без явного успадкування!
print(isinstance(Circle(1), Drawable))   # True (через @runtime_checkable)
```

---

### Типові помилки

```python
# ❌ __eq__ без __hash__ — об'єкт стає неhashable
class Num:
    def __init__(self, v):
        self.v = v
    def __eq__(self, other):
        return self.v == other.v
    # __hash__ автоматично стає None!

n = Num(5)
{n: "value"}   # TypeError: unhashable type: 'Num'

# ✅ Явно визначити __hash__
class Num:
    def __eq__(self, other):
        return self.v == other.v
    def __hash__(self):
        return hash(self.v)

# ❌ lru_cache з мутабельними аргументами
@lru_cache
def process(data: list):   # TypeError: unhashable type: 'list'
    return sum(data)

# ✅ Використовуй tuple
@lru_cache
def process(data: tuple):
    return sum(data)
```

---

## Що маєш вміти після уроку
- [ ] Написати клас з `__add__`, `__eq__`, `__hash__`, `__iter__`
- [ ] Написати декоратор з аргументами (фабрику декораторів)
- [ ] Використати `@lru_cache` та `@cached_property`
- [ ] Описати клас через `@dataclass(frozen=True)`
- [ ] Пояснити різницю ABC (nominal) і Protocol (structural) типізації

---

## Що далі
`task.md`. Потім — **Урок 2: Асинхронність**.
