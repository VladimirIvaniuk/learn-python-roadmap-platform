"""
Розв'язки — Урок 3: Comprehensions та генератори
"""
import sys
import itertools
import time

# ── Завдання 1 — List comprehensions ─────────────────────────────────────────
cubes = [x**3 for x in range(1, 11)]
print("Куби:", cubes)

evens = [x for x in range(0, 51, 2)]
print("Парні:", evens)

long_words = [w for w in ["cat", "elephant", "dog", "python", "ox"] if len(w) > 4]
print("Довгі слова:", long_words)

arrows = [f"{x} → {x**2}" for x in range(1, 6)]
print("Стрілки:", arrows)

# ── Завдання 2 — Dict та Set comprehensions ───────────────────────────────────
parity = {n: ("парне" if n % 2 == 0 else "непарне") for n in range(1, 6)}
print("\nПарність:", parity)

original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
print("Інвертований:", inverted)

words = ["apple", "Banana", "CHERRY"]
first_letters = {w[0].lower() for w in words}
print("Перші літери:", first_letters)

# ── Завдання 3 — Генераторна функція Фібоначчі ───────────────────────────────
def fibonacci():
    """Нескінченний генератор Фібоначчі."""
    a, b = 0, 1
    while True:
        yield b
        a, b = b, a + b

first_15 = list(itertools.islice(fibonacci(), 15))
print(f"\nПерші 15 Фібоначчі: {first_15}")

sum_20 = sum(itertools.islice(fibonacci(), 20))
print(f"Сума перших 20: {sum_20}")

# ── Завдання 4 — Порівняння продуктивності ───────────────────────────────────
N = 1_000_000

t0 = time.perf_counter()
total_list = sum([x**2 for x in range(N)])
t_list = time.perf_counter() - t0

t0 = time.perf_counter()
total_gen = sum(x**2 for x in range(N))
t_gen = time.perf_counter() - t0

list_mem = sys.getsizeof([x**2 for x in range(1000)])
gen_mem = sys.getsizeof(x**2 for x in range(1000))

print(f"\nList comprehension: {t_list:.4f}с, пам'ять (1000 ел.): {list_mem} байт")
print(f"Generator expression: {t_gen:.4f}с, пам'ять:            {gen_mem} байт")

# ── Завдання 5 (Challenge) — Pipeline транзакцій ─────────────────────────────
transactions = [
    {"id": 1, "amount": 150.0,  "type": "credit", "user_id": 42},
    {"id": 2, "amount": -50.0,  "type": "debit",  "user_id": 7},
    {"id": 3, "amount": 200.0,  "type": "credit", "user_id": 42},
    {"id": 4, "amount": -300.0, "type": "debit",  "user_id": 7},
]

# 1. Сума кредитових транзакцій
credit_total = sum(t["amount"] for t in transactions if t["type"] == "credit")
print(f"\nСума кредитових: {credit_total}")

# 2. Сума по кожному користувачу
user_totals: dict[int, float] = {}
for t in transactions:
    uid = t["user_id"]
    user_totals[uid] = user_totals.get(uid, 0) + t["amount"]
print(f"По користувачах: {user_totals}")

# 3. ID транзакцій з від'ємною сумою
negative_ids = [t["id"] for t in transactions if t["amount"] < 0]
print(f"Від'ємні транзакції: {negative_ids}")
