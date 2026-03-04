# Урок 4 — Функції

## Що вивчимо
- Визначення та виклик функцій (`def`, `return`)
- Параметри: позиційні, іменовані, зі значенням за замовчуванням
- `*args` та `**kwargs` — змінна кількість аргументів
- Область видимості: `global`, `nonlocal`, LEGB-правило
- Анотації типів (type hints)
- Lambda-функції
- Docstrings — документування функцій
- Функції вищого порядку: `map()`, `filter()`, `sorted()`

---

## Теорія

### 1. Базовий синтаксис

```python
# Визначення
def greet(name: str) -> str:
    """Повертає рядок привітання."""
    return f"Привіт, {name}!"

# Виклик
message = greet("Олег")
print(message)   # Привіт, Олег!

# Функція без return повертає None
def say_hello():
    print("Hello!")

result = say_hello()  # виводить: Hello!
print(result)         # None
```

---

### 2. Параметри та аргументи

```python
# Позиційні (порядок важливий)
def power(base, exponent):
    return base ** exponent

print(power(2, 10))   # 1024
print(power(10, 2))   # 100 — інший порядок, інший результат

# Значення за замовчуванням (default arguments)
def greet(name: str, greeting: str = "Привіт") -> str:
    return f"{greeting}, {name}!"

print(greet("Іван"))              # Привіт, Іван!
print(greet("Іван", "Доброго ранку"))  # Доброго ранку, Іван!

# Іменовані аргументи (keyword arguments)
def create_user(name: str, age: int, role: str = "user") -> dict:
    return {"name": name, "age": age, "role": role}

# Можна передавати в будь-якому порядку якщо іменовано
user = create_user(age=25, name="Аліса", role="admin")
print(user)
```

**Важливо: мутабельні дефолтні значення — пастка!**
```python
# ❌ НЕБЕЗПЕЧНО — список shared між усіма викликами!
def add_item(item, storage=[]):
    storage.append(item)
    return storage

print(add_item("яблуко"))   # ["яблуко"]
print(add_item("груша"))    # ["яблуко", "груша"] — несподівано!

# ✅ Правильно — використовуй None
def add_item(item, storage=None):
    if storage is None:
        storage = []
    storage.append(item)
    return storage
```

---

### 3. `*args` та `**kwargs`

```python
# *args — довільна кількість позиційних аргументів (tuple)
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3))          # 6
print(sum_all(1, 2, 3, 4, 5))    # 15
print(sum_all())                  # 0

# **kwargs — довільна кількість іменованих аргументів (dict)
def print_info(**data):
    for key, value in data.items():
        print(f"  {key}: {value}")

print_info(name="Аліса", age=25, city="Одеса")
# name: Аліса
# age: 25
# city: Одеса

# Комбінування (порядок суворий: позиційні, *args, дефолт, **kwargs)
def mixed(pos1, pos2, *args, keyword="default", **kwargs):
    print(f"pos1={pos1}, pos2={pos2}")
    print(f"args={args}")
    print(f"keyword={keyword}")
    print(f"kwargs={kwargs}")

mixed(1, 2, 3, 4, 5, keyword="hello", x=10, y=20)
```

**Розпакування при виклику:**
```python
def add(a, b, c):
    return a + b + c

numbers = [1, 2, 3]
print(add(*numbers))       # розпаковує список → add(1, 2, 3)

params = {"a": 1, "b": 2, "c": 3}
print(add(**params))       # розпаковує dict → add(a=1, b=2, c=3)
```

---

### 4. Область видимості — LEGB

Python шукає змінну у чотирьох областях (LEGB):
1. **L**ocal — поточна функція
2. **E**nclosing — зовнішня функція (якщо є)
3. **G**lobal — модуль (файл)
4. **B**uilt-in — вбудовані (`print`, `len`, ...)

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)    # local (L)

    inner()
    print(x)        # enclosing (E)

outer()
print(x)            # global (G)

# global — змінюємо глобальну змінну з функції
counter = 0

def increment():
    global counter
    counter += 1

increment()
increment()
print(counter)  # 2

# nonlocal — змінюємо змінну зовнішньої (не глобальної) функції
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c = make_counter()
print(c())  # 1
print(c())  # 2
print(c())  # 3
```

---

### 5. Анотації типів (Type Hints)

```python
# Базовий синтаксис
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str, times: int = 1) -> str:
    return (name + " ") * times

def process(items: list) -> None:
    for item in items:
        print(item)

# Складні типи (Python 3.9+ — можна писати list, dict, tuple напряму)
def get_names(users: list[dict]) -> list[str]:
    return [user["name"] for user in users]

