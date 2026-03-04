# Урок 2 — Словники та множини

## Що вивчимо
- Словник `dict`: створення, доступ, оновлення, видалення
- Методи: `keys()`, `values()`, `items()`, `get()`, `setdefault()`, `update()`
- Ітерація по словнику
- Вкладені словники
- Множина `set`: унікальні елементи, операції (об'єднання, перетин, різниця)
- `frozenset` — незмінна множина
- `defaultdict` та `Counter` з `collections`

---

## Теорія

### 1. Словник `dict` — ключ → значення

```python
# Створення
empty = {}
person = {"name": "Аліса", "age": 25, "city": "Київ"}

# З dict()
person2 = dict(name="Боб", age=30)

# З пар ключ-значення
pairs = [("a", 1), ("b", 2), ("c", 3)]
d = dict(pairs)   # {"a": 1, "b": 2, "c": 3}

# Ключі: незмінні типи (str, int, tuple — ✅, list — ❌)
d = {1: "one", (0, 0): "origin", "key": [1, 2, 3]}
```

**Доступ до значень:**
```python
person = {"name": "Аліса", "age": 25, "email": None}

# Прямий доступ — кидає KeyError якщо ключ відсутній
print(person["name"])    # Аліса
# print(person["phone"]) # KeyError!

# .get() — безпечний доступ
print(person.get("phone"))          # None  (не кидає помилку)
print(person.get("phone", "N/A"))   # N/A   (значення за замовчуванням)

# in — перевірка наявності ключа
print("age" in person)              # True
print("phone" in person)            # False
```

---

### 2. Зміна словника

```python
config = {"debug": True, "port": 8000, "host": "localhost"}

# Додавання та оновлення
config["version"] = "1.0"           # новий ключ
config["port"] = 9000               # зміна існуючого

# update() — злиття
config.update({"debug": False, "workers": 4})
config.update(debug=True, timeout=30)   # через keyword args

# Злиття (Python 3.9+)
defaults = {"port": 8000, "host": "localhost"}
overrides = {"port": 9000, "debug": True}
merged = defaults | overrides        # {"port": 9000, "host": "localhost", "debug": True}
merged = {**defaults, **overrides}   # теж саме (Python 3.5+)

# Видалення
del config["version"]                # кидає KeyError якщо немає
val = config.pop("workers")          # видаляє і повертає значення
val = config.pop("missing", None)    # безпечно, повертає None
config.clear()                       # очищає весь словник

# setdefault — встановлює якщо ключ відсутній
cache = {}
cache.setdefault("hits", 0)
cache["hits"] += 1
print(cache)    # {"hits": 1}
```

---

### 3. Ітерація по словнику

```python
grades = {"Аліса": 92, "Боб": 78, "Катя": 88}

# По ключах (за замовчуванням)
for name in grades:
    print(name)

# По значеннях
for score in grades.values():
    print(score)

# По парах (найчастіше)
for name, score in grades.items():
    label = "✅" if score >= 80 else "⚠️"
    print(f"{label} {name}: {score}")

# Словник завжди зберігає порядок (Python 3.7+)
# Перший доданий — перший при ітерації
```

**Корисні операції:**
```python
# Словникові методи
grades = {"Аліса": 92, "Боб": 78, "Катя": 88}

keys = list(grades.keys())         # ["Аліса", "Боб", "Катя"]
values = list(grades.values())     # [92, 78, 88]
items = list(grades.items())       # [("Аліса", 92), ("Боб", 78), ("Катя", 88)]

# Знайти ключ з максимальним значенням
best_student = max(grades, key=grades.get)
print(best_student)    # Аліса

# Відфільтрувати
good_grades = {k: v for k, v in grades.items() if v >= 80}
print(good_grades)     # {"Аліса": 92, "Катя": 88}
```

---

### 4. Вкладені словники

```python
# "База даних" користувачів
users_db = {
    1: {"name": "Аліса", "role": "admin",  "active": True},
    2: {"name": "Боб",   "role": "user",   "active": False},
    3: {"name": "Катя",  "role": "editor", "active": True},
}

# Доступ
print(users_db[1]["name"])           # Аліса
print(users_db[2].get("email", ""))  # "" (email відсутній)

# Безпечний доступ по ланцюжку
config = {"database": {"host": "localhost", "port": 5432}}
host = config.get("database", {}).get("host", "unknown")
print(host)   # localhost

# Оновлення вкладеного
users_db[2]["active"] = True
users_db[4] = {"name": "Денис", "role": "user", "active": True}

# Знайти всіх активних адмінів
admins = [u["name"] for u in users_db.values() if u["active"] and u["role"] == "admin"]
```

---

### 5. Множина `set` — унікальні елементи

```python
# Створення
empty = set()              # НЕ {} — це порожній dict!
numbers = {1, 2, 3, 4, 5}
from_list = set([1, 2, 2, 3, 3, 3])   # {1, 2, 3}  дублікати прибрані

# Порядок НЕ гарантований!
print(set("hello"))    # {'h', 'e', 'l', 'o'}  (l тільки раз)

# Операції
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)          # {1, 2, 3, 4, 5, 6}  — об'єднання (union)
print(a & b)          # {3, 4}              — перетин (intersection)
print(a - b)          # {1, 2}              — різниця (difference)
print(a ^ b)          # {1, 2, 5, 6}        — симетрична різниця (XOR)

# Перевірки
print(3 in a)          # True
print({1, 2} <= a)     # True   — підмножина (subset)
print({1, 2} < a)      # True   — власна підмножина
print(a >= {1, 2})     # True   — надмножина (superset)
print(a.isdisjoint(b)) # False  — чи немає спільних елементів

# Зміна
a.add(10)
a.remove(1)         # KeyError якщо немає
a.discard(99)       # безпечно, немає помилки
popped = a.pop()    # видаляє довільний елемент
a.clear()
```

---

### 6. Застосування `set` — прибрати дублікати

```python
# ✅ Найшвидший спосіб прибрати дублікати (порядок може змінитись)
words = ["the", "quick", "the", "fox", "quick", "runs"]
unique = list(set(words))

# Якщо потрібен порядок
seen = set()
unique_ordered = []
for w in words:
    if w not in seen:
        unique_ordered.append(w)
        seen.add(w)

# Або через dict.fromkeys (зберігає порядок, Python 3.7+)
unique_ordered = list(dict.fromkeys(words))
print(unique_ordered)   # ["the", "quick", "fox", "runs"]

# Перевірка на унікальність
def has_duplicates(lst):
    return len(lst) != len(set(lst))

# Перетин для пошуку спільних елементів
enrolled_math = {"Аліса", "Боб", "Катя", "Денис"}
enrolled_python = {"Катя", "Денис", "Олег"}
both_courses = enrolled_math & enrolled_python
only_math = enrolled_math - enrolled_python
```

---

### 7. `frozenset` — незмінна множина

```python
# Можна використовувати як ключ словника або елемент set
fs = frozenset({1, 2, 3})
d = {fs: "значення"}   # ✅

allowed_roles = frozenset({"admin", "editor", "moderator"})
if user_role in allowed_roles:
    print("Доступ дозволено")
```

---

### 8. `defaultdict` та `Counter`

```python
from collections import defaultdict, Counter

# defaultdict — не кидає KeyError, створює дефолтне значення
word_count = defaultdict(int)   # дефолт = 0
for word in "the quick brown fox the fox".split():
    word_count[word] += 1       # не потрібен .get() або setdefault

print(dict(word_count))   # {'the': 2, 'quick': 1, 'brown': 1, 'fox': 2}

# Групування
from collections import defaultdict
grouped = defaultdict(list)
for item in [("fruits", "apple"), ("vegs", "carrot"), ("fruits", "banana")]:
    grouped[item[0]].append(item[1])
print(dict(grouped))   # {'fruits': ['apple', 'banana'], 'vegs': ['carrot']}

# Counter — підрахунок частот
text = "abracadabra"
freq = Counter(text)
print(freq)                    # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
print(freq.most_common(3))     # [('a', 5), ('b', 2), ('r', 2)]

words = "the quick brown fox the fox the".split()
word_freq = Counter(words)
print(word_freq.most_common(2))  # [('the', 3), ('fox', 2)]
```

---

### Типові помилки

```python
# ❌ Порожня множина через {}
empty = {}       # це DICT, не set!
empty = set()    # ✅ порожня множина

# ❌ KeyError при прямому доступі
d = {"a": 1}
print(d["b"])    # KeyError: 'b'
print(d.get("b", 0))  # ✅ безпечно

# ❌ Зміна dict під час ітерації
d = {"a": 1, "b": 2, "c": 3}
for k in d:
    if k == "a":
        del d[k]    # RuntimeError: dictionary changed size during iteration

# ✅ Ітеруємо по копії ключів
for k in list(d.keys()):
    if k == "a":
        del d[k]

# ❌ set не зберігає порядок — не сортуй не очікуй
s = {3, 1, 2}
print(s)   # {1, 2, 3}  або {3, 1, 2} — не визначено!
```

---

### У реальному проєкті

```python
# Кешування (мемоізація)
cache: dict[str, any] = {}

def get_user(user_id: int) -> dict:
    key = f"user:{user_id}"
    if key not in cache:
        cache[key] = db.query(User).get(user_id)
    return cache[key]

# Агрегація статистики
from collections import Counter, defaultdict

def analyze_logs(log_entries: list[dict]) -> dict:
    status_counts = Counter(e["status"] for e in log_entries)
    errors_by_path = defaultdict(list)
    for e in log_entries:
        if e["status"] >= 400:
            errors_by_path[e["path"]].append(e["message"])
    return {"status_counts": dict(status_counts), "errors": dict(errors_by_path)}

# Дедублікація ID
def get_unique_user_ids(events: list[dict]) -> set[int]:
    return {e["user_id"] for e in events if e.get("user_id")}
```

---

## Що маєш вміти після уроку
- [ ] Безпечно отримати значення через `.get()` з дефолтом
- [ ] Ітерувати по `.items()` та обробляти вкладені словники
- [ ] Виконати всі 4 операції з множинами (`|`, `&`, `-`, `^`)
- [ ] Прибрати дублікати зі списку через `set` (зі збереженням порядку)
- [ ] Використати `Counter` для підрахунку частот
- [ ] Пояснити чому `{}` — це dict, а не set

---

## Що далі
Виконай завдання з `task.md`. Потім — **Урок 3: Comprehensions**.
