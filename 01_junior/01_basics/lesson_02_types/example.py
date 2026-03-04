"""
Урок 2 — Приклади: типи даних та операції
"""

# ── int та float ──────────────────────────────────────────────────────────────
a, b = 17, 5

print(f"{a} + {b} = {a + b}")     # 22
print(f"{a} - {b} = {a - b}")     # 12
print(f"{a} * {b} = {a * b}")     # 85
print(f"{a} / {b} = {a / b}")     # 3.4  (завжди float)
print(f"{a} // {b} = {a // b}")   # 3    (цілочисельне)
print(f"{a} % {b} = {a % b}")     # 2    (остача)
print(f"{a} ** {b} = {a ** b}")   # 1419857

# Цікаві особливості
print(f"-7 // 2 = {-7 // 2}")     # -4  (не -3 — завжди в менший бік!)
print(f"-7 % 2 = {-7 % 2}")       # 1   (знак результату = знак дільника)

# float проблема
print(f"0.1 + 0.2 = {0.1 + 0.2}")          # 0.30000000000000004
print(f"rounded: {round(0.1 + 0.2, 10)}")   # 0.3

from decimal import Decimal
print(f"Decimal: {Decimal('0.1') + Decimal('0.2')}")  # 0.3

# ── str методи ────────────────────────────────────────────────────────────────
text = "  Hello, World!  "

print(repr(text))                  # покаже пробіли
print(text.strip())                # "Hello, World!"
print(text.strip().upper())        # "HELLO, WORLD!"
print(text.strip().lower())        # "hello, world!"
print(text.strip().title())        # "Hello, World!"

s = "banana"
print(f"find 'an': {s.find('an')}")        # 1
print(f"count 'a': {s.count('a')}")        # 3
print(f"replace: {s.replace('a', 'o')}")   # bonono
print(f"startswith 'ban': {s.startswith('ban')}")  # True

csv = "яблуко,груша,слива,манго"
fruits = csv.split(",")
print(fruits)                      # ['яблуко', 'груша', 'слива', 'манго']
print(" | ".join(fruits))          # яблуко | груша | слива | манго

# ── bool та truthy/falsy ──────────────────────────────────────────────────────
print("\nTruthy / Falsy:")
falsy_values = [0, 0.0, "", [], {}, set(), None, False]
for val in falsy_values:
    print(f"  {repr(val):12} → {'truthy' if val else 'falsy'}")

# ── Конвертація типів ─────────────────────────────────────────────────────────
print(int("42"))           # 42
print(int(3.99))           # 3  (не округляє, відкидає!)
print(float("3.14"))       # 3.14
print(str(42))             # "42"
print(bool(0))             # False
print(bool("hello"))       # True

# Безпечна конвертація
def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

print(safe_int("42"))    # 42
print(safe_int("abc"))   # 0
print(safe_int(None))    # 0
