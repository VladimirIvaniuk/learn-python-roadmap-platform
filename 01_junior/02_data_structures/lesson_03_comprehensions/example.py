"""
Урок 3 — Приклади: comprehensions та генератори
"""
import sys
import itertools

# ── List comprehensions ────────────────────────────────────────────────────────
squares = [x**2 for x in range(1, 11)]
print("Квадрати:", squares)

evens = [x for x in range(20) if x % 2 == 0]
print("Парні:", evens)

# З умовою у виразі (не фільтрі)
labels = ["парне" if x % 2 == 0 else "непарне" for x in range(1, 7)]
print("Парність:", labels)

# ── Dict та Set comprehensions ────────────────────────────────────────────────
number_names = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}
inverted = {v: k for k, v in number_names.items()}
print("Інвертований:", inverted)

words = ["banana", "apple", "cherry", "avocado", "blueberry"]
first_letters = {w[0] for w in words}
print("Перші літери:", first_letters)

# Нормалізація
raw_data = {"  Name ": "Аліса", "AGE": 25, "  CITY ": "Київ"}
clean = {k.strip().lower(): v for k, v in raw_data.items()}
print("Нормалізовано:", clean)

# ── Вкладені comprehensions ───────────────────────────────────────────────────
matrix = [[i * j for j in range(1, 4)] for i in range(1, 4)]
print("\nМатриця:")
for row in matrix:
    print(" ", row)

flat = [x for row in matrix for x in row]
print("Плоский:", flat)

# Декартовий добуток
colors = ["red", "green", "blue"]
sizes = ["S", "M"]
variants = [f"{c}-{s}" for c in colors for s in sizes]
print("Варіанти:", variants)

# ── Generator expressions ────────────────────────────────────────────────────
# Порівняння пам'яті
N = 100_000
lst = [x**2 for x in range(N)]
gen = (x**2 for x in range(N))
print(f"\nList [{N}]: {sys.getsizeof(lst):,} байт")
print(f"Generator:   {sys.getsizeof(gen):,} байт")

# sum з генератором — ефективніше
total = sum(x**2 for x in range(N))
print(f"Сума квадратів: {total:,}")

# ── Генераторні функції ───────────────────────────────────────────────────────
def fibonacci():
    """Нескінченний генератор Фібоначчі."""
    a, b = 0, 1
    while True:
        yield b
        a, b = b, a + b

fib = fibonacci()
print("\nПерші 10 Фібоначчі:", [next(fib) for _ in range(10)])

# Через islice
print("Перші 15:", list(itertools.islice(fibonacci(), 15)))
print("Сума 20: ", sum(itertools.islice(fibonacci(), 20)))

def gen_range(start, stop, step=1):
    """Власна реалізація range."""
    current = start
    while current < stop:
        yield current
        current += step

print("\nВласний range(0,10,3):", list(gen_range(0, 10, 3)))

# ── yield from ───────────────────────────────────────────────────────────────
def flatten(nested):
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item

data = [1, [2, [3, 4], 5], [6, [7, [8]]]]
print("Flatten:", list(flatten(data)))

# ── itertools ─────────────────────────────────────────────────────────────────
print("\nitertools examples:")
print("chain:", list(itertools.chain([1, 2], [3], [4, 5])))
print("product:", list(itertools.product("AB", "12")))
print("combinations:", list(itertools.combinations([1, 2, 3, 4], 2)))
