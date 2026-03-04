# Урок 3 — Умови та цикли

## Що вивчимо
- `if / elif / else` — умовні конструкції та вкладення
- Тернарний оператор (conditional expression)
- `for` — цикл по послідовності, `range()`
- `while` — цикл з умовою
- `break`, `continue`, `else` у циклах
- `enumerate()`, `zip()` — корисні вбудовані функції

---

## Теорія

### 1. Умовні конструкції — `if / elif / else`

```python
temperature = 22

if temperature > 30:
    print("Спекотно 🔥")
elif temperature > 20:
    print("Тепло ☀️")       # ← виконається це
elif temperature > 10:
    print("Прохолодно")
else:
    print("Холодно 🥶")
```

**Правила:**
- Блок коду визначається **відступом** (4 пробіли, ніяких Tab!)
- `elif` і `else` — необов'язкові
- Умова перевіряється зверху вниз, виконується перший True

**Вкладені умови:**
```python
age = 20
has_id = True

if age >= 18:
    if has_id:
        print("Доступ дозволено ✅")
    else:
        print("Покажіть посвідчення")
else:
    print("Недостатньо років")

# Те саме, коротше (and):
if age >= 18 and has_id:
    print("Доступ дозволено ✅")
```

**Тернарний оператор:**
```python
# <значення_якщо_True> if <умова> else <значення_якщо_False>
status = "дорослий" if age >= 18 else "неповнолітній"
print(status)   # дорослий

# Корисно в f-рядках
print(f"Користувач {'активний' if is_active else 'заблокований'}")

# Вибір значення з кількох варіантів
label = "відмінно" if score >= 90 else "добре" if score >= 70 else "задовільно"
```

**Порівняння:**
```python
x = 5

print(x == 5)     # True  — рівно
print(x != 5)     # False — не рівно
print(x > 3)      # True  — більше
print(x < 3)      # False — менше
print(x >= 5)     # True  — більше або рівно
print(x <= 4)     # False — менше або рівно

# Ланцюгові порівняння (унікально для Python)
print(0 < x < 10)           # True  — x між 0 і 10
print(1 <= x <= 5)           # True
print(10 < x < 20)           # False

# Перевірка приналежності
fruits = ["яблуко", "груша"]
print("груша" in fruits)     # True
print("манго" not in fruits) # True

# Перевірка ідентичності (це той самий об'єкт у пам'яті)
a = [1, 2, 3]
b = a
c = [1, 2, 3]
print(a is b)   # True  — один об'єкт
print(a is c)   # False — однакові значення, але різні об'єкти
print(a == c)   # True  — однакові значення
```

---

### 2. `match/case` — структурний pattern matching (Python 3.10+)

```python
status_code = 404

match status_code:
    case 200:
        print("OK")
    case 404:
        print("Not Found")      # ← виконається це
    case 500:
        print("Server Error")
    case _:
        print(f"Невідомий код: {status_code}")

# Збіг з умовою (guard)
match status_code:
    case code if 200 <= code < 300:
        print("Успіх")
    case code if 400 <= code < 500:
        print("Помилка клієнта")    # ← виконається це
    case _:
        print("Інший код")
```

---

### 3. Цикл `for`

`for` проходить по **будь-якій послідовності** (список, рядок, словник, файл...).

```python
# По списку
fruits = ["яблуко", "груша", "слива"]
for fruit in fruits:
    print(f"Фрукт: {fruit}")

# По рядку (символ за символом)
for char in "Python":
    print(char, end=" ")   # P y t h o n

# По range()
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 10):      # 2, 3, ..., 9
    print(i)

for i in range(0, 20, 3):   # 0, 3, 6, 9, 12, 15, 18
    print(i)

for i in range(10, 0, -1):  # 10, 9, ..., 1 — зворотний порядок
    print(i)
```

**`enumerate()` — індекс + значення:**
```python
fruits = ["яблуко", "груша", "слива"]

# Без enumerate — погано
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# З enumerate — pythonic ✅
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
# 0: яблуко
# 1: груша
# 2: слива

# Починати з іншого числа
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")
# 1. яблуко
# 2. груша
```

**`zip()` — паралельний обхід:**
```python
names = ["Аліса", "Боб", "Катя"]
scores = [95, 82, 88]
grades = ["A", "B", "A"]

for name, score, grade in zip(names, scores, grades):
    print(f"{name}: {score} балів ({grade})")
# Аліса: 95 балів (A)
# Боб: 82 балів (B)
# Катя: 88 балів (A)
```

