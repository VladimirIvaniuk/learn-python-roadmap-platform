# Завдання — Урок 1: Класи та об'єкти

## Завдання 1 — Книга
Створи клас `Book` з атрибутами `title`, `author`, `pages`, `year`.
- `__str__`: `"'Кобзар' — Тарас Шевченко (1840)"`
- `__repr__`: `"Book(title='Кобзар', author='Тарас Шевченко', pages=312, year=1840)"`
- Метод `is_classic()` → `True` якщо рік < 1970

---

## Завдання 2 — Прямокутник
Клас `Rectangle(width, height)`:
- Методи `area()` та `perimeter()`
- `@classmethod square(cls, side)` → квадрат зі стороною `side`
- `@staticmethod is_valid(width, height)` → `True` якщо обидва > 0
- `__eq__` — рівні якщо однакова площа
- `__lt__` — менший якщо менша площа

---

## Завдання 3 — Банківський рахунок
Клас `BankAccount(owner, balance=0)`:
- `@property balance` з setter що перевіряє: баланс не може стати від'ємним
- `deposit(amount)` та `withdraw(amount)` з валідацією
- Властивість `transactions` — список усіх операцій
- `__str__`: `"Рахунок Аліси: 1500.00 грн"`

---

## Завдання 4 — @property температура
Клас `Temperature(celsius=0)`:
- `@property celsius` — з валідацією (мінімум −273.15)
- `@property fahrenheit` — обчислюваний (F = C × 9/5 + 32)
- `@property kelvin` — обчислюваний (K = C + 273.15)
- Сеттери для fahrenheit та kelvin що конвертують і встановлюють celsius

---

## Завдання 5 (Challenge) — Черга (Queue)
Реалізуй клас `Queue` (FIFO) з методами:
`enqueue(item)`, `dequeue() -> item` (ValueError якщо порожня),
`peek() -> item`, `is_empty()`, `__len__`, `__contains__`, `__repr__`
