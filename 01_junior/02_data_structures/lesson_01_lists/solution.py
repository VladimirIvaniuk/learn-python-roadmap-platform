"""
Розв'язки — Урок 1: Списки та кортежі
"""
import copy

# ── Завдання 1 — Індексація і зрізи ──────────────────────────────────────────
lst = [10, 20, 30, 40, 50, 60, 70, 80, 90]

print(f"Перший:     {lst[0]}, Останній: {lst[-1]}")
print(f"Індекси 2–5: {lst[2:6]}")
print(f"Кожен 3-й:  {lst[::3]}")
print(f"Зворотний:  {lst[::-1]}")

# ── Завдання 2 — Методи ───────────────────────────────────────────────────────
fruits = ["banana", "apple", "cherry"]
fruits.append("mango")           # 1
fruits.insert(1, "grape")        # 2
fruits.remove("banana")          # 3
fruits.sort()                    # 4
print("Sorted:", fruits)
print("Reversed:", sorted(fruits, reverse=True))  # 5 (не змінює оригінал)

# ── Завдання 3 — Shallow vs Deep Copy ────────────────────────────────────────
original = [1, [2, 3], 4]
shallow = original.copy()
# Зміна вкладеного списку у копії впливає на оригінал
shallow[1].append(999)
print(f"\nShallow copy: зміна вкладеного = {original[1]}")  # [2, 3, 999]!

original = [1, [2, 3], 4]
deep = copy.deepcopy(original)
deep[1].append(0)
print(f"Deep copy: оригінал незмінний = {original[1]}")     # [2, 3]

# ── Завдання 4 — list_stats() ─────────────────────────────────────────────────
def list_stats(numbers: list[int | float]) -> dict:
    if not numbers:
        return {}
    sorted_nums = sorted(numbers)
    return {
        "min":    min(numbers),
        "max":    max(numbers),
        "sum":    sum(numbers),
        "mean":   sum(numbers) / len(numbers),
        "range":  max(numbers) - min(numbers),
        "sorted": sorted_nums,
    }

print(f"\nStats: {list_stats([3, 1, 4, 1, 5, 9, 2, 6])}")

# ── Завдання 5 (Challenge) — Матриця ─────────────────────────────────────────
def transpose(matrix: list[list]) -> list[list]:
    """Транспонує матрицю."""
    return [list(row) for row in zip(*matrix)]

def matrix_multiply(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """Множення матриць A × B."""
    rows_a, cols_a = len(a), len(a[0])
    cols_b = len(b[0])
    result = [[0.0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    return result

m = [[1, 2, 3], [4, 5, 6]]
print(f"\nОригінал:      {m}")
print(f"Транспонована: {transpose(m)}")

a = [[1, 2], [3, 4]]
b = [[5, 6], [7, 8]]
print(f"A × B = {matrix_multiply(a, b)}")
