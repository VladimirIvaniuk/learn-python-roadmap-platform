"""
Урок 1 — Приклади: файли та серіалізація
"""
import csv, json
from pathlib import Path
from contextlib import contextmanager
import time

BASE = Path(__file__).parent / "_demo_files"
BASE.mkdir(exist_ok=True)

# ── Запис та читання тексту ───────────────────────────────────────────────────
txt_path = BASE / "notes.txt"
txt_path.write_text(
    "Перший рядок\nДругий рядок\nТретій рядок\n",
    encoding="utf-8"
)

with open(txt_path, encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        print(f"  {i}: {line.rstrip()}")

# Ефективне читання великих файлів — рядок за рядком
def count_lines(path: Path) -> int:
    count = 0
    with open(path, encoding="utf-8") as f:
        for _ in f:
            count += 1
    return count

print(f"Рядків: {count_lines(txt_path)}")

# ── CSV ───────────────────────────────────────────────────────────────────────
csv_path = BASE / "students.csv"
students = [
    {"name": "Аліса", "age": 20, "grade": 92},
    {"name": "Боб",   "age": 22, "grade": 78},
    {"name": "Катя",  "age": 19, "grade": 88},
]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age", "grade"])
    writer.writeheader()
    writer.writerows(students)

with open(csv_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    loaded = list(reader)

print("\nCSV завантажено:")
for s in loaded:
    grade = int(s["grade"])
    print(f"  {s['name']}: {grade} {'✅' if grade >= 80 else '❌'}")

# ── JSON ──────────────────────────────────────────────────────────────────────
json_path = BASE / "config.json"
config = {
    "app_name": "LearnPython",
    "version": "2.0",
    "debug": False,
    "features": ["timer", "notes", "stats"],
    "db": {"host": "localhost", "port": 5432},
}

json_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
loaded_config = json.loads(json_path.read_text(encoding="utf-8"))
print(f"\nJSON: version={loaded_config['version']}, features={loaded_config['features']}")

# ── pathlib ───────────────────────────────────────────────────────────────────
p = Path("src/utils/helpers.py")
print(f"\npathlib:")
print(f"  name: {p.name}")
print(f"  stem: {p.stem}")
print(f"  suffix: {p.suffix}")
print(f"  parent: {p.parent}")

# Список файлів у директорії
print(f"\nФайли в {BASE}:")
for f in BASE.iterdir():
    size = f.stat().st_size
    print(f"  {f.name} ({size} байт)")

# ── Контекстний менеджер ──────────────────────────────────────────────────────
class Timer:
    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self._start
        print(f"  Виконано за {self.elapsed:.4f}с")
        return False

print("\nТаймер:")
with Timer():
    result = sum(x**2 for x in range(100_000))

@contextmanager
def temp_file(suffix=".tmp"):
    p = BASE / f"temp{suffix}"
    try:
        yield p
    finally:
        if p.exists():
            p.unlink()

with temp_file(".json") as tmp:
    tmp.write_text('{"temp": true}')
    print(f"  Тимчасовий файл: {tmp.exists()}")
print(f"  Після with: {tmp.exists()}")   # False — видалено
