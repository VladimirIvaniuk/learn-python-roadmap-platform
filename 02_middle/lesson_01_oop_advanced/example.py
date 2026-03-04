"""
Урок Middle 1 — Приклади: поглиблене ООП
"""
import math
import functools
import time
from dataclasses import dataclass, field


# ── Повний клас з dunder методами ─────────────────────────────────────────────
class Vector:
    """2D вектор з повною реалізацією dunder методів."""

    __slots__ = ("x", "y")   # оптимізація пам'яті

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, s: float) -> "Vector":
        return Vector(self.x * s, self.y * s)

    def __rmul__(self, s: float) -> "Vector":
        return self.__mul__(s)

    def __neg__(self) -> "Vector":
        return Vector(-self.x, -self.y)

    def __abs__(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __lt__(self, other: "Vector") -> bool:
        return abs(self) < abs(other)

    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __iter__(self):
        yield self.x
        yield self.y

    def __len__(self) -> int:
        return 2


v1, v2 = Vector(3, 4), Vector(1, 2)
print(f"v1={v1}, v2={v2}")
print(f"v1+v2={v1+v2}, v1*3={v1*3}, -v1={-v1}")
print(f"|v1|={abs(v1)}, sorted: {sorted([Vector(3,4), Vector(1,1), Vector(5,0)])}")
print(f"bool(Vector(0,0))={bool(Vector(0,0))}, bool(v1)={bool(v1)}")
print(f"list(v1)={list(v1)}, in set: {len({v1, v2, v1}) == 2}")


# ── Декоратор з аргументами ────────────────────────────────────────────────────
def retry(times: int = 3, delay: float = 0.0, exceptions: tuple = (Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if i == times:
                        raise
                    print(f"  Retry {i}/{times}: {e}")
                    if delay:
                        time.sleep(delay)
        return wrapper
    return decorator


_attempt = 0

@retry(times=3, exceptions=(ValueError,))
def flaky():
    global _attempt
    _attempt += 1
    if _attempt < 3:
        raise ValueError(f"Not ready (attempt {_attempt})")
    return "success"

print(f"\nRetry: {flaky()}")


# ── lru_cache vs manual recursion ────────────────────────────────────────────
def fib_slow(n: int) -> int:
    if n < 2:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)

@functools.lru_cache(maxsize=None)
def fib_fast(n: int) -> int:
    if n < 2:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)

@functools.cached_property
def _heavy_calculation(self): ...

n = 30
t0 = time.perf_counter()
fib_slow(n)
slow_time = time.perf_counter() - t0

t0 = time.perf_counter()
fib_fast(n)
fast_time = time.perf_counter() - t0

print(f"\nfib({n}):")
print(f"  Без кешу: {slow_time:.4f}с")
print(f"  lru_cache: {fast_time:.6f}с (x{slow_time/max(fast_time,1e-9):.0f} швидше!)")
print(f"  Cache info: {fib_fast.cache_info()}")


# ── dataclass ─────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Config:
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    tags: tuple[str, ...] = ()

cfg1 = Config(port=9000, tags=("api", "v2"))
cfg2 = Config(port=9000, tags=("api", "v2"))
print(f"\nConfig: {cfg1}")
print(f"Frozen eq: {cfg1 == cfg2}")
print(f"Hashable: {hash(cfg1)}")
print(f"Can be dict key: { {cfg1: 'value'}[cfg1]}")

# ── Protocol ──────────────────────────────────────────────────────────────────
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str: ...

class HtmlButton:
    def __init__(self, text: str) -> None:
        self.text = text
    def render(self) -> str:
        return f'<button>{self.text}</button>'

class MarkdownButton:
    def __init__(self, text: str) -> None:
        self.text = text
    def render(self) -> str:
        return f'**[{self.text}]**'

def display_all(items: list[Renderable]) -> None:
    for item in items:
        print(f"  {item.render()}")

print("\nProtocol (Duck Typing with types):")
display_all([HtmlButton("Натисни"), MarkdownButton("Натисни")])
