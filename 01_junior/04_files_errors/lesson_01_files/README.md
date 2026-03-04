# Урок 1 — Файли та серіалізація

## Що вивчимо
- `open()`, контекстний менеджер `with`
- Режими файлів: `r`, `w`, `a`, `rb`, `wb`
- Читання: `read()`, `readline()`, `readlines()`
- CSV через `csv` модуль
- JSON через `json` модуль
- `pathlib.Path` — сучасна робота зі шляхами

---

## Теорія

### 1. Відкриття файлів — `open()` та `with`

```python
# Завжди використовуй with — він автоматично закриє файл
# навіть якщо виникне виключення

# ✅ Правильно
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()

# ❌ Уникай — якщо вийде помилка, файл НЕ закриється
f = open("data.txt")
content = f.read()
f.close()
```

**Режими відкриття:**
| Режим | Опис |
|-------|------|
| `"r"` | Читання (за замовчуванням). Помилка якщо файл не існує |
| `"w"` | Запис. Перезаписує або створює файл |
| `"a"` | Додавання в кінець. Створює якщо немає |
| `"x"` | Створення. Помилка якщо файл вже існує |
| `"rb"`, `"wb"` | Бінарний режим (зображення, PDF, ...) |
| `"r+"` | Читання та запис |

---

### 2. Читання файлів

```python
# read() — весь файл одним рядком
with open("poem.txt", encoding="utf-8") as f:
    text = f.read()
    print(text)

# readlines() — список рядків (із \n в кінці кожного)
with open("data.txt", encoding="utf-8") as f:
    lines = f.readlines()        # ["рядок1\n", "рядок2\n", ...]
    lines = [l.strip() for l in lines]  # прибрати \n

# readline() — один рядок за раз
with open("data.txt", encoding="utf-8") as f:
    first = f.readline().strip()
    second = f.readline().strip()

# ✅ Найефективніше — ітерація (не завантажує весь файл у пам'ять)
with open("huge_file.txt", encoding="utf-8") as f:
    for line in f:
        process(line.strip())    # обробляємо по одному рядку
```

---

### 3. Запис у файл

```python
# Запис — перезаписує файл
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Перший рядок\n")
    f.write("Другий рядок\n")
    f.writelines(["рядок 3\n", "рядок 4\n"])   # список рядків

# Додавання до існуючого файлу
import datetime
with open("log.txt", "a", encoding="utf-8") as f:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"[{timestamp}] Подія сталась\n")

# print() у файл
with open("report.txt", "w", encoding="utf-8") as f:
    print("Заголовок", file=f)
    print("="*20, file=f)
    for i, item in enumerate(items, 1):
        print(f"{i}. {item}", file=f)
```

---

### 4. CSV — табличні дані

```python
import csv

# Читання CSV
with open("students.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)    # перший рядок = заголовки
    students = list(reader)

for s in students:
    print(f"{s['name']}: {s['grade']}")

# Читання як списків
with open("data.csv") as f:
    reader = csv.reader(f)
    header = next(reader)      # перший рядок — заголовок
    rows = list(reader)

# Запис CSV
students = [
    {"name": "Аліса", "age": 20, "grade": "A"},
    {"name": "Боб",   "age": 22, "grade": "B"},
]

with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age", "grade"])
    writer.writeheader()
    writer.writerows(students)

# Запис як списків
rows = [["Name", "Score"], ["Alice", 92], ["Bob", 78]]
with open("scores.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows)
```

---

### 5. JSON — серіалізація даних

```python
import json

# Python → JSON рядок
data = {
    "name": "Аліса",
    "age": 25,
    "skills": ["Python", "FastAPI"],
    "active": True,
    "salary": None,
}

json_str = json.dumps(data, ensure_ascii=False, indent=2)
print(json_str)
# {
#   "name": "Аліса",
#   "age": 25,
#   ...
# }

# Python → JSON файл
with open("user.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# JSON файл → Python
with open("user.json", encoding="utf-8") as f:
    loaded = json.load(f)

print(loaded["name"])    # Аліса

# JSON рядок → Python
parsed = json.loads('{"x": 1, "y": [2, 3]}')
print(parsed["y"])       # [2, 3]
```

**Таблиця відповідності Python ↔ JSON:**
| Python | JSON |
|--------|------|
| `dict` | `object {}` |
| `list`, `tuple` | `array []` |
| `str` | `string ""` |
| `int`, `float` | `number` |
| `True`, `False` | `true`, `false` |
| `None` | `null` |

**Кастомна серіалізація:**
```python
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

data = {"created_at": datetime.now()}
print(json.dumps(data, cls=DateTimeEncoder))
# {"created_at": "2026-03-01T12:30:00.123456"}
```

