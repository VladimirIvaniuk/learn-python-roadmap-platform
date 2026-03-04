# Завдання — OOP Advanced

## Завдання 1 — Повний Vector клас
Реалізуй клас `Vector2D(x, y)` з дunder методами:
`__add__`, `__sub__`, `__mul__` (скаляр), `__rmul__`, `__neg__`, `__abs__`,
`__eq__`, `__hash__`, `__iter__`, `__len__`, `__getitem__`, `__bool__`, `__repr__`, `__str__`.
Протестуй `sorted([Vector(3,4), Vector(1,1), Vector(5,0)])`.

## Завдання 2 — Декоратор з аргументами
Напиши `@validate_types` декоратор що перевіряє типи аргументів за анотаціями функції.
Кидає `TypeError` якщо тип не відповідає.
```python
@validate_types
def add(a: int, b: int) -> int:
    return a + b
add(1, "2")  # → TypeError: arg 'b' expected int, got str
```

## Завдання 3 — dataclass
Створи `@dataclass(frozen=True) class Config` з полями:
`host: str`, `port: int`, `debug: bool = False`, `cors_origins: tuple[str, ...] = ()`.
Додай `@classmethod from_env()` що читає з `os.environ`.
Переконайся що Config можна використати як ключ у dict.

## Завдання 4 — lru_cache
Порівняй час рекурсивного fibonacci(35) без кешу і з `@lru_cache`.
Напиши `memoize` декоратор — свій аналог `lru_cache` без обмеження розміру.

## Завдання 5 (Challenge) — Observable
Реалізуй `Observable` mixin що дозволяє підписатись на зміни атрибутів.
```python
class User(Observable):
    name: str
    email: str

u = User()
u.on_change("name", lambda old, new: print(f"name: {old} → {new}"))
u.name = "Аліса"   # → name: None → Аліса
```
