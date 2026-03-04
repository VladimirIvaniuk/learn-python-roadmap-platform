# Урок 3 — Comprehensions та генератори

## Що вивчимо
- List comprehension — компактні списки
- Dict comprehension та Set comprehension
- Вкладені comprehensions
- Generator expression — ліниве обчислення
- `yield` — генераторні функції
- `itertools` — корисні ітератори

---

## Теорія

### 1. List Comprehension

**Базовий синтаксис:** `[вираз for елемент in послідовність if умова]`

```python
# Еквівалентний цикл → comprehension
squares_loop = []
for x in range(1, 6):
    squares_loop.append(x ** 2)

# ✅ Comprehension — чистіше і швидше
squares = [x ** 2 for x in range(1, 6)]
print(squares)   # [1, 4, 9, 16, 25]

# З умовою (фільтр)
evens = [x for x in range(20) if x % 2 == 0]
print(evens)     # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Трансформація рядків
words = ["hello", "world", "python"]
upper = [w.upper() for w in words]
lengths = [len(w) for w in words]
long_upper = [w.upper() for w in words if len(w) > 4]

# Якщо/інакше у виразі (не у фільтрі)
labels = ["парне" if x % 2 == 0 else "непарне" for x in range(6)]
print(labels)   # ['парне', 'непарне', 'парне', 'непарне', 'парне', 'непарне']
```

---

### 2. Dict та Set Comprehension

```python
# Dict comprehension: {ключ: значення for ... if ...}
numbers = [1, 2, 3, 4, 5]
squares_dict = {n: n**2 for n in numbers}
print(squares_dict)   # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Інвертувати словник (ключі ↔ значення)
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
print(inverted)       # {1: "a", 2: "b", 3: "c"}

# Фільтрація словника
grades = {"Аліса": 92, "Боб": 58, "Катя": 85, "Денис": 71}
passed = {name: grade for name, grade in grades.items() if grade >= 70}
print(passed)         # {"Аліса": 92, "Катя": 85, "Денис": 71}

# Нормалізація ключів
raw = {"  Name ": "Аліса", "AGE": 25}
normalized = {k.strip().lower(): v for k, v in raw.items()}
print(normalized)     # {"name": "Аліса", "age": 25}

# Set comprehension: {вираз for ...}
words = ["apple", "banana", "avocado", "blueberry", "cherry"]
first_letters = {w[0] for w in words}
print(first_letters)  # {"a", "b", "c"}  (порядок не гарантований)
```

---

### 3. Вкладені Comprehensions

```python
# Матриця 3×4
matrix = [[i * j for j in range(1, 5)] for i in range(1, 4)]
print(matrix)
# [[1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12]]

# Розгорнути матрицю в список (flatten)
flat = [x for row in matrix for x in row]
print(flat)   # [1, 2, 3, 4, 2, 4, 6, 8, 3, 6, 9, 12]

# Читається як: "для кожного row в matrix, для кожного x в row"
# Еквівалентно:
flat = []
for row in matrix:
    for x in row:
        flat.append(x)

# Декартовий добуток (усі комбінації)
colors = ["red", "green"]
sizes = ["S", "M", "L"]
products = [f"{c}-{s}" for c in colors for s in sizes]
print(products)
# ['red-S', 'red-M', 'red-L', 'green-S', 'green-M', 'green-L']
```

---

### 4. Generator Expression — ліниве обчислення

**Відмінність:** list comprehension обчислює всі значення одразу,  
генераторний вираз — по одному, тільки коли потрібно.

```python
# List comprehension — всі 1 млн елементів у пам'яті відразу
squares_list = [x**2 for x in range(1_000_000)]   # ~8 MB пам'яті

# Generator expression — обчислює один елемент при запиті
squares_gen = (x**2 for x in range(1_000_000))     # ~кілька байт

# Використання
import sys
print(sys.getsizeof(squares_list))   # ~8 MB
print(sys.getsizeof(squares_gen))    # ~104 байти!

# Генератор можна використати тільки ОДИН РАЗ
gen = (x**2 for x in range(5))
print(list(gen))    # [0, 1, 4, 9, 16]
print(list(gen))    # []  — вже вичерпаний!

# Ефективні обчислення
total = sum(x**2 for x in range(1_000_000))   # не потребує списку в пам'яті
first_even = next(x for x in range(100) if x % 7 == 0)  # знаходить першийBez зайвого

# any/all з генератором — зупиняється раніше
has_admin = any(u["role"] == "admin" for u in users)   # зупиняється на першому admin
all_active = all(u["active"] for u in users)           # зупиняється на першому False
```

---

### 5. Генераторні функції — `yield`

