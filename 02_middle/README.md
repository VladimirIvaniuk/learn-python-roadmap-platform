# Middle — Уроки

## Уроки

| Урок | Тема | Що вивчиш |
|-----|------|------------|
| [Урок 1](lesson_01_oop_advanced/README.md) | Поглиблене ООП | Магічні методи, декоратори, property, ABC |
| [Урок 2](lesson_02_async/README.md) | Асинхронність | asyncio, async/await, gather |
| [Урок 3](lesson_03_fastapi/README.md) | FastAPI | REST API, Pydantic, маршрути |
| [Урок 4](lesson_04_databases/README.md) | Бази даних | SQLAlchemy, ORM, CRUD |
| [Урок 5](lesson_05_testing/README.md) | Тестування | pytest, parametrize, fixtures |
| [Урок 6](lesson_06_devops/README.md) | DevOps | Git, Docker, .env |

## Структура

```
lesson_XX/
├── README.md   ← теорія
├── example.py  ← приклад
└── task.md     ← завдання
```

**Практика:** `practice/`  
**Відповіді:** `solutions/`

## Повний проєкт

Після уроків 3–5 збери все разом: [full_project/](full_project/README.md) — API + SQLAlchemy + pytest в одній папці.

## Залежності

```bash
pip install fastapi uvicorn sqlalchemy pytest
```
