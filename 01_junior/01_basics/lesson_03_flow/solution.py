"""
Розв'язки — Урок 3: Умови та цикли
"""

# ── Завдання 1 — grade() ─────────────────────────────────────────────────────
def grade(score: int) -> str:
    if not 0 <= score <= 100:
        return "помилка"
    if score >= 90:
        return "відмінно"
    if score >= 75:
        return "добре"
    if score >= 60:
        return "задовільно"
    return "незадовільно"

for s in [95, 80, 65, 50, 110, -5]:
    print(f"  {s:>3} → {grade(s)}")

# ── Завдання 2 — FizzBuzz ─────────────────────────────────────────────────────
print()
for i in range(1, 31):
    if i % 15 == 0:
        print("FizzBuzz", end=" ")
    elif i % 3 == 0:
        print("Fizz", end=" ")
    elif i % 5 == 0:
        print("Buzz", end=" ")
    else:
        print(i, end=" ")
print()

# ── Завдання 3 — Таблиця множення ────────────────────────────────────────────
print()
for i in range(2, 10):
    row = "  ".join(f"{i} × {j} = {i*j:<3}" for j in range(1, 10))
    print(row)

# ── Завдання 4 — Підрахунок слів ─────────────────────────────────────────────
sentences = ["Python is great", "I love Python", "Python is easy", "Java is old"]
target = "python"
count = sum(1 for s in sentences if target in s.lower().split())
print(f'\nРечень з "Python": {count}')

# ── Завдання 5 (Challenge) — Числа Фібоначчі ──────────────────────────────────
def fibonacci(max_val: int) -> list[int]:
    result = []
    a, b = 1, 1
    while a <= max_val:
        result.append(a)
        a, b = b, a + b
    return result

print(f"\nfibonacci(10):  {fibonacci(10)}")
print(f"fibonacci(100): {fibonacci(100)}")

divisible_by_3 = [n for n in fibonacci(1000) if n % 3 == 0]
print(f"Фібоначчі ≤1000, кратні 3: {divisible_by_3}")
