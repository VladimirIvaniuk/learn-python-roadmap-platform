"""
Рішення — Урок 3 (Comprehensions)

Дивись після того, як спробував сам!
"""

# Завдання 1
cubes = [x**3 for x in range(1, 6)]
print(cubes)

# Завдання 2
evens = [x for x in range(21) if x % 2 == 0]
print(evens)

# Завдання 3
names = ["Анна", "Богдан", "Віктор"]
name_lengths = {name: len(name) for name in names}
print(name_lengths)

# Завдання 4
numbers = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
doubled_unique = {x * 2 for x in numbers}
print(doubled_unique)
