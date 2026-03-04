"""
Розв'язки — Урок 2: Типи даних та операції
"""

# ── Завдання 1 — Арифметика ───────────────────────────────────────────────────
a, b = 17, 5
operations = [
    ("+",  a + b),
    ("-",  a - b),
    ("*",  a * b),
    ("/",  a / b),
    ("//", a // b),
    ("%",  a % b),
    ("**", a ** b),
]
for op, result in operations:
    print(f"{a} {op} {b} = {result}")

# ── Завдання 2 — Рядкові методи ───────────────────────────────────────────────
text = "  hello, world!  "
print(text.strip())                          # 1. без пробілів
print(text.strip().capitalize())             # 2. перша велика
print(text.count("l"))                       # 3. скільки 'l'
print(text.strip().replace("world", "Python"))  # 4. заміна
parts = text.strip().split(", ")            # 5. розбити за ", "
print(parts)                                 # ['hello', 'world!']

# ── Завдання 3 — safe_int ─────────────────────────────────────────────────────
def safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

print(safe_int("42"))    # 42
print(safe_int("abc"))   # 0
print(safe_int(3.7))     # 3
print(safe_int(None))    # 0

# ── Завдання 4 — Truthiness ──────────────────────────────────────────────────
values = [0, 1, "", "hello", [], [0], None, False, True, 0.0, 0.001]
for val in values:
    print(f"  {repr(val):12} → {'truthy' if val else 'falsy'}")

# ── Завдання 5 (Challenge) — Калькулятор ─────────────────────────────────────
def calculator(a_str: str, op: str, b_str: str) -> str:
    try:
        a = float(a_str)
        b = float(b_str)
    except ValueError:
        return "Помилка: введіть числа"

    match op:
        case "+": result = a + b
        case "-": result = a - b
        case "*": result = a * b
        case "/":
            if b == 0:
                return "Помилка: ділення на нуль"
            result = a / b
        case _:
            return f"Помилка: невідома операція '{op}'"

    return f"{a} {op} {b} = {result:.2f}"

print(calculator("10", "/", "3"))   # 10.0 / 3.0 = 3.33
print(calculator("5", "+", "2.5"))  # 5.0 + 2.5 = 7.50
print(calculator("10", "/", "0"))   # ділення на нуль
print(calculator("abc", "+", "1"))  # не числа
