"""
Урок 1 — Приклади: списки та кортежі
"""
import copy

# ── Індексація та зрізи ───────────────────────────────────────────────────────
fruits = ["яблуко", "груша", "слива", "манго", "ківі"]

print(fruits[0])       # яблуко
print(fruits[-1])      # ківі
print(fruits[1:4])     # ['груша', 'слива', 'манго']
print(fruits[::2])     # ['яблуко', 'слива', 'ківі']  (кожен 2-й)
print(fruits[::-1])    # зворотній порядок

# ── Методи списку ─────────────────────────────────────────────────────────────
lst = [3, 1, 4, 1, 5, 9]

lst.append(2)           # додати в кінець
lst.insert(0, 0)        # вставити на початку
lst.extend([6, 5])      # додати кілька
print("Після додавань:", lst)

lst.remove(1)           # видалити перше '1'
last = lst.pop()        # видалити і повернути останній
print(f"Видалено: {last}, залишилось: {lst}")

nums = [3, 1, 4, 1, 5, 9, 2, 6]
print(f"sorted: {sorted(nums)}")     # новий список
nums.sort()                          # на місці
print(f"sort(): {nums}")
print(f"reversed: {list(reversed(nums))}")

# ── Пастка: shallow vs deep copy ─────────────────────────────────────────────
original = [1, [2, 3], 4]

shallow = original.copy()           # або original[:]
shallow[0] = 99                     # не впливає на original
shallow[1].append(999)              # ВПЛИВАЄ! — вкладений список shared
print("Original після shallow:", original)   # [1, [2, 3, 999], 4]

deep = copy.deepcopy(original)
deep[1].append(0)
print("Original після deep:", original)     # не змінився

# ── Кортежі ───────────────────────────────────────────────────────────────────
point = (3, 7)
x, y = point
print(f"Точка: x={x}, y={y}")

# Зміна кортежу неможлива
# point[0] = 99   # TypeError: 'tuple' object does not support item assignment

# namedtuple
from collections import namedtuple
from typing import NamedTuple

Color = namedtuple("Color", ["r", "g", "b"])
red = Color(255, 0, 0)
print(f"Червоний: R={red.r}, G={red.g}, B={red.b}")

class Product(NamedTuple):
    name: str
    price: float
    in_stock: bool = True

p = Product("Python Book", 29.99)
print(p)                # Product(name='Python Book', price=29.99, in_stock=True)
print(p._asdict())     # {'name': 'Python Book', 'price': 29.99, 'in_stock': True}

# ── Матриці ───────────────────────────────────────────────────────────────────
# ПРАВИЛЬНЕ створення матриці (не через * !)
matrix = [[0] * 3 for _ in range(3)]
matrix[0][0] = 1
print("Матриця:", matrix)   # [[1,0,0],[0,0,0],[0,0,0]]

# Транспонування
m = [[1, 2, 3], [4, 5, 6]]
transposed = [list(row) for row in zip(*m)]
print("Транспонована:", transposed)   # [[1,4],[2,5],[3,6]]

# ── Вбудовані функції ─────────────────────────────────────────────────────────
nums = [7, 2, 9, 1, 8, 3]
print(f"len={len(nums)}, sum={sum(nums)}, min={min(nums)}, max={max(nums)}")
print(f"any > 8: {any(x > 8 for x in nums)}")
print(f"all > 0: {all(x > 0 for x in nums)}")
