# 🎓 Junior Project: CLI Task Manager

Фінальний проєкт Junior рівня — перевірка всіх вивчених концепцій.

---

## 📋 Опис

Консольний менеджер задач з persistence у JSON-файлі.

---

## ✅ Вимоги

### Обов'язкові (основний бал)

1. **Клас `Task`** (OOP)
   ```python
   @dataclass
   class Task:
       id: int
       title: str
       description: str
       status: str  # "todo" | "in_progress" | "done"
       priority: int  # 1-5
       created_at: str  # ISO format
       tags: list[str]
   ```

2. **Клас `TaskManager`** (OOP + файли)
   - `add_task(title, description, priority, tags)` → Task
   - `update_status(task_id, new_status)`
   - `delete_task(task_id)`
   - `list_tasks(status=None, priority=None, tag=None)` → list[Task]
   - `save(path)` / `load(path)` — JSON serialization

3. **Обробка помилок** (виключення)
   - Власний `TaskNotFoundError(task_id)`
   - Валідація: priority 1-5, status тільки з дозволеного списку
   - `safe_load()` — не крашиться якщо файл відсутній

4. **CLI інтерфейс** (цикл + умови)
   ```
   > add "Зробити тест" --priority 3 --tags python,testing
   > list --status todo
   > update 1 done
   > delete 2
   > stats
   > quit
   ```

5. **Статистика** `stats()`:
   - Кількість задач за статусами
   - Середній пріоритет
   - Найпопулярніші теги (Counter)

### Додаткові (бонусні бали)

- `search(query)` — пошук по title + description
- `export_csv(path)` — експорт у CSV
- Сортування: `list --sort priority|created_at|title`
- Кольоровий вивід через `\033[...m` escape codes
- `undo` остання операція

---

## 🗂 Структура проєкту

```
junior_project/
├── task_manager.py    # TaskManager клас
├── models.py          # Task dataclass + exceptions
├── cli.py             # CLI loop (main)
├── storage.py         # JSON load/save
└── tasks.json         # (авто-створюється)
```

---

## 💡 Підказки

- Використовуй `dataclasses.asdict()` для серіалізації у JSON
- `datetime.now().isoformat()` для created_at
- `argparse` або власний простий парсер команд
- `collections.Counter` для статистики тегів
- `pathlib.Path` для роботи з файловою системою

---

## 🧪 Як перевірити себе

```bash
python cli.py
# Спробуй:
# 1. add 5 задач з різними пріоритетами і тегами
# 2. list --status todo
# 3. update <id> done
# 4. stats
# 5. Перезапусти — переконайся що задачі збереглися
```

---

## 📊 Критерії оцінки

| Критерій | Бали |
|----------|------|
| Всі класи реалізовані | 20 |
| Обробка помилок | 15 |
| CLI інтерфейс | 20 |
| JSON persistence | 15 |
| Статистика | 10 |
| Код читабельний (PEP 8) | 10 |
| Бонус (search, export...) | +10 |

**Прохідний бал: 70/90**

---

## 🏆 Еталонне рішення

Після виконання перевір `solution/` директорію (якщо є) або попроси ментора.
