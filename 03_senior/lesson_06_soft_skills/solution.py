"""
Розв'язки — Soft Skills (Senior)
Цей файл містить: результат code review, README шаблон, ADR шаблон,
приклади STAR-відповідей і рефакторинг коду для менторингу.
"""

# ── Завдання 1 — Code Review (проблемний UserManager) ────────────────────────
CODE_FOR_REVIEW = '''
# ──── ОРИГІНАЛЬНИЙ КОД (знайдіть і виправте проблеми) ────
class UserManager:
    users = []                       # ПРОБЛЕМА: mutable class attr

    def addUser(self, n, e):         # ПРОБЛЕМА: camelCase (PEP 8)
        u = {"name": n, "email": e}  # ПРОБЛЕМА: однолітерні назви
        self.users.append(u)         # ПРОБЛЕМА: немає валідації
        return u

def getAdmins(users):                # ПРОБЛЕМА: немає типових анотацій
    result = []
    for u in users:
        if u.get("role") == "admin":
            result.append(u)
    return result
'''

CODE_REVIEW_COMMENT = """
📋 Code Review для UserManager

🔴 CRITICAL (обов'язково виправити):
  1. `users = []` — mutable class attribute поділяється між усіма екземплярами.
     Виправлення: перенести у `__init__(self): self.users = []`

  2. `addUser` → `add_user` (PEP 8 snake_case для методів).

  3. Відсутня валідація email перед збереженням (ін'єкція, некоректні дані).

🟡 WARNING (бажано виправити):
  4. Однолітерні параметри `n`, `e`, `u` → `name`, `email`, `user`.

  5. `getAdmins` → `get_admins`, і краще зробити методом класу.

  6. Відсутні типові анотації (mypy не зможе перевірити).

🟢 SUGGESTION (для покращення):
  7. Використати `@dataclass` для `User` замість dict.

  8. Метод `get_admins` — list comprehension замість explicit loop.
"""

print(CODE_REVIEW_COMMENT)

# ── Виправлений UserManager ───────────────────────────────────────────────────
from dataclasses import dataclass, field
import re

@dataclass
class User:
    name: str
    email: str
    role: str = "user"

    def __post_init__(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError(f"Invalid email: {self.email!r}")
        if not self.name.strip():
            raise ValueError("Name cannot be empty")

class UserManager:
    def __init__(self) -> None:
        self._users: list[User] = []

    def add_user(self, name: str, email: str, role: str = "user") -> User:
        user = User(name=name, email=email, role=role)
        self._users.append(user)
        return user

    def get_admins(self) -> list[User]:
        return [u for u in self._users if u.role == "admin"]

    def find_by_email(self, email: str) -> User | None:
        return next((u for u in self._users if u.email == email), None)

    def __len__(self) -> int:
        return len(self._users)

mgr = UserManager()
mgr.add_user("Аліса", "alice@example.com", "admin")
mgr.add_user("Боб", "bob@example.com")
print(f"Admins: {mgr.get_admins()}")
print(f"Total: {len(mgr)}")

# ── Завдання 2 — README шаблон ────────────────────────────────────────────────
README_TEMPLATE = """
# 🚀 My FastAPI Project

> Короткий опис проекту — для чого і для кого.

## ✨ Можливості

- 🔒 JWT автентифікація
- 📦 CRUD для ресурсів
- 🐳 Docker підтримка
- ✅ 90%+ тест покриття

## 🛠 Технологічний стек

| Компонент | Технологія |
|-----------|------------|
| Backend   | FastAPI 0.110 |
| ORM       | SQLAlchemy 2.0 |
| DB        | PostgreSQL 16 |
| Cache     | Redis 7 |
| CI/CD     | GitHub Actions |

## 🚀 Запуск

```bash
# 1. Клонування
git clone https://github.com/user/project.git
cd project

# 2. Середовище
cp .env.example .env
# Відредагуй .env

# 3. Docker
docker compose up -d

# 4. Або локально
pip install -r requirements.txt
uvicorn main:app --reload
```

## 📡 API

Документація доступна на `http://localhost:8000/docs`

## 🧪 Тести

```bash
pytest --cov=. --cov-report=html
```

## 📜 Ліцензія

MIT — дивись [LICENSE](LICENSE)
"""

print("README template length:", len(README_TEMPLATE), "chars")

# ── Завдання 3 — ADR ──────────────────────────────────────────────────────────
ADR_001 = """
# ADR-001: Вибір PostgreSQL замість MongoDB

**Дата**: 2026-03-02
**Статус**: Accepted
**Автор**: Tech Lead

## Контекст

Нам потрібна база даних для зберігання користувачів, замовлень і транзакцій.
Дані мають чіткі зв'язки (Users → Orders → Items → Products).

## Варіанти

| | PostgreSQL | MongoDB |
|-|------------|---------|
| ACID | ✅ | Частково |
| Schema | Strict | Flexible |
| Joins | Native | $lookup |
| Scalability | Vertical + Read replicas | Horizontal |

## Рішення

**Вибираємо PostgreSQL** через:
1. Чіткі реляційні зв'язки між сутностями
2. Потреба у ACID транзакціях (фінансові операції)
3. SQLAlchemy 2.0 з async підтримкою
4. Команда має досвід з SQL

## Наслідки

**Позитивні**:
- Строга схема запобігає некоректним даним
- Складні запити через JOIN

**Негативні**:
- Горизонтальне масштабування складніше
- Потреба в Alembic для міграцій
"""

print("ADR template length:", len(ADR_001), "chars")

# ── Завдання 4 — STAR відповіді ───────────────────────────────────────────────
STAR_ANSWERS = {
    "Розкажіть про складний баг": """
**S** (Situation): В продакшені замічено що 5% запитів до /checkout закінчуються
    таймаутом під час пікового навантаження (10k RPS).

**T** (Task): Знайти та усунути проблему за 24 години, не зупиняючи сервіс.

**A** (Action):
  1. Увімкнув профілювання (py-spy) — виявив N+1 запит у cart.get_items()
  2. Додав selectinload() для eager loading товарів
  3. Додав Redis кеш на 60с для catalog.get_product()
  4. Написав навантажувальний тест (locust) для верифікації

**R** (Result): Час відповіді знизився з 2.1с до 0.08с. 0 таймаутів після деплою.
    Додав ці перевірки у CI pipeline.
""",
    "Конфлікт у команді": """
**S**: Старший розробник наполягав на монолітній архітектурі, я бачив потребу
    в мікросервісах для нового модуля.

**T**: Прийняти технічне рішення без розколу в команді.

**A**:
  1. Запропонував написати ADR з обома варіантами
  2. Провів технічне ревʼю з командою, показав trade-offs
  3. Запропонував компроміс: модульний моноліт з чистими межами модулів
  4. Встановили критерії переходу на мікросервіси (50k DAU, 3+ команди)

**R**: Прийнято одноголосно. Через 6 місяців досягли критеріїв і успішно
    виокремили перший мікросервіс.
"""
}

for question, answer in STAR_ANSWERS.items():
    print(f"\n🎯 Питання: {question}")
    print(answer)
