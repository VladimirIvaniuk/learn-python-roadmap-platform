# Урок 1 — Списки та кортежі

## Що вивчимо
- Список `list`: створення, індексація, зрізи
- Основні методи: `append`, `insert`, `pop`, `remove`, `sort`, `reverse`
- Вкладені списки та матриці
- Кортеж `tuple`: незмінність, розпакування, `namedtuple`
- Коли list, а коли tuple?
- Корисні функції: `len`, `sum`, `min`, `max`, `sorted`, `reversed`

---

## Теорія

### 1. Список `list` — мутабельна послідовність

```python
# Створення
empty = []
numbers = [1, 2, 3, 4, 5]
mixed = [42, "hello", 3.14, True, None]    # різні типи (не рекомендується)
nested = [[1, 2], [3, 4], [5, 6]]          # вкладений список

# З вбудованих
chars = list("Python")   # ['P', 'y', 't', 'h', 'o', 'n']
zeros = [0] * 5          # [0, 0, 0, 0, 0]
```

**Індексація та зрізи:**
```python
fruits = ["яблуко", "груша", "слива", "манго", "ківі"]
#            0         1        2        3       4
#           -5        -4       -3       -2      -1

print(fruits[0])      # яблуко   (перший)
print(fruits[-1])     # ківі     (останній)
print(fruits[1:3])    # ["груша", "слива"]      від 1 до 3 (не включно)
print(fruits[:2])     # ["яблуко", "груша"]     перші 2
print(fruits[2:])     # ["слива", "манго", "ківі"] від 2 до кінця
print(fruits[::2])    # ["яблуко", "слива", "ківі"] кожен 2-й
print(fruits[::-1])   # зворотній порядок

# Зрізи не кидають IndexError
print(fruits[10:20])  # []  (порожній, не помилка)
```

---

### 2. Основні методи списку

```python
lst = [3, 1, 4, 1, 5, 9, 2, 6]

# Додавання
lst.append(7)           # [3, 1, 4, 1, 5, 9, 2, 6, 7]   — в кінець
lst.insert(0, 0)        # [0, 3, 1, 4, 1, 5, 9, 2, 6, 7] — за індексом
lst.extend([8, 10])     # додає всі елементи іншого списку
lst += [11, 12]         # теж саме через +=

# Видалення
lst.remove(1)           # видаляє перше входження 1
popped = lst.pop()      # видаляє і повертає останній елемент
popped3 = lst.pop(0)    # видаляє і повертає елемент за індексом

# Пошук
fruits = ["яблуко", "груша", "слива", "яблуко"]
print(fruits.index("груша"))   # 1  — індекс першого входження
print(fruits.count("яблуко")) # 2  — кількість входжень
print("манго" in fruits)      # False

# Сортування
nums = [3, 1, 4, 1, 5, 9]
nums.sort()                    # сортує НА МІСЦІ (in-place), повертає None
nums.sort(reverse=True)        # спадання
sorted_nums = sorted(nums)     # ✅ повертає НОВИЙ список, оригінал не змінюється

# Реверс
lst.reverse()                  # на місці
reversed_lst = list(reversed(lst))  # новий список

# Копіювання
copy1 = lst.copy()       # поверхнева копія
copy2 = lst[:]           # теж поверхнева копія
import copy
deep = copy.deepcopy(lst)  # глибока копія (для вкладених структур)

# Очищення
lst.clear()              # []
```

---

### 3. Підводні камені: копіювання та посилання

```python
# ❌ Пастка — не копія, а друге ім'я для того самого списку!
a = [1, 2, 3]
b = a           # b і a вказують на ОДИН список
b.append(4)
print(a)        # [1, 2, 3, 4]  — а теж змінився!

# ✅ Поверхнева копія
b = a.copy()    # або a[:]
b.append(5)
print(a)        # [1, 2, 3, 4]  — а НЕ змінився

# Проблема з вкладеними списками
matrix = [[1, 2], [3, 4]]
copy = matrix.copy()         # поверхнева копія
copy[0].append(99)
print(matrix[0])             # [1, 2, 99]  — вкладений список shared!

import copy
deep_copy = copy.deepcopy(matrix)
deep_copy[0].append(0)
print(matrix[0])             # [1, 2, 99]  — не змінився
```

---

### 4. Вкладені списки та матриці

```python
# Матриця 3×3
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

print(matrix[1][2])     # 6  — рядок 1, стовпець 2

# Обхід матриці
for row in matrix:
    for val in row:
        print(f"{val:3}", end="")
    print()

# Транспонування (рядки ↔ стовпці)
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
# Або через zip:
transposed = list(map(list, zip(*matrix)))
```

---

### 5. Кортеж `tuple` — незмінна послідовність