---

### 6. `pathlib` — сучасна робота зі шляхами

```python
from pathlib import Path

# Створення шляху
p = Path("data/users/report.csv")
home = Path.home()              # /Users/username
current = Path.cwd()           # поточна директорія
absolute = p.resolve()         # абсолютний шлях

# Компоненти шляху
print(p.name)      # report.csv
print(p.stem)      # report
print(p.suffix)    # .csv
print(p.parent)    # data/users

# Навігація
config = Path.home() / ".config" / "myapp" / "settings.json"
print(config)      # /Users/username/.config/myapp/settings.json

# Перевірки
print(p.exists())   # чи існує
print(p.is_file())  # чи є файлом
print(p.is_dir())   # чи є директорією

# Читання/запис
text = p.read_text(encoding="utf-8")
p.write_text("новий вміст", encoding="utf-8")
bytes_data = p.read_bytes()

# Директорії
data_dir = Path("data")
data_dir.mkdir(parents=True, exist_ok=True)   # створити з усіма батьками

# Список файлів
for py_file in Path("src").glob("**/*.py"):   # рекурсивно
    print(py_file)

# Інформація про файл
stat = p.stat()
print(f"Розмір: {stat.st_size} байт")

# Перейменування та видалення
p.rename(Path("data/report_v2.csv"))
p.unlink()           # видалити файл (unlink_missing_ok=True для безпеки)
```

---

### 7. Контекстний менеджер — як він працює

```python
# with ... as: викликає __enter__ при вході та __exit__ при виході
# __exit__ викликається НАВІТЬ при виключенні

# Власний контекстний менеджер
class Timer:
    def __enter__(self):
        import time
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"Час виконання: {self.elapsed:.3f}с")
        return False   # False = не пригнічуємо виключення

with Timer():
    import time
    time.sleep(0.1)
    print("Робота...")
# Робота...
# Час виконання: 0.101с

# Через contextlib
from contextlib import contextmanager

@contextmanager
def managed_resource():
    print("Відкриваємо ресурс")
    try:
        yield "ресурс"
    finally:
        print("Закриваємо ресурс")

with managed_resource() as r:
    print(f"Використовуємо: {r}")
```

---

### Типові помилки

```python
# ❌ Читання файлу без закриття
f = open("data.txt")
data = f.read()
# f.close()  ← ЗАБУЛИ! — відкриті файлові дескриптори

# ❌ Неправильне кодування
with open("ukraine.txt") as f:    # за замовчуванням — системне кодування
    text = f.read()               # може не читати кирилицю на Windows

# ✅ Завжди вказуй encoding
with open("ukraine.txt", encoding="utf-8") as f:
    text = f.read()

# ❌ Перезапис замість додавання
with open("log.txt", "w") as f:   # "w" = перезаписує!
    f.write("новий запис")

# ✅ Додавання
with open("log.txt", "a") as f:
    f.write("новий запис\n")

# ❌ FileNotFoundError без перевірки
with open("maybe_exists.txt") as f:  # кине FileNotFoundError!
    data = f.read()

# ✅ Перевірка або обробка виключення
from pathlib import Path
path = Path("maybe_exists.txt")
if path.exists():
    data = path.read_text()
else:
    data = ""

# або
try:
    with open("maybe_exists.txt") as f:
        data = f.read()
except FileNotFoundError:
    data = ""
```

---

### У реальному проєкті

```python
# Читання конфігурації
from pathlib import Path
import json

CONFIG_FILE = Path("config.json")
DEFAULT_CONFIG = {"port": 8000, "debug": False, "db_url": "sqlite:///app.db"}

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        return DEFAULT_CONFIG.copy()
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

# Логування у файл
import logging
from pathlib import Path

def setup_logging(log_dir: Path = Path("logs")) -> None:
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=log_dir / "app.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        encoding="utf-8",
    )

# Обробка CSV завантажень у FastAPI
import csv
from io import StringIO

async def process_csv_upload(file_content: str) -> list[dict]:
    reader = csv.DictReader(StringIO(file_content))
    return [row for row in reader]
```

---

## Що маєш вміти після уроку
- [ ] Прочитати файл через `with open(...)` із правильним кодуванням
- [ ] Записати та дописати в файл
- [ ] Прочитати і записати CSV через `csv.DictReader/DictWriter`
- [ ] Серіалізувати та десеріалізувати JSON
- [ ] Маніпулювати шляхами через `pathlib.Path`
- [ ] Написати власний контекстний менеджер

---

## Що далі
Виконай завдання з `task.md`. Потім — **Урок 2: Виключення**.
