# Завдання — Урок 2: Успадкування та поліморфізм

## Завдання 1 — Зоопарк
Ієрархія класів:
- `Animal(name, age)` — базовий з методами `speak()` → `"..."` і `info()`
- `Dog(name, age, breed)` — `speak()` → `"Гав!"`, `fetch()` → `f"{name} приніс м'яч!"`
- `Cat(name, age)` — `speak()` → `"Няв!"`, `purr()` → `"Мурр..."`
- `Bird(name, age, can_fly)` — `speak()` → `"Цвірінь!"`, `move()` → `"Летить!"/"Іде!"`

Створи список тварин і виведи що каже кожна (поліморфізм).

---

## Завдання 2 — Фігури (ABC)
Абстрактний клас `Shape`:
- Абстрактні методи: `area()`, `perimeter()`
- Конкретний `describe()` → рядок з площею та периметром

Реалізуй: `Circle(radius)`, `Rectangle(w, h)`, `Triangle(a, b, c)` (формула Герона).

Напиши `total_area(shapes: list[Shape])` та `largest(shapes: list[Shape])`.

---

## Завдання 3 — Транспорт
`Vehicle(brand, year)` → `Car(brand, year, doors)` → `ElectricCar(brand, year, range_km)`
- Кожен клас перевизначає `info()` розширюючи батьківський через `super().info()`
- `Car` додає `.start_engine()`, `ElectricCar` — `.charge()`

---

## Завдання 4 — Mixin
Напиши `SerializableMixin` з методами `to_dict()` та `from_dict(cls, d)`.
Напиши `ValidatableMixin` з `validate()` що перевіряє обов'язкові поля.
Застосуй обидва до класу `User(name, email, age)`.

---

## Завдання 5 (Challenge) — Репозиторій
Абстрактний `Repository[T]` з методами:
`add(item)`, `get(id) -> T | None`, `all() -> list[T]`, `delete(id)`, `count() -> int`

Реалізуй `InMemoryRepository` та перевір через `UserRepository(InMemoryRepository)`.
