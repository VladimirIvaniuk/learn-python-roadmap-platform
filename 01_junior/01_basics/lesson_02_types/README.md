# Урок 2 — Типи даних та операції

## Що вивчимо
- Чотири основні типи: `int`, `float`, `str`, `bool`
- Арифметичні операції та пріоритет
- Рядкові методи: `upper/lower`, `strip`, `split/join`, `replace`, `find`
- Логічні оператори: `and`, `or`, `not`
- Перевірка та перетворення типів: `type()`, `int()`, `str()`, `float()`
- `None` — відсутність значення

---

## Теорія

### 1. Числові типи: `int` та `float`

```python
# int — цілі числа (будь-яка довжина!)
age = 25
year = 2026
big = 1_000_000_000     # підкреслення для читабельності
negative = -42
binary = 0b1010          # двійкове = 10
octal = 0o17             # вісімкове = 15
hexadecimal = 0xFF       # шістнадцяткове = 255

# float — числа з плаваючою крапкою
price = 19.99
pi = 3.14159265358979
scientific = 1.5e10      # 1.5 × 10^10 = 15000000000.0
```

**Арифметичні операції:**
```python
a, b = 17, 5

print(a + b)    # 22  — додавання
print(a - b)    # 12  — віднімання
print(a * b)    # 85  — множення
print(a / b)    # 3.4 — ділення (завжди float!)
print(a // b)   # 3   — цілочисельне ділення (floor division)
print(a % b)    # 2   — остача від ділення (modulo)
print(a ** b)   # 1419857 — піднесення до степеня

# Пріоритет: ** > * / // % > + -
print(2 + 3 * 4)     # 14, а не 20
print((2 + 3) * 4)   # 20
```

**Скорочений запис:**
```python
x = 10
x += 5    # x = x + 5  → 15
x -= 3    # x = x - 3  → 12
x *= 2    # x = x * 2  → 24
x //= 5   # x = x // 5 → 4
x **= 3   # x = x ** 3 → 64
```

**Вбудовані математичні функції:**
```python
print(abs(-7))         # 7   — модуль
print(round(3.567, 2)) # 3.57 — округлення
print(round(3.567))    # 4
print(max(3, 7, 2))    # 7
print(min(3, 7, 2))    # 2
print(sum([1, 2, 3]))  # 6
print(pow(2, 10))      # 1024

import math
print(math.sqrt(16))   # 4.0
print(math.ceil(3.1))  # 4  — вгору
print(math.floor(3.9)) # 3  — вниз
print(math.pi)         # 3.141592653589793
print(math.log(100, 10))  # 2.0
```

**Проблема float-точності:**
```python
print(0.1 + 0.2)         # 0.30000000000000004 — не 0.3!
print(0.1 + 0.2 == 0.3)  # False

# Рішення 1: round()
print(round(0.1 + 0.2, 10) == 0.3)  # True

# Рішення 2: decimal для фінансових розрахунків
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))  # 0.3 — точно!
```

---

### 2. Рядки — `str`

Рядок — послідовність символів у лапках (одинарних або подвійних — однаково).

```python
s1 = "Привіт"
s2 = 'World'
s3 = "He said 'hello'"   # одинарні всередині подвійних
s4 = 'She said "hello"'  # подвійні всередині одинарних
s5 = """
Багаторядковий
рядок
"""
```

**Операції з рядками:**
```python
first = "Hello"
second = "World"

print(first + " " + second)    # Hello World — конкатенація
print(first * 3)                # HelloHelloHello — повторення
print(len(first))               # 5 — довжина
print(first[0])                 # H  — перший символ
print(first[-1])                # o  — останній символ
print(first[1:4])               # ell — зріз [від:до]
print(first[::2])               # Hlo — крок 2
print(first[::-1])              # olleH — реверс
```

**Основні методи рядків:**
```python
text = "  Привіт, Світе!  "

# Регістр
print(text.upper())           # "  ПРИВІТ, СВІТЕ!  "
print(text.lower())           # "  привіт, світе!  "
print(text.title())           # "  Привіт, Світе!  "
print(text.swapcase())        # "  пРИВІТ, сВІТЕ!  "

# Обрізка пробілів
print(text.strip())           # "Привіт, Світе!"
print(text.lstrip())          # "Привіт, Світе!  "
print(text.rstrip())          # "  Привіт, Світе!"

# Пошук і заміна
s = "banana"
print(s.find("an"))           # 1  — індекс першого входження (-1 якщо немає)
print(s.count("a"))           # 3  — кількість входжень
print(s.replace("a", "o"))    # "bonono"
print(s.startswith("ban"))    # True
print(s.endswith("na"))       # True
print("ana" in s)             # True — перевірка входження

# Розбивання та об'єднання
csv = "яблуко,груша,слива"
fruits = csv.split(",")       # ["яблуко", "груша", "слива"]
print(fruits)

words = ["Python", "це", "круто"]
print(" ".join(words))        # "Python це круто"
print("-".join(words))        # "Python-це-круто"

# Перевірки
print("123".isdigit())        # True
print("abc".isalpha())        # True
print("abc123".isalnum())     # True
print("  \t\n".isspace())     # True

# Вирівнювання
print("hi".center(10))        # "    hi    "
print("hi".ljust(10, "."))    # "hi........"
print("hi".rjust(10, "0"))    # "00000000hi"
```

