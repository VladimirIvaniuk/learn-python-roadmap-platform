"""
Розв'язки — OOP Advanced (Middle)
"""
from __future__ import annotations
import math
import os
import time
import threading
from dataclasses import dataclass, field
from functools import lru_cache, wraps
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)

# ── Завдання 1 — Vector2D ─────────────────────────────────────────────────────
class Vector2D:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vector2D({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2D:
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vector2D:
        return self.__mul__(scalar)

    def __neg__(self) -> Vector2D:
        return Vector2D(-self.x, -self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def __abs__(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __bool__(self) -> bool:
        return abs(self) > 0

    def dot(self, other: Vector2D) -> float:
        return self.x * other.x + self.y * other.y

    def normalized(self) -> Vector2D:
        length = abs(self)
        if length == 0:
            raise ValueError("Cannot normalize zero vector")
        return Vector2D(self.x / length, self.y / length)

v1 = Vector2D(3, 4)
v2 = Vector2D(1, 2)
print(v1 + v2, v1 - v2, v1 * 2, 3 * v1)
print(f"|v1| = {abs(v1)}, dot = {v1.dot(v2)}")

# ── Завдання 2 — type_validated декоратор ─────────────────────────────────────
def type_validated(func: F) -> F:
    """Перевіряє типи аргументів за анотаціями при виклику."""
    hints = func.__annotations__

    @wraps(func)
    def wrapper(*args, **kwargs):
        import inspect
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for param_name, value in bound.arguments.items():
            if param_name in hints and param_name != "return":
                expected = hints[param_name]
                if not isinstance(value, expected):
                    raise TypeError(
                        f"Параметр {param_name!r}: очікується {expected.__name__}, "
                        f"отримано {type(value).__name__}"
                    )
        return func(*args, **kwargs)
    return wrapper  # type: ignore

@type_validated
def add(a: int, b: int) -> int:
    return a + b

print(add(1, 2))
try:
    print(add(1, "2"))
except TypeError as e:
    print(f"TypeError: {e}")

# ── Завдання 3 — Config dataclass ─────────────────────────────────────────────
@dataclass(frozen=True)
class Config:
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    workers: int = 4

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            host    = os.getenv("HOST", "localhost"),
            port    = int(os.getenv("PORT", "8000")),
            debug   = os.getenv("DEBUG", "false").lower() == "true",
            workers = int(os.getenv("WORKERS", "4")),
        )

cfg = Config.from_env()
print(f"\n{cfg}")
print(f"hashable: {hash(cfg)}")

# ── Завдання 4 — lru_cache vs manual memoize ──────────────────────────────────
@lru_cache(maxsize=None)
def fib_cached(n: int) -> int:
    if n <= 1:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)

t0 = time.perf_counter()
_ = [fib_cached(i) for i in range(50)]
print(f"\nlru_cache fib(49)={fib_cached(49)}, time={time.perf_counter()-t0:.6f}s")

def memoize(func: F) -> F:
    cache: dict = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    wrapper.cache = cache  # type: ignore
    return wrapper  # type: ignore

@memoize
def fib_manual(n: int) -> int:
    if n <= 1:
        return n
    return fib_manual(n - 1) + fib_manual(n - 2)

print(f"manual memoize fib(49)={fib_manual(49)}")

# ── Завдання 5 (Challenge) — Observable Mixin ────────────────────────────────
class ObservableMixin:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._listeners: dict[str, list[Callable]] = {}

    def subscribe(self, event: str, listener: Callable) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(listener)

    def emit(self, event: str, *args, **kwargs) -> None:
        for listener in self._listeners.get(event, []):
            listener(*args, **kwargs)

class Store(ObservableMixin):
    def __init__(self) -> None:
        self._data: dict = {}
        self._listeners = {}

    def set(self, key: str, value) -> None:
        old = self._data.get(key)
        self._data[key] = value
        self.emit("change", key=key, old=old, new=value)

    def get(self, key: str, default=None):
        return self._data.get(key, default)

store = Store()
store.subscribe("change", lambda **kw: print(f"  [change] {kw['key']}: {kw['old']} → {kw['new']}"))
store.set("count", 0)
store.set("count", 1)
store.set("name", "test")
