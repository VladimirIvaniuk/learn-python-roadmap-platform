"""
Розв'язки — Урок 1: Файли та pathlib
"""
import csv
import json
import tempfile
from contextlib import contextmanager
from pathlib import Path

# ── Завдання 1 — Читання/запис тексту ────────────────────────────────────────
with tempfile.TemporaryDirectory() as tmpdir:
    sample = Path(tmpdir) / "story.txt"
    lines = ["Python — чудова мова.", "Я вчуся щодня.", "Прогрес є!"]
    sample.write_text("\n".join(lines), encoding="utf-8")

    text = sample.read_text(encoding="utf-8")
    print("=== Файл ===")
    print(text)

    # рядки довжиною > 15
    long_lines = [l for l in text.splitlines() if len(l) > 15]
    print("Довгі рядки:", long_lines)

    new_text = text.replace("Прогрес є!", "Завтра більше!")
    (Path(tmpdir) / "story2.txt").write_text(new_text, encoding="utf-8")

# ── Завдання 2 — CSV ──────────────────────────────────────────────────────────
students = [
    {"name": "Аліса", "grade": 92},
    {"name": "Боб",   "grade": 58},
    {"name": "Катя",  "grade": 85},
]

with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = Path(tmpdir) / "students.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "grade"])
        writer.writeheader()
        writer.writerows(students)

    with open(csv_path, encoding="utf-8") as f:
        data = list(csv.DictReader(f))

    avg = sum(int(r["grade"]) for r in data) / len(data)
    best = max(data, key=lambda r: int(r["grade"]))
    print(f"\nCSV середній бал: {avg:.1f}")
    print(f"Найкращий: {best['name']} — {best['grade']}")

    above_avg = [r for r in data if int(r["grade"]) >= avg]
    print(f"Вище середнього: {[r['name'] for r in above_avg]}")

# ── Завдання 3 — JSON конфіг ──────────────────────────────────────────────────
default_config = {
    "debug": False,
    "host": "localhost",
    "port": 8000,
    "max_connections": 100,
}

def load_config(path: Path, defaults: dict) -> dict:
    if not path.exists():
        path.write_text(json.dumps(defaults, indent=2), encoding="utf-8")
        print(f"Створено конфіг: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {**defaults, **raw}

with tempfile.TemporaryDirectory() as tmpdir:
    cfg = load_config(Path(tmpdir) / "config.json", default_config)
    print(f"\nКонфіг: {cfg}")

# ── Завдання 5 (Challenge) — Аналіз директорії ────────────────────────────────
def analyze_directory(path: str | Path) -> dict:
    root = Path(path)
    if not root.exists():
        return {}

    stats: dict[str, int] = {}
    total = 0
    for f in root.rglob("*"):
        if f.is_file():
            ext = f.suffix.lower() or "(без розширення)"
            stats[ext] = stats.get(ext, 0) + 1
            total += 1

    return {
        "total_files": total,
        "extensions": dict(sorted(stats.items(), key=lambda x: x[1], reverse=True)),
        "path": str(root),
    }

# Аналізуємо свій модуль
here = Path(__file__).parent
result = analyze_directory(here)
print(f"\nАналіз {result['path']}:")
print(f"  Файлів: {result['total_files']}")
for ext, cnt in result["extensions"].items():
    print(f"  {ext}: {cnt}")
