"""
Розв'язки — Урок 2: Словники та множини
"""
from collections import defaultdict

# ── Завдання 1 — Студенти ────────────────────────────────────────────────────
grades = {"Аліса": 92, "Боб": 58, "Катя": 85, "Денис": 71, "Олег": 45}

print("Провалили іспит:")
for name, g in grades.items():
    if g < 60:
        print(f"  ❌ {name}: {g}")

best = max(grades, key=grades.get)
print(f"Найкращий студент: {best} ({grades[best]})")

avg = sum(grades.values()) / len(grades)
print(f"Середній бал: {avg:.1f}")

grades["Боб"] = 75
grades["Євген"] = 88
print(f"Оновлений словник: {grades}")

# ── Завдання 2 — word_count() ────────────────────────────────────────────────
import re

def word_count(text: str) -> dict[str, int]:
    """Підраховує слова без урахування регістру та пунктуації."""
    words = re.findall(r"\w+", text.lower())
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

print(f"\nword_count: {word_count('the quick fox the fox')}")

# ── Завдання 3 — Множини ─────────────────────────────────────────────────────
math_class = {"Аліса", "Боб", "Катя", "Денис", "Олег"}
python_class = {"Катя", "Денис", "Ірина", "Максим"}

print(f"\nВ обох класах:           {math_class & python_class}")
print(f"Тільки в math:           {math_class - python_class}")
print(f"Хоч в одному:            {math_class | python_class}")
print(f"Тільки в одному (XOR):   {math_class ^ python_class}")

# ── Завдання 4 — deduplicate() ───────────────────────────────────────────────
def deduplicate(lst: list) -> list:
    """Прибирає дублікати зі збереженням порядку."""
    seen: set = set()
    result = []
    for item in lst:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result

print(f"\nDeduplicate: {deduplicate([3, 1, 4, 1, 5, 9, 2, 6, 5])}")

# ── Завдання 5 (Challenge) — group_by() ──────────────────────────────────────
def group_by(items: list[dict], key: str) -> dict[str, list]:
    """Групує список словників за значенням поля."""
    grouped: dict[str, list] = defaultdict(list)
    for item in items:
        if key in item:
            grouped[item[key]].append(item)
    return dict(grouped)

users = [
    {"name": "A", "city": "Kyiv"},
    {"name": "B", "city": "Lviv"},
    {"name": "C", "city": "Kyiv"},
    {"name": "D", "city": "Lviv"},
]
grouped = group_by(users, "city")
print(f"\nGrouped by city:")
for city, members in grouped.items():
    names = [u["name"] for u in members]
    print(f"  {city}: {names}")