---

### 4. Цикл `while`

`while` виконується, поки умова True.

```python
count = 0
while count < 5:
    print(count)
    count += 1

# Читання введення поки не правильне
# Local-версія (термінал)
# while True:
#     answer = input("Введи 'так' або 'ні': ").lower()
#     if answer in ("так", "ні"):
#         break
#     print("Невірна відповідь, спробуй ще раз")

# Platform-версія (веб-ранер): симулюємо введення
test_answers = ["можливо", "так"]
idx = 0
while True:
    answer = test_answers[idx].lower()
    idx += 1
    if answer in ("так", "ні"):
        break
    print("Невірна відповідь, спробуй ще раз")

print(f"Ти обрав: {answer}")
```

**Різниця for vs while:**
| `for` | `while` |
|-------|---------|
| Коли знаєш кількість ітерацій | Коли умова зупинки невідома |
| По послідовності (список, рядок) | Очікування події / введення |
| Переважно безпечніший | Ризик нескінченного циклу |

---

### 5. `break`, `continue`, `else`

```python
# break — виходить з циклу
numbers = [3, 7, 2, 9, 4]
for num in numbers:
    if num == 9:
        print(f"Знайшли {num}!")
        break       # зупиняємось
else:
    print("9 не знайдено")
# Виводить: Знайшли 9!

# continue — пропускає ітерацію
for i in range(10):
    if i % 2 == 0:
        continue    # пропускаємо парні
    print(i, end=" ")   # 1 3 5 7 9

# else у циклі — виконується якщо не було break
for num in [2, 4, 6, 8]:
    if num % 2 != 0:
        print("Знайшли непарне!")
        break
else:
    print("Всі числа парні ✅")     # ← виконається
```

---

### 6. Вкладені цикли та `_` як ігнорована змінна

```python
# Таблиця множення
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i}×{j}={i*j}", end="  ")
    print()     # новий рядок

# _ — коли значення не потрібне
for _ in range(3):
    print("Привіт!")   # виводить 3 рази

# Дістати останній елемент
_, _, last = (1, 2, 3)
print(last)    # 3
```

---

### Типові помилки

```python
# ❌ Нескінченний цикл — забули змінювати умову
count = 0
while count < 5:
    print(count)
    # count += 1 ← ЗАБУЛИ! Ctrl+C для зупинки

# ❌ Змінюємо список під час ітерації
items = [1, 2, 3, 4, 5]
for item in items:
    if item % 2 == 0:
        items.remove(item)  # непередбачувана поведінка!

# ✅ Правильно — ітеруємо по копії
for item in items[:]:
    if item % 2 == 0:
        items.remove(item)

# ✅ Або фільтрація
items = [item for item in items if item % 2 != 0]

# ❌ range(len(list)) замість enumerate
for i in range(len(fruits)):
    print(fruits[i])        # некрасиво

for fruit in fruits:
    print(fruit)            # ✅ краще

for i, fruit in enumerate(fruits):  # ✅ якщо потрібен індекс
    print(i, fruit)
```

---

### У реальному проєкті

```python
# FastAPI: валідація статус кодів
def handle_response(status: int) -> str:
    match status:
        case 200 | 201:
            return "success"
        case code if 400 <= code < 500:
            return "client_error"
        case code if 500 <= code < 600:
            return "server_error"
        case _:
            return "unknown"

# Обробка пагінованих даних з API
def get_all_users(client) -> list:
    all_users = []
    page = 1
    while True:
        batch = client.get_users(page=page, limit=100)
        if not batch:
            break
        all_users.extend(batch)
        page += 1
    return all_users

# Знаходження першого активного адміна
def find_admin(users: list) -> dict | None:
    for user in users:
        if user["role"] == "admin" and user["is_active"]:
            return user
    return None     # явно повертаємо None якщо не знайдено
```

---

## Що маєш вміти після уроку
- [ ] Написати `if/elif/else` для класифікації значення (наприклад, оцінки)
- [ ] Використати тернарний оператор замість if/else там, де це читабельно
- [ ] Пройти по списку через `for` і вибрати елементи за умовою
- [ ] Використати `enumerate()` та `zip()`
- [ ] Написати `while` з умовою виходу та з `break`
- [ ] Пояснити коли спрацьовує `else` у циклі

---

## Що далі
Виконай завдання з `task.md`. Потім — **Урок 4: Функції**.
