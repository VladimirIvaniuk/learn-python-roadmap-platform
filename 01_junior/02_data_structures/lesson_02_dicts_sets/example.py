"""
Урок 2 — Приклади: словники та множини
"""
from collections import defaultdict, Counter

# ── Словник: базові операції ─────────────────────────────────────────────────
person = {"name": "Аліса", "age": 25, "city": "Київ"}

# Безпечний доступ
print(person.get("phone", "N/A"))   # N/A
print(person.get("name"))           # Аліса

# Оновлення
person["email"] = "alice@example.com"
person.update({"age": 26, "role": "admin"})
merged = {"defaults": True} | person           # Python 3.9+
print(person)

# Ітерація
print("\nДані користувача:")
for key, value in person.items():
    print(f"  {key}: {value}")

# Фільтрація
grades = {"Аліса": 92, "Боб": 58, "Катя": 85, "Денис": 71}
passed = {k: v for k, v in grades.items() if v >= 70}
print(f"\nСклали іспит: {passed}")
print(f"Найкращий: {max(grades, key=grades.get)}")

# ── Вкладені словники ────────────────────────────────────────────────────────
config = {
    "database": {"host": "localhost", "port": 5432, "name": "mydb"},
    "cache": {"host": "localhost", "port": 6379, "ttl": 300},
}

db_host = config.get("database", {}).get("host", "unknown")
print(f"\nDB host: {db_host}")

# ── Множини ──────────────────────────────────────────────────────────────────
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

print(f"\nA: {a}")
print(f"B: {b}")
print(f"A | B (об'єднання): {a | b}")
print(f"A & B (перетин):    {a & b}")
print(f"A - B (різниця):    {a - b}")
print(f"A ^ B (симетр.різн):{a ^ b}")

# Дедублікація зі збереженням порядку
def deduplicate(lst):
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
print(f"\nДедуплікація: {deduplicate(data)}")

# ── defaultdict ───────────────────────────────────────────────────────────────
text = "the quick brown fox jumps over the lazy dog the fox"
word_count = Counter(text.split())
print(f"\nТоп-3 слова: {word_count.most_common(3)}")

# Групування
events = [
    ("2026-03-01", "login"), ("2026-03-01", "view"),
    ("2026-03-02", "login"), ("2026-03-01", "purchase"),
]
by_date = defaultdict(list)
for date, event in events:
    by_date[date].append(event)

print("\nПодії по датах:")
for date, evts in sorted(by_date.items()):
    print(f"  {date}: {evts}")