---

### 3. Логічний тип — `bool`

```python
is_active = True
is_blocked = False

# Порівняння повертають bool
print(5 > 3)       # True
print(5 == 5)      # True
print(5 != 3)      # True
print(5 >= 6)      # False
```

**Логічні оператори:**
```python
age = 25
has_ticket = True

# and — обидві умови мають бути True
print(age >= 18 and has_ticket)   # True

# or — хоч одна умова True
print(age < 18 or has_ticket)     # True

# not — інвертує
print(not is_blocked)             # True (якщо is_blocked = False)

# Пріоритет: not > and > or
print(True or False and False)    # True (and обчислюється першим)
print((True or False) and False)  # False
```

**Truthy і Falsy значення:**
```python
# Falsy (вважаються False в умовах):
# False, None, 0, 0.0, "", [], {}, set()

# Truthy — усе решта

if "":       # Falsy — не виконається
    print("рядок не порожній")

if "hello":  # Truthy — виконається
    print("рядок не порожній")  # → рядок не порожній

if 0:        # Falsy
    pass

if []:       # Falsy — порожній список
    pass

# Практика
users = []
if not users:
    print("Список користувачів порожній")
```

---

### 4. `None` — відсутність значення

```python
result = None   # змінна оголошена, але значення ще немає

# Перевірка на None — тільки через is/is not
if result is None:
    print("Результату ще немає")

if result is not None:
    print(f"Результат: {result}")

# Функція без return повертає None
def do_nothing():
    pass

x = do_nothing()
print(x)         # None
print(x is None) # True
```

---

### 5. Перетворення типів

```python
# str → int, float
age = int("25")          # 25
price = float("19.99")   # 19.99
binary_val = int("1010", 2)  # 10 (двійкове)
hex_val = int("FF", 16)      # 255 (шістнадцяткове)

# int, float → str
s = str(42)         # "42"
s = str(3.14)       # "3.14"

# Перетворення типів може кинути виключення
try:
    x = int("abc")  # ValueError!
except ValueError:
    print("Не вдалося конвертувати")

# type() — перевірка типу
print(type(42))       # <class 'int'>
print(type("hello"))  # <class 'str'>
print(type(True))     # <class 'bool'>

# isinstance() — кращий спосіб перевірки
print(isinstance(42, int))        # True
print(isinstance(42, (int, float)))# True — перевірка на кілька типів
print(isinstance(True, int))      # True! — bool є підкласом int
```

---

### Типові помилки

```python
# ❌ Ділення на нуль
x = 10 / 0    # ZeroDivisionError!

# ❌ Конкатенація str + non-str
print("Вік: " + 25)   # TypeError

# ❌ Порівняння замість присвоєння
x = 5
if x = 5:   # SyntaxError! (у Python це заборонено, в C/JS — ні)
    pass

# ❌ Перевірка на None через ==
if result == None:   # працює, але не pythonic
    pass
if result is None:   # ✅ правильно

# ❌ Переповнення float
import sys
big = sys.float_info.max
print(big * 2)     # inf — не помилка, але несподівано

# ❌ Плутанина int і float у ділення
print(7 / 2)    # 3.5  (float)
print(7 // 2)   # 3    (int — цілочисельне!)
```

---

### У реальному проєкті

```python
# Валідація типів у FastAPI через Pydantic
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str           # автоматично перевіряє тип
    age: int                # і конвертує якщо можливо
    balance: float = 0.0   # значення за замовчуванням
    is_active: bool = True

# При некоректних даних Pydantic кине ValidationError
# — до твого коду вони не доберуться

# Типові операції у бізнес-логіці
def calculate_discount(price: float, discount_percent: float) -> float:
    """Повертає ціну після знижки."""
    if not 0 <= discount_percent <= 100:
        raise ValueError(f"Знижка має бути 0-100%, отримано {discount_percent}")
    return round(price * (1 - discount_percent / 100), 2)
```

---

## Що маєш вміти після уроку
- [ ] Виконати всі арифметичні операції, включаючи `//`, `%`, `**`
- [ ] Використати 5+ методів рядків (`upper`, `strip`, `split`, `replace`, `find`)
- [ ] Пояснити чому `0.1 + 0.2 != 0.3` і як це виправити
- [ ] Розрізняти truthy / falsy значення в умові `if`
- [ ] Безпечно конвертувати типи через `int()`, `float()`, `str()`
- [ ] Перевіряти тип через `isinstance()` (не `type() ==`)

---

## Що далі
Виконай завдання з `task.md`. Потім — **Урок 3: Умови та цикли**.