```python
# Створення
point = (3, 7)
rgb = (255, 128, 0)
single = (42,)        # ОБОВ'ЯЗКОВО кома для кортежу з одного елемента!
empty = ()

# Без дужок теж кортеж (tuple packing)
coordinates = 10, 20, 30

# Розпакування
x, y = point
r, g, b = rgb
first, *rest = (1, 2, 3, 4, 5)  # first=1, rest=[2,3,4,5]

# Іменований кортеж
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 7)
print(p.x, p.y)      # 3  7  (зручніше ніж p[0], p[1])
print(p)             # Point(x=3, y=7)

# Python 3.6+: typing.NamedTuple
from typing import NamedTuple

class User(NamedTuple):
    name: str
    age: int
    role: str = "user"

u = User("Аліса", 25)
print(u.name, u.age, u.role)   # Аліса  25  user
```

---

### 6. List vs Tuple — коли що

| Властивість | `list` | `tuple` |
|-------------|--------|---------|
| Мутабельність | ✅ змінний | ❌ незмінний |
| Синтаксис | `[1, 2, 3]` | `(1, 2, 3)` |
| Швидкість | повільніший | швидший |
| Пам'ять | більше | менше |
| Як ключ dict/set | ❌ не можна | ✅ можна |
| Семантика | "колекція однотипних" | "запис з полями" |

**Коли tuple:**
- Координати: `(x, y)`, `(lat, lon)`
- RGB кольори: `(255, 128, 0)`
- Повернення кількох значень з функції
- Константні дані, що не повинні змінюватись
- Ключі словника

```python
# Функція повертає кілька значень — фактично tuple
def min_max(lst):
    return min(lst), max(lst)

low, high = min_max([3, 1, 4, 1, 5, 9])
print(low, high)   # 1  9
```

---

### 7. Корисні вбудовані функції

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]

print(len(nums))          # 8
print(sum(nums))          # 31
print(min(nums))          # 1
print(max(nums))          # 9
print(sorted(nums))       # [1, 1, 2, 3, 4, 5, 6, 9]  (новий список)
print(list(reversed(nums)))  # [6, 2, 9, 5, 1, 4, 1, 3]

# any і all
print(any(x > 5 for x in nums))   # True (хоч одне > 5)
print(all(x > 0 for x in nums))   # True (всі > 0)
print(all(x > 3 for x in nums))   # False

# enumerate та zip
for i, val in enumerate(nums, start=1):
    print(f"{i:2}. {val}")

# zip — зупиняється на найкоротшому
a = [1, 2, 3, 4]
b = ["a", "b", "c"]
print(list(zip(a, b)))   # [(1,'a'), (2,'b'), (3,'c')] — 4 не включено
```

---

### Типові помилки

```python
# ❌ IndexError — вихід за межі
lst = [1, 2, 3]
print(lst[5])       # IndexError: list index out of range
print(lst[-4])      # IndexError

# ❌ sort() vs sorted()
lst = [3, 1, 2]
result = lst.sort()  # result = None! sort() нічого не повертає
print(result)        # None — типова помилка!

# ✅
sorted_lst = sorted(lst)  # повертає новий список
lst.sort()                # змінює lst, повертає None

# ❌ Множення вкладених списків — shared references!
matrix = [[0] * 3] * 3
matrix[0][0] = 1
print(matrix)   # [[1, 0, 0], [1, 0, 0], [1, 0, 0]] — всі рядки змінились!

# ✅ Правильно
matrix = [[0] * 3 for _ in range(3)]
matrix[0][0] = 1
print(matrix)   # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
```

---

### У реальному проєкті

```python
# Пагінація
def get_page(items: list, page: int, per_page: int = 20) -> list:
    start = (page - 1) * per_page
    return items[start:start + per_page]

# Безпечне отримання останнього елемента
def last_or_default(lst: list, default=None):
    return lst[-1] if lst else default

# Batch обробка
def process_in_batches(items: list, batch_size: int = 100):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        yield batch   # yield вивчимо пізніше

# Фільтрація та сортування
users = [{"name": "A", "age": 30, "active": True}, ...]
active = [u for u in users if u["active"]]
by_age = sorted(active, key=lambda u: u["age"])
```

---

## Що маєш вміти після уроку
- [ ] Створити список, отримати елемент за індексом, зріз
- [ ] Додати/видалити елемент через `append`, `insert`, `pop`, `remove`
- [ ] Правильно скопіювати список (не через `=`)
- [ ] Відсортувати список та поверхнево розуміти стабільність сортування
- [ ] Розпакувати кортеж та створити `namedtuple`
- [ ] Пояснити різницю `sort()` (in-place) та `sorted()` (новий список)

---

## Що далі
Виконай завдання з `task.md`. Потім — **Урок 2: Словники та множини**.
