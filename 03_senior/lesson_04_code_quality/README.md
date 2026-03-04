# Урок 4 — Якість коду: mypy, ruff, pre-commit

## Що вивчимо
- `mypy` — статична перевірка типів
- `ruff` — linter + formatter (замінює flake8, isort, black, pylint)
- `pre-commit` — автоматичні перевірки перед кожним комітом
- Метрики якості коду: цикломатична складність, зв'язність
- Code review: що перевіряти, як давати фідбек
- Рефакторинг: безпечні кроки

---

## Теорія

### 1. mypy — статична типізація

```python
# Без типів — Python дозволяє все, помилки тільки в runtime
def process(data):
    return data.upper()

process(42)    # AttributeError в runtime!

# З типами + mypy — помилка знайдена до запуску
def process(data: str) -> str:
    return data.upper()

# mypy: error: Argument 1 to "process" has incompatible type "int"; expected "str"
process(42)

# ── Складніші типи ─────────────────────────────────────────────────────────────
from typing import TypeVar, Generic, Callable, overload

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# Generic клас
class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def peek(self) -> T | None:
        return self._items[-1] if self._items else None

s: Stack[int] = Stack()
s.push(1)
s.push("hello")   # mypy: error! Expected int, got str

# overload — кілька сигнатур
from typing import overload

@overload
def double(x: int) -> int: ...
@overload
def double(x: str) -> str: ...

def double(x: int | str) -> int | str:
    return x * 2

reveal_type(double(5))      # mypy: int
reveal_type(double("hi"))   # mypy: str

# TypedDict — типізовані словники
from typing import TypedDict, Required, NotRequired

class UserDict(TypedDict):
    id: int
    username: str
    email: str
    role: NotRequired[str]   # необов'язкове

def get_username(user: UserDict) -> str:
    return user["username"]

# Protocol — structural subtyping (duck typing з типами)
from typing import Protocol, runtime_checkable

@runtime_checkable
class Hashable(Protocol):
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...
```

**Конфігурація mypy:**
```ini
# mypy.ini або pyproject.toml [tool.mypy]
[mypy]
python_version = 3.12
strict = True
warn_return_any = True
warn_unused_configs = True
ignore_missing_imports = True

# Виключення для конкретних пакетів
[mypy-sqlalchemy.*]
ignore_missing_imports = True
```

---

### 2. ruff — сучасний linter

```bash
pip install ruff

# Перевірка
ruff check .
ruff check src/

# Автоматичне виправлення
ruff check --fix .

# Форматування (замінює black)
ruff format .
ruff format --check .   # тільки перевірити

# Окремі правила
ruff check --select E,F,I,N,W .   # помилки, flake8, isort, naming, warnings
ruff check --ignore E501 .         # ігнорувати довгі рядки
```

**Конфігурація:**
```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
]
ignore = ["E501"]  # довгі рядки — рішення форматера

[tool.ruff.lint.isort]
known-first-party = ["myapp"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

---

### 3. pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace      # видалити пробіли в кінці рядків
      - id: end-of-file-fixer        # файл має закінчуватись \n
      - id: check-yaml               # валідний YAML
      - id: check-merge-conflict     # немає маркерів merge конфлікту
      - id: check-added-large-files  # забороняє великі файли
        args: ['--maxkb=500']

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff           # linting
        args: [--fix]
      - id: ruff-format    # formatting

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, pydantic]
```

```bash
# Встановлення
pip install pre-commit
pre-commit install     # реєструємо git hook

# Запуск вручну на всіх файлах
pre-commit run --all-files

# Пропустити (не рекомендовано)
git commit --no-verify
```

---

### 4. Метрики якості коду

**Цикломатична складність (Cyclomatic Complexity):**
```python
# Складність = кількість незалежних шляхів через код
# 1-10: простий код
# 11-20: складний, варто рефакторити
# 21+: дуже складний, обов'язково рефакторити

# ❌ Висока складність (CC ~8)
def process_order(order):
    if order.status == "pending":
        if order.payment_method == "card":
            if order.amount > 1000:
                if order.user.is_premium:
                    discount = 0.1
                else:
                    discount = 0.05
            else:
                discount = 0
        elif order.payment_method == "cash":
            discount = 0.02
        else:
            discount = 0
    elif order.status == "paid":
        pass

# ✅ Рефакторинг: декомпозиція
def get_discount(order) -> float:
    if order.payment_method == "cash":
        return 0.02
    if order.payment_method != "card":
        return 0.0
    if order.amount <= 1000:
        return 0.0
    return 0.1 if order.user.is_premium else 0.05

def process_order(order):
    if order.status == "pending":
        order.discount = get_discount(order)
    # ...
```

**Принципи читабельного коду:**
```python
# 1. Виразні імена — пиши як документацію
# ❌
def calc(x, lst, f):
    return [f(i) for i in lst if i > x]

# ✅
def filter_and_transform(threshold: float, items: list, transform: Callable) -> list:
    return [transform(item) for item in items if item > threshold]

# 2. Ранній вихід (Early Return) — зменшує вкладеність
# ❌ Pyramid of Doom
def validate_user(user):
    if user:
        if user.is_active:
            if user.email:
                if "@" in user.email:
                    return True
    return False

# ✅ Guard Clauses
def validate_user(user) -> bool:
    if not user:
        return False
    if not user.is_active:
        return False
    if not user.email or "@" not in user.email:
        return False
    return True

# 3. Короткі функції — одна задача
# Якщо функція не вміщається на екрані — розбий її

# 4. Уникай магічних чисел
BCRYPT_ROUNDS = 12           # ✅ назва пояснює що це
hash = bcrypt.hash(pw, 12)   # ❌ що таке 12?
```

---

### 5. Code Review — що перевіряти

```
Checklist для code review:
├── Correctness
│   ├── Чи вирішує задачу?
│   ├── Edge cases: None, порожній список, від'ємні числа?
│   └── Concurrent доступ до shared state?
├── Security
│   ├── SQL injection? (raw queries)
│   ├── XSS? (вивід user input в HTML)
│   └── Secrets в коді?
├── Performance
│   ├── N+1 запити до БД?
│   ├── Завантажує всі дані замість пагінації?
│   └── Дорога операція в циклі?
├── Readability
│   ├── Назви змінних зрозумілі?
│   ├── Складні місця мають коментарі?
│   └── Функція робить тільки одне?
└── Tests
    ├── Є тести для нового коду?
    └── Happy path + edge cases покриті?
```

**Як давати фідбек:**
```
# ✅ Конструктивно — пояснюй і пропонуй
"Можливо варто використати `get()` замість прямого доступу до словника [line 42],
це запобіжить KeyError якщо ключ відсутній. Наприклад: `data.get('key', default_value)`"

# ❌ Агресивно або без причини
"Це неправильно."
"Погано написано."

# Рівні важливості у коментарях
# nit: незначна дрібниця (необов'язково виправляти)
# suggestion: пропозиція (бажано але не обов'язково)
# blocking: обов'язково виправити перед мержем
```

---

## Що маєш вміти після уроку
- [ ] Налаштувати mypy strict і виправити всі помилки типів
- [ ] Налаштувати ruff із відповідними правилами для проєкту
- [ ] Встановити pre-commit та переконатись що він блокує погані коміти
- [ ] Провести code review чужого PR за checklisом
- [ ] Пояснити цикломатичну складність і рефакторити функцію CC>10

---

## Що далі
`task.md`. Потім — **Урок 5: Безпека**.
