# 🏆 Senior Project: Production-Ready Python Service

Фінальний проєкт Senior рівня — enterprise-grade мікросервіс з усіма best practices.

---

## 📋 Опис

**Система управління завданнями** (Task Management System) зі Clean Architecture,
повною тестовою покриттю, CI/CD, Docker та документацією.

---

## 🎯 Ціль

Побудувати систему, яку можна з гордістю показати на інтерв'ю та в реальному продакшені.

---

## ✅ Вимоги

### Архітектура (Clean / Hexagonal)

```
src/
├── domain/              # Entities + Domain Logic (чистий Python, без залежностей)
│   ├── entities.py      # Task, User, Comment dataclasses
│   ├── value_objects.py # Email, TaskStatus, Priority
│   └── exceptions.py    # DomainError, ValidationError, NotFoundError
│
├── application/         # Use Cases (бізнес-логіка, залежить тільки від domain)
│   ├── use_cases/
│   │   ├── create_task.py
│   │   ├── assign_task.py
│   │   └── complete_task.py
│   └── ports/           # Interfaces (Protocol)
│       ├── task_repo.py
│       ├── user_repo.py
│       └── notifier.py
│
├── infrastructure/      # Adapters (конкретні реалізації)
│   ├── db/
│   │   ├── models.py    # SQLAlchemy models
│   │   └── repositories.py
│   ├── cache/
│   │   └── redis_cache.py
│   └── notifications/
│       └── email_notifier.py
│
├── api/                 # FastAPI (Interface Adapter)
│   ├── v1/
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── dependencies.py
│   └── middleware.py
│
└── container.py         # DI Container
```

### Domain Entities

```python
# domain/entities.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    BACKLOG     = "backlog"
    IN_PROGRESS = "in_progress"
    REVIEW      = "review"
    DONE        = "done"

class Priority(int, Enum):
    LOW    = 1
    MEDIUM = 2
    HIGH   = 3
    URGENT = 4

@dataclass
class Task:
    id: str
    title: str
    assignee_id: str | None
    status: TaskStatus
    priority: Priority
    created_by: str
    created_at: datetime
    due_date: datetime | None = None
    tags: list[str] = field(default_factory=list)
    comments: list["Comment"] = field(default_factory=list)

    def assign(self, user_id: str) -> None:
        if self.status == TaskStatus.DONE:
            raise DomainError("Cannot assign completed task")
        self.assignee_id = user_id

    def complete(self) -> None:
        if self.status != TaskStatus.IN_PROGRESS:
            raise DomainError("Task must be in progress to complete")
        self.status = TaskStatus.DONE
```

### Ports (Interfaces)

```python
# application/ports/task_repo.py
from typing import Protocol

class TaskRepository(Protocol):
    async def find_by_id(self, task_id: str) -> Task | None: ...
    async def find_by_assignee(self, user_id: str, status: TaskStatus | None = None) -> list[Task]: ...
    async def save(self, task: Task) -> None: ...
    async def delete(self, task_id: str) -> None: ...
    async def count(self, filters: dict) -> int: ...
```

### Use Cases

```python
# application/use_cases/create_task.py
@dataclass
class CreateTaskCommand:
    title: str
    created_by: str
    priority: Priority = Priority.MEDIUM
    assignee_id: str | None = None
    due_date: datetime | None = None
    tags: list[str] = field(default_factory=list)

class CreateTaskUseCase:
    def __init__(self, task_repo: TaskRepository, notifier: Notifier) -> None:
        self._repo = task_repo
        self._notifier = notifier

    async def execute(self, command: CreateTaskCommand) -> Task:
        task = Task(
            id=str(uuid.uuid4()),
            title=command.title,
            status=TaskStatus.BACKLOG,
            priority=command.priority,
            assignee_id=command.assignee_id,
            created_by=command.created_by,
            created_at=datetime.utcnow(),
            due_date=command.due_date,
            tags=command.tags,
        )
        await self._repo.save(task)
        if task.assignee_id:
            await self._notifier.notify_assigned(task)
        return task
```

### API Layer

```python
# api/v1/routes/tasks.py
@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    body: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateTaskUseCase = Depends(get_create_task_use_case),
) -> TaskResponse:
    command = CreateTaskCommand(
        title=body.title,
        created_by=current_user.id,
        priority=body.priority,
        assignee_id=body.assignee_id,
    )
    task = await use_case.execute(command)
    return TaskResponse.from_domain(task)
```

### Обов'язкові компоненти

1. **Caching (Redis)**
   - Кешувати `GET /tasks/{id}` на 60с
   - Інвалідація при `PUT/DELETE`

2. **Authentication (JWT)**
   - Access token (15 хв) + Refresh token (7 днів)
   - Token revocation list (Redis)

3. **Rate Limiting**
   - 100 req/min на IP (Sliding Window)
   - 10 req/min на create/update

4. **Testing (≥85% coverage)**
   - Unit тести для Domain (pytest)
   - Integration тести для Use Cases (InMemoryRepository)
   - E2E тести для API (TestClient)
   - `conftest.py` з fixtures

5. **Docker + Docker Compose**
   - Multi-stage Dockerfile
   - docker-compose з PostgreSQL + Redis
   - healthchecks

6. **CI/CD (GitHub Actions)**
   - lint + type check + tests при PR
   - Build Docker image при push до main

7. **Документація**
   - README з Quick Start
   - ADR-001 для вибору ключового архітектурного рішення
   - OpenAPI автодокументація через FastAPI

### Додаткові (бонус)

- Alembic міграції
- Celery / asyncio worker для email notifications
- WebSocket для real-time статусу задач
- Prometheus metrics (`/metrics`)
- Distributed tracing (OpenTelemetry)

---

## 📊 Критерії оцінки

| Критерій | Бали |
|----------|------|
| Clean Architecture (шари ізольовані) | 20 |
| Domain entities + Use Cases | 15 |
| API Layer | 10 |
| Caching + Rate Limiting | 10 |
| JWT Auth | 10 |
| Testing ≥85% | 15 |
| Docker + CI | 10 |
| Документація | 5 |
| Бонус | +15 |

**Прохідний бал: 75/95**

---

## 🔍 Checklist перед здачею

- [ ] `mypy --strict src/` без помилок
- [ ] `ruff check src/` без помилок  
- [ ] `pytest --cov=src --cov-fail-under=85`
- [ ] `docker compose up` — все стартує з першого разу
- [ ] Всі endpoints задокументовані в `/docs`
- [ ] README дозволяє новому розробнику запустити проєкт за 5 хвилин
- [ ] ADR написано для ключового архітектурного рішення

---

## 💬 Підсказка від Senior

> «Чистий код — це не той, що важко писати, а той, що легко читати через 6 місяців.
> Якщо ти можеш пояснити архітектурне рішення за 2 хвилини — воно правильне.»
