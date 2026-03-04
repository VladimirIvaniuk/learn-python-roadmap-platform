"""
Рішення — Урок 3

Дивись після того, як спробував сам!
"""

# Завдання 1
number = 7
if number % 2 == 0:
    print("Парне")
else:
    print("Непарне")

# Завдання 2
for i in range(1, 6):
    print(i**2)

# Завдання 3
fruits = ["яблуко", "груша", "слива"]
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")

# Завдання 4
count = 10
while count >= 1:
    print(count)
    count -= 1
print("Старт!")