```python
# Звичайна функція повертає все одразу
def get_squares(n):
    return [x**2 for x in range(n)]

# Генераторна функція — повертає по одному елементу
def gen_squares(n):
    for x in range(n):
        yield x**2   # зупиняється тут, повертає значення, продовжує при наступному next()

# Використання однаково
for sq in gen_squares(5):
    print(sq)   # 0, 1, 4, 9, 16

# Нескінченний генератор
def count_up(start=0, step=1):
    n = start
    while True:
        yield n
        n += step

counter = count_up(10, 5)
print(next(counter))    # 10
print(next(counter))    # 15
print(next(counter))    # 20

# Практичний приклад — читання файлу по рядках
def read_lines(filepath: str):
    """Генератор для читання великого файлу."""
    with open(filepath) as f:
        for line in f:
            yield line.strip()

for line in read_lines("data.txt"):
    process(line)   # обробляємо по одному рядку, не вантажимо весь файл

# yield from — делегування іншому генератору
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)   # рекурсивно
        else:
            yield item

print(list(flatten([1, [2, [3, 4], 5], 6])))   # [1, 2, 3, 4, 5, 6]
```

---

### 6. `itertools` — потужні ітератори

```python
import itertools

# chain — об'єднати послідовності
combined = list(itertools.chain([1, 2], [3, 4], [5]))
print(combined)   # [1, 2, 3, 4, 5]

# islice — зріз для генератора
first_5 = list(itertools.islice(count_up(), 5))
print(first_5)    # [0, 1, 2, 3, 4]

# product — декартовий добуток (ефективніше за вкладений for)
combos = list(itertools.product([1, 2], ["a", "b"]))
print(combos)     # [(1,'a'), (1,'b'), (2,'a'), (2,'b')]

# combinations та permutations
cards = ["A", "K", "Q"]
print(list(itertools.combinations(cards, 2)))
# [('A','K'), ('A','Q'), ('K','Q')]

print(list(itertools.permutations(cards, 2)))
# [('A','K'), ('A','Q'), ('K','A'), ('K','Q'), ('Q','A'), ('Q','K')]

# groupby — групування (потрібне попереднє сортування!)
data = [("fruits", "apple"), ("vegs", "carrot"), ("fruits", "banana")]
data.sort(key=lambda x: x[0])
for key, group in itertools.groupby(data, key=lambda x: x[0]):
    print(key, list(group))
# fruits [('fruits', 'apple'), ('fruits', 'banana')]
# vegs [('vegs', 'carrot')]
```

---

### Коли використовувати що

| Тип | Синтаксис | Пам'ять | Повторне використання |
|-----|-----------|---------|----------------------|
| List comp | `[x for x in ...]` | Всі елементи | ✅ Так |
| Generator expr | `(x for x in ...)` | О(1) | ❌ Тільки раз |
| Generator func | `def f(): yield x` | О(1) | ✅ Так (новий виклик) |

**Правило:** якщо результат використовуєш більше одного разу — список.  
Якщо тільки один прохід (sum, for, any, all) — генератор.

---

### Типові помилки

```python
# ❌ Надто складний comprehension — нечитабельно
result = [f(x) for x in [g(y) for y in data if h(y)] if p(x)]
# Краще розбити на кілька рядків або використати звичайний цикл

# ❌ Side effects у comprehension
processed = []
result = [processed.append(x) for x in data]   # повертає список None
# ✅ Якщо потрібен side effect — використовуй for

# ❌ Генератор вже вичерпаний
gen = (x for x in range(5))
total = sum(gen)       # 10
items = list(gen)      # []  — порожньо! генератор витрачено

# ✅ Якщо потрібно кілька разів — список або повторно виклик функції

# ❌ Список замість генератора для великих даних
huge = [x**2 for x in range(10_000_000)]  # 400 MB!
total = sum(huge)                          # ще +400 MB

# ✅ Генератор
total = sum(x**2 for x in range(10_000_000))  # кілька KB
```

---

### У реальному проєкті

```python
# Трансформація API-відповіді
def format_users(raw_users: list[dict]) -> list[dict]:
    return [
        {
            "id": u["id"],
            "display_name": f"{u['first_name']} {u['last_name']}",
            "is_premium": u.get("subscription") == "premium",
        }
        for u in raw_users
        if u.get("active")
    ]

# Індексування по полю
def index_by_id(items: list[dict]) -> dict[int, dict]:
    return {item["id"]: item for item in items}

# Підрахунок статистики
from collections import Counter

def top_errors(logs: list[dict], n: int = 10) -> list[tuple]:
    error_counts = Counter(
        log["error_code"]
        for log in logs
        if log["level"] == "ERROR"
    )
    return error_counts.most_common(n)

# Пакетна обробка через генератор (не вантажить усі дані одразу)
def process_users_lazy(user_ids: list[int]):
    return (
        {"id": uid, "processed": True}
        for uid in user_ids
        if uid > 0
    )
```

---

## Що маєш вміти після уроку
- [ ] Написати list / dict / set comprehension із фільтром
- [ ] Пояснити різницю між `[x for x in ...]` і `(x for x in ...)`
- [ ] Написати генераторну функцію з `yield`
- [ ] Використати `sum(x for x in ...)` замість `sum([x for x in ...])`
- [ ] Пояснити що відбудеться якщо використати вичерпаний генератор двічі

---

## Що далі
Виконай завдання з `task.md`. Потім — **Модуль 3: ООП — Класи**.