def merge(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    return {**a, **b}

# Optional — значення або None
from typing import Optional

def find_user(user_id: int) -> Optional[dict]:
    # може повернути dict або None
    ...

# Union — один з типів (Python 3.10+: можна писати int | str)
def convert(value: int | str) -> str:
    return str(value)
```

**Анотації — підказки, не примус:**
```python
def add(a: int, b: int) -> int:
    return a + b

# Python не перевіряє типи при виконанні!
result = add("hello", " world")   # "hello world" — Python не кине помилку
# Але mypy (статичний аналізатор) виявить цю помилку
```

---

### 6. Lambda-функції

Lambda — анонімна однорядкова функція:

```python
# lambda параметри: вираз
square = lambda x: x ** 2
print(square(5))   # 25

add = lambda a, b: a + b
print(add(3, 4))   # 7

# Де lambda корисна — як аргумент функції
numbers = [3, -1, 7, -5, 2]
print(sorted(numbers))                  # [-5, -1, 2, 3, 7]
print(sorted(numbers, key=lambda x: abs(x)))  # [−1, 2, 3, −5, 7]

users = [{"name": "Аліса", "age": 30}, {"name": "Боб", "age": 25}]
sorted_by_age = sorted(users, key=lambda u: u["age"])
print(sorted_by_age[0]["name"])   # Боб

# Де lambda НЕ корисна — надто складна логіка, краще def
# ❌ Нечитабельно
f = lambda x: x if x > 0 else -x if x < 0 else 0

# ✅ Краще
def absolute(x):
    """Повертає абсолютне значення."""
    if x > 0: return x
    if x < 0: return -x
    return 0
```

---

### 7. Функції вищого порядку

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# map() — застосовує функцію до кожного елемента
squares = list(map(lambda x: x ** 2, numbers))
print(squares)  # [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

# filter() — залишає елементи де функція повертає True
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)    # [2, 4, 6, 8, 10]

# sorted() з key
words = ["banana", "apple", "cherry", "date"]
print(sorted(words))                        # за алфавітом
print(sorted(words, key=len))               # за довжиною
print(sorted(words, key=len, reverse=True)) # за довжиною, зворотно

# У реальному коді краще list comprehension (читабельніше)
squares = [x ** 2 for x in numbers]        # замість map
evens = [x for x in numbers if x % 2 == 0] # замість filter
```

---

### 8. Docstrings — документування

```python
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """
    Розраховує індекс маси тіла (BMI).

    Args:
        weight_kg: Вага у кілограмах.
        height_m: Зріст у метрах.

    Returns:
        BMI — значення типу float.

    Raises:
        ValueError: якщо вага або зріст <= 0.

    Example:
        >>> calculate_bmi(70, 1.75)
        22.857142857142858
    """
    if weight_kg <= 0 or height_m <= 0:
        raise ValueError("Вага і зріст повинні бути позитивними")
    return weight_kg / height_m ** 2

# Docstring доступний через __doc__
print(calculate_bmi.__doc__)
# Або через help()
help(calculate_bmi)
```

---

### Типові помилки

```python
# ❌ Мутабельний default argument
def append(item, lst=[]):    # lst shared між викликами!
    lst.append(item)
    return lst

# ❌ Глобальні змінні без потреби
total = 0
def add_to_total(x):
    global total    # ускладнює код, краще повернути значення
    total += x

# ✅ Чиста функція (pure function)
def add_to_total(current_total: int, x: int) -> int:
    return current_total + x

# ❌ Занадто довга функція (більше 20-30 рядків — розбий)
# ❌ Функція робить 5 різних речей (Single Responsibility!)

# ❌ Зайвий return None в кінці
def process(x):
    print(x)
    return None    # зайво — Python сам поверне None

# ✅
def process(x):
    print(x)
```

---

### У реальному проєкті

```python
# FastAPI — функції = endpoint handlers
from fastapi import FastAPI, HTTPException

app = FastAPI()

def get_or_404(db, model, item_id: int):
    """Дістає об'єкт або кидає 404."""
    obj = db.query(model).get(item_id)
    if obj is None:
        raise HTTPException(404, f"{model.__name__} з id={item_id} не знайдено")
    return obj

@app.get("/users/{user_id}")
async def get_user(user_id: int, db=Depends(get_db)):
    return get_or_404(db, User, user_id)

# Утилітарні функції — з типами і docstring
def paginate(query, page: int = 1, per_page: int = 20) -> dict:
    """Повертає пагіновані результати."""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page,
    }
```

---

## Що маєш вміти після уроку
- [ ] Написати функцію з анотаціями типів і docstring
- [ ] Коректно використати default arguments (не мутабельні!)
- [ ] Написати функцію з `*args` і `**kwargs`
- [ ] Пояснити LEGB-правило і продемонструвати `global` / `nonlocal`
- [ ] Написати lambda і пояснити коли вона доречна
- [ ] Відсортувати список об'єктів за полем через `key=`

---

## Що далі
Виконай завдання з `task.md`. Потім — **Модуль 2: Структури даних**.
