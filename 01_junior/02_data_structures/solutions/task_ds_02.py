"""
Рішення — Урок 2 (Словники та множини)

Дивись після того, як спробував сам!
"""

# Завдання 1
product = {"name": "Телефон", "price": 5000, "in_stock": True}
print(product["name"], product["price"])
print(product.get("discount", "0%"))

# Завдання 2
my_data = {"name": "Олексій", "age": 41, "city": "Київ"}
my_data["країна"] = "Україна"
for key, value in my_data.items():
    print(f"{key}: {value}")

# Завдання 3
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
print("Об'єднання:", a | b)
print("Перетин:", a & b)
print("Різниця a-b:", a - b)

# Завдання 4
duplicates = [1, 2, 2, 3, 3, 3, 4]
unique = set(duplicates)
print(unique)
