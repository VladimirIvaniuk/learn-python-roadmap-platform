"""
Урок 3 — Приклади: умови та цикли
"""

# ── if / elif / else ──────────────────────────────────────────────────────────
temperature = 22

if temperature > 30:
    status = "Спекотно 🔥"
elif temperature > 20:
    status = "Тепло ☀️"
elif temperature > 10:
    status = "Прохолодно"
else:
    status = "Холодно 🥶"

print(f"{temperature}°C — {status}")

# Тернарний оператор
age = 20
label = "дорослий" if age >= 18 else "неповнолітній"
print(f"Вік {age}: {label}")

# ── for цикл ──────────────────────────────────────────────────────────────────
fruits = ["яблуко", "груша", "слива", "манго"]

print("\nСписок фруктів:")
for i, fruit in enumerate(fruits, start=1):
    print(f"  {i}. {fruit}")

# range зі步
print("\nПарні числа від 2 до 10:")
for n in range(2, 11, 2):
    print(n, end=" ")   # 2 4 6 8 10
print()

# Зворотний відлік
print("\nЗворотній відлік:")
for i in range(5, 0, -1):
    print(i, end=" ")
print("Старт! 🚀")

# zip — паралельний обхід
names = ["Аліса", "Боб", "Катя"]
scores = [92, 78, 85]

print("\nРезультати:")
for name, score in zip(names, scores):
    grade = "A" if score >= 90 else "B" if score >= 80 else "C"
    print(f"  {name}: {score} ({grade})")

# ── while цикл ────────────────────────────────────────────────────────────────
print("\nЧисла Фібоначчі до 100:")
a, b = 0, 1
while b <= 100:
    print(b, end=" ")
    a, b = b, a + b
print()

# ── break, continue, else ────────────────────────────────────────────────────
print("\nПошук першого числа кратного 7:")
for n in range(1, 50):
    if n % 7 == 0:
        print(f"  Знайшли: {n}")
        break
else:
    print("  Не знайшли")

print("\nНепарні від 1 до 10:")
for i in range(1, 11):
    if i % 2 == 0:
        continue
    print(i, end=" ")
print()

# ── match / case (Python 3.10+) ──────────────────────────────────────────────
def http_status(code: int) -> str:
    match code:
        case 200 | 201 | 204:
            return "Success"
        case 301 | 302:
            return "Redirect"
        case 400:
            return "Bad Request"
        case 404:
            return "Not Found"
        case c if 500 <= c < 600:
            return f"Server Error ({c})"
        case _:
            return f"Unknown ({code})"

for code in [200, 404, 500, 503, 999]:
    print(f"  HTTP {code}: {http_status(code)}")

# ── FizzBuzz ──────────────────────────────────────────────────────────────────
print("\nFizzBuzz (1-20):")
for i in range(1, 21):
    if i % 15 == 0:
        print("FizzBuzz", end=" ")
    elif i % 3 == 0:
        print("Fizz", end=" ")
    elif i % 5 == 0:
        print("Buzz", end=" ")
    else:
        print(i, end=" ")
print()
