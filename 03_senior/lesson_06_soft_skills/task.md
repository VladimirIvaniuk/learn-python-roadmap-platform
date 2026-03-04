# Завдання — Soft Skills

## Завдання 1 — Code Review
Проведи code review для наступного коду:
```python
def process(x, y, z, lst, flag):
    res = []
    for i in range(len(lst)):
        if flag == True:
            if lst[i] > x:
                if lst[i] < y:
                    res.append(lst[i] * z)
        else:
            res.append(lst[i])
    return res
```
Знайди і задокументуй: нейменування, структуру, типи, edge cases, тести.

## Завдання 2 — Technical Documentation
Напиши README для свого FastAPI проєкту (або demo):
- Badges (Python version, tests, coverage)
- Quick Start (< 5 команд)
- Configuration table
- API Overview
- Contributing guidelines

## Завдання 3 — ADR
Напиши Architecture Decision Record для одного реального рішення в проєкті.
Формат: Context → Decision → Consequences (позитивні та негативні).
Наприклад: "Вибір SQLite замість PostgreSQL для MVP"

## Завдання 4 — Interview Preparation
Підготуй відповіді (STAR format) на питання:
1. "Розкажи про найскладніший баг що ти виправляв"
2. "Розкажи про ситуацію де ти не погоджувався з рішенням команди"
3. "Яке твоє найбільше технічне досягнення?"

## Завдання 5 (Challenge) — Teaching
Поясни наступні концепції так, ніби пояснюєш Junior розробнику:
1. Навіщо SOLID? (без слів "принцип" — тільки аналогії)
2. Що таке N+1 проблема? (з реальним прикладом з коду)
3. Чому bcrypt а не SHA256 для паролів? (з числами)
Запиши голосом або текстом (мінімум 200 слів кожне).
