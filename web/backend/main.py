"""
Learn Python — Веб-платформа навчання

Backend: FastAPI
Запуск: python3 web/run.py
"""
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .executor import run_code, check_task, MAX_CODE_SIZE
from .database import (
    init_db, get_db, User, Progress, CodeSnapshot, LessonNote,
    LessonAttempt, ReviewQueue, UserGamification, WeeklyPlanTaskState,
)

app = FastAPI(title="Learn Python", version="1.0")

# Rate limit для /api/run: 60 викликів/хв на IP
_run_calls: dict[str, list[float]] = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 60


def check_rate_limit(ip: str) -> bool:
    now = time.time()
    if ip not in _run_calls:
        _run_calls[ip] = []
    calls = _run_calls[ip]
    calls[:] = [t for t in calls if now - t < RATE_LIMIT_WINDOW]
    if len(calls) >= RATE_LIMIT_MAX:
        return False
    calls.append(now)
    return True


# Ініціалізація БД
init_db()

# Шлях до кореня проєкту
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# === API Models ===
class RunCodeRequest(BaseModel):
    code: str

    @field_validator("code")
    @classmethod
    def code_size_limit(cls, v: str) -> str:
        if len(v) > MAX_CODE_SIZE:
            raise ValueError(f"Код занадто великий (максимум {MAX_CODE_SIZE // 1024} KB)")
        return v


class CheckTaskRequest(BaseModel):
    lesson_id: str
    module_id: Optional[str] = None
    code: str

    @field_validator("code")
    @classmethod
    def code_size_limit(cls, v: str) -> str:
        if len(v) > MAX_CODE_SIZE:
            raise ValueError(f"Код занадто великий (максимум {MAX_CODE_SIZE // 1024} KB)")
        return v


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProgressRequest(BaseModel):
    module_id: str
    lesson_id: str
    time_spent: int = 0


class TimeRequest(BaseModel):
    module_id: str
    lesson_id: str
    seconds: int


class NoteRequest(BaseModel):
    module_id: str
    lesson_id: str
    content: str


class CodeRequest(BaseModel):
    module_id: str
    lesson_id: str
    code: str


class ReviewCompleteRequest(BaseModel):
    module_id: str
    lesson_id: str
    topic: str
    success: bool = True


class ReviewSessionItem(BaseModel):
    module_id: str
    lesson_id: str
    topic: str
    success: bool = True


class ReviewSessionRequest(BaseModel):
    items: list[ReviewSessionItem]


class GoalPresetRequest(BaseModel):
    preset: str


class PlanTaskActionRequest(BaseModel):
    plan_date: str  # YYYY-MM-DD
    task_key: str
    action: str  # done|skip|snooze|pending


# === Auth ===
from .auth import hash_password, verify_password, create_access_token, decode_token


def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    return payload


# === Lessons config ===
# Junior: модулі з уроками
LESSONS_CONFIG = {
    "01_basics": {
        "name": "Основи Python",
        "lessons": [
            ("lesson_01_hello", "Урок 1 — Перша програма"),
            ("lesson_02_types", "Урок 2 — Типи та операції"),
            ("lesson_03_flow", "Урок 3 — Умови та цикли"),
            ("lesson_04_functions", "Урок 4 — Функції"),
        ],
    },
    "02_data_structures": {
        "name": "Структури даних",
        "lessons": [
            ("lesson_01_lists", "Урок 1 — Списки"),
            ("lesson_02_dicts_sets", "Урок 2 — Словники та множини"),
            ("lesson_03_comprehensions", "Урок 3 — Comprehensions"),
        ],
    },
    "03_oop": {
        "name": "ООП",
        "lessons": [
            ("lesson_01_classes", "Урок 1 — Класи та об'єкти"),
            ("lesson_02_inheritance", "Урок 2 — Наслідування"),
        ],
    },
    "04_files_errors": {
        "name": "Файли та винятки",
        "lessons": [
            ("lesson_01_files", "Урок 1 — Робота з файлами"),
            ("lesson_02_exceptions", "Урок 2 — Обробка помилок"),
        ],
    },
    # Middle: один модуль, уроки в 02_middle/
    "02_middle": {
        "name": "Middle",
        "lessons": [
            ("lesson_01_oop_advanced", "Урок 1 — Поглиблене ООП"),
            ("lesson_02_async", "Урок 2 — Асинхронність"),
            ("lesson_03_fastapi", "Урок 3 — FastAPI"),
            ("lesson_04_databases", "Урок 4 — Бази даних"),
            ("lesson_05_testing", "Урок 5 — Тестування"),
            ("lesson_06_devops", "Урок 6 — DevOps"),
        ],
    },
    # Senior: один модуль, уроки в 03_senior/
    "03_senior": {
        "name": "Senior",
        "lessons": [
            ("lesson_01_architecture", "Урок 1 — Архітектура"),
            ("lesson_02_design_patterns", "Урок 2 — Design Patterns"),
            ("lesson_03_system_design", "Урок 3 — Системний дизайн"),
            ("lesson_04_code_quality", "Урок 4 — Якість коду"),
            ("lesson_05_security", "Урок 5 — Безпека"),
            ("lesson_06_soft_skills", "Урок 6 — М'які навички"),
        ],
    },
}

MODULE_PATHS = {
    "01_basics": "01_junior/01_basics",
    "02_data_structures": "01_junior/02_data_structures",
    "03_oop": "01_junior/03_oop",
    "04_files_errors": "01_junior/04_files_errors",
    "02_middle": "02_middle",
    "03_senior": "03_senior",
}

# Рівні для API: які модулі належать якому рівню
LEVELS_CONFIG = {
    "junior": {
        "name": "Junior",
        "modules": ["01_basics", "02_data_structures", "03_oop", "04_files_errors"],
    },
    "middle": {
        "name": "Middle",
        "modules": ["02_middle"],
    },
    "senior": {
        "name": "Senior",
        "modules": ["03_senior"],
    },
}


def get_total_lessons() -> int:
    """Загальна кількість уроків."""
    return sum(len(cfg["lessons"]) for cfg in LESSONS_CONFIG.values())


# Додаткові ресурси для поглиблення (lesson_id -> [{name, url}])
LESSON_RESOURCES = {
    "lesson_01_hello": [
        {"name": "Python print()", "url": "https://realpython.com/python-print/"},
        {"name": "Python Basics", "url": "https://docs.python.org/3/tutorial/"},
    ],
    "lesson_02_types": [
        {"name": "Python Data Types", "url": "https://realpython.com/python-data-types/"},
    ],
    "lesson_03_flow": [
        {"name": "Conditionals", "url": "https://realpython.com/python-conditional-statements/"},
        {"name": "Loops", "url": "https://realpython.com/python-for-loop/"},
    ],
    "lesson_04_functions": [
        {"name": "Defining Functions", "url": "https://realpython.com/defining-your-own-python-function/"},
    ],
    "lesson_01_lists": [
        {"name": "Lists and Tuples", "url": "https://realpython.com/python-lists-tuples/"},
    ],
    "lesson_02_dicts_sets": [
        {"name": "Dictionaries", "url": "https://realpython.com/python-dicts/"},
        {"name": "Sets", "url": "https://realpython.com/python-sets/"},
    ],
    "lesson_03_comprehensions": [
        {"name": "Comprehensions", "url": "https://realpython.com/list-comprehension-python/"},
    ],
    "lesson_01_classes": [
        {"name": "OOP in Python", "url": "https://realpython.com/python3-object-oriented-programming/"},
    ],
    "lesson_02_inheritance": [
        {"name": "Inheritance", "url": "https://realpython.com/inheritance-composition-python/"},
    ],
    "lesson_01_files": [
        {"name": "Reading and Writing Files", "url": "https://realpython.com/read-write-files-python/"},
    ],
    "lesson_02_exceptions": [
        {"name": "Exceptions", "url": "https://realpython.com/python-exceptions/"},
    ],
    "lesson_01_oop_advanced": [
        {"name": "Magic Methods", "url": "https://realpython.com/operator-function-overloading/"},
        {"name": "Decorators", "url": "https://realpython.com/primer-on-python-decorators/"},
    ],
    "lesson_02_async": [
        {"name": "Async IO", "url": "https://realpython.com/async-io-python/"},
    ],
    "lesson_03_fastapi": [
        {"name": "FastAPI", "url": "https://fastapi.tiangolo.com/"},
    ],
    "lesson_04_databases": [
        {"name": "SQLAlchemy", "url": "https://docs.sqlalchemy.org/"},
    ],
    "lesson_05_testing": [
        {"name": "pytest", "url": "https://docs.pytest.org/"},
    ],
    "lesson_06_devops": [
        {"name": "Docker", "url": "https://docs.docker.com/"},
    ],
    "lesson_01_architecture": [
        {"name": "Clean Architecture", "url": "https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html"},
    ],
    "lesson_02_design_patterns": [
        {"name": "Python Patterns", "url": "https://refactoring.guru/design-patterns/python"},
    ],
    "lesson_03_system_design": [
        {"name": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer"},
    ],
    "lesson_04_code_quality": [
        {"name": "mypy", "url": "https://mypy-lang.org/"},
        {"name": "ruff", "url": "https://docs.astral.sh/ruff/"},
    ],
    "lesson_05_security": [
        {"name": "OWASP Top 10", "url": "https://owasp.org/www-project-top-ten/"},
    ],
}

# Підказки для уроків (lesson_id -> [підказка1, підказка2, ...])
LESSON_HINTS = {
    "lesson_01_hello": [
        "Використовуй print('текст') для виводу.",
        "Змінну створюй через city = 'назва'",
        "Сума: print(a + b)",
    ],
    "lesson_02_types": [
        "Ділення: a/b, цілочисельне: a//b, остача: a%b",
        "f-string: f'Температура: {temperature}°C'",
        "input() повертає рядок, int(input()) — число",
    ],
    "lesson_03_flow": [
        "Парність: number % 2 == 0",
        "range(1, 6) дає 1,2,3,4,5",
        "enumerate(list, start=1) — індекс з 1",
    ],
    "lesson_04_functions": [
        "def square(n): return n * n",
        "Параметр за замовчуванням: time_of_day='день'",
        "Парність: n % 2 == 0",
    ],
    "lesson_01_lists": [
        "colors[1] — другий, colors[-1] — останній",
        "Зріз: nums[1:4] — елементи 1,2,3",
        "append('x'), insert(1, 'x')",
    ],
    "lesson_02_dicts_sets": [
        "dict.get('key', 'default')",
        "for key, value in d.items():",
        "Множини: a | b, a & b, a - b",
    ],
    "lesson_03_comprehensions": [
        "[x**3 for x in range(1, 6)]",
        "[x for x in range(21) if x % 2 == 0]",
        "{name: len(name) for name in names}",
    ],
    "lesson_01_classes": [
        "def __init__(self, title, author):",
        "Метод area: return self.width * self.height",
        "deposit: if amount > 0: self.balance += amount",
    ],
    "lesson_02_inheritance": [
        "class Dog(Animal):",
        "super().info() для виклику батьківського методу",
        "_price — захищений атрибут",
    ],
    "lesson_01_files": [
        "open(path, 'w') — запис, open(path, 'r') — читання",
        "with open(...) as f: f.read()",
        "Режим 'a' — додавання в кінець",
    ],
    "lesson_02_exceptions": [
        "try: ... except ZeroDivisionError:",
        "safe_divide: if b == 0: return None",
        "class NegativeNumberError(Exception): pass",
    ],
}

# Теги тем для adaptive-routing і weak-topics
LESSON_TOPIC_MAP = {
    "lesson_01_hello": ["print", "variables", "f-strings", "input"],
    "lesson_02_types": ["types", "strings", "conversion", "truthy-falsy"],
    "lesson_03_flow": ["if-else", "for", "while", "enumerate-zip"],
    "lesson_04_functions": ["functions", "args-kwargs", "scope", "decorators"],
    "lesson_01_lists": ["lists", "tuples", "slicing"],
    "lesson_02_dicts_sets": ["dict", "set", "counter-defaultdict"],
    "lesson_03_comprehensions": ["comprehensions", "generators"],
    "lesson_01_classes": ["classes", "properties", "dunder"],
    "lesson_02_inheritance": ["inheritance", "polymorphism", "abc"],
    "lesson_01_files": ["files", "pathlib", "json-csv"],
    "lesson_02_exceptions": ["exceptions", "custom-exceptions", "retry"],
    "lesson_01_oop_advanced": ["dunder", "dataclass", "protocol"],
    "lesson_02_async": ["asyncio", "tasks", "semaphore-queue"],
    "lesson_03_fastapi": ["fastapi", "pydantic", "depends"],
    "lesson_04_databases": ["sqlalchemy", "orm", "n+1"],
    "lesson_05_testing": ["pytest", "fixtures", "mocking"],
    "lesson_06_devops": ["docker", "ci-cd", "settings"],
    "lesson_01_architecture": ["solid", "clean-architecture", "di"],
    "lesson_02_design_patterns": ["patterns", "factory", "strategy", "observer"],
    "lesson_03_system_design": ["cache", "rate-limit", "cap"],
    "lesson_04_code_quality": ["mypy", "ruff", "refactor"],
    "lesson_05_security": ["security", "jwt", "owasp", "injection"],
    "lesson_06_soft_skills": ["mentoring", "code-review", "documentation"],
}

LESSON_SMART_FEEDBACK = {
    "lesson_01_hello": {
        "Завд.1": "Перевір базовий вивід через print() і наявність числового віку.",
        "Завд.2": "Створи змінні city/a/b і виведи форматований рядок з обчисленням.",
        "Завд.3": "Використай f-string для суми/форматування, не конкатенацію рядків.",
    },
    "lesson_02_types": {
        "Завд.1": "Покрий усі операції: /, //, %, ** і виведи результати у явному форматі.",
        "Завд.2": "Покажи методи рядків: strip/capitalize/count/replace/split.",
        "Завд.3": "safe_int має використовувати try/except і повертати 0 при помилці.",
        "Завд.4": "Для кожного значення з набору виведи truthy/falsy.",
        "Завд.5": "Калькулятор: валідація операції, ділення на нуль, формат .2f.",
    },
    "lesson_03_flow": {
        "Завд.1": "Зроби гілкування через if/elif/else з чіткими межами умов.",
        "Завд.2": "Цикл for + range для генерації послідовності/квадратів.",
        "Завд.3": "enumerate для нумерації, zip для паралельного обходу.",
    },
}

SKILL_GROUPS = {
    "Python Core": {"print", "variables", "f-strings", "types", "strings", "conversion", "truthy-falsy", "if-else", "for", "while", "functions", "args-kwargs", "scope"},
    "Data Structures": {"lists", "tuples", "slicing", "dict", "set", "counter-defaultdict", "comprehensions", "generators"},
    "Backend": {"fastapi", "pydantic", "depends", "sqlalchemy", "orm", "n+1"},
    "Engineering": {"pytest", "fixtures", "mocking", "docker", "ci-cd", "settings", "mypy", "ruff", "refactor"},
    "Senior": {"solid", "clean-architecture", "di", "patterns", "factory", "strategy", "observer", "cache", "rate-limit", "cap", "security", "jwt", "owasp", "injection"},
}

ERROR_TOPIC_MAP = {
    "SyntaxError": ["syntax"],
    "IndentationError": ["syntax"],
    "NameError": ["variables"],
    "TypeError": ["types", "conversion"],
    "ValueError": ["conversion"],
    "IndexError": ["lists"],
    "KeyError": ["dict"],
    "AttributeError": ["classes"],
    "ZeroDivisionError": ["types"],
    "ModuleNotFoundError": ["imports"],
    "EOFError": ["input"],
}


def _safe_json_load_list(raw: str) -> list[str]:
    try:
        value = json.loads(raw or "[]")
        return value if isinstance(value, list) else []
    except Exception:
        return []


def _safe_json_dump(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def _ensure_platform_local_notice(text: str) -> str:
    """Глобальний стандарт Platform/Local для уроків з input()."""
    if not text:
        return text
    lowered = text.lower()
    if "input(" not in lowered:
        return text
    if "platform-версія" in lowered or "platform mode" in lowered:
        return text
    notice = (
        "\n\n> ⚠️ **Platform/Local стандарт**\n"
        "> - **Platform**: у веб-ранері `input()` може бути недоступний. Підстав фіксовані значення.\n"
        "> - **Local**: запускай у терміналі, якщо потрібен реальний ввід користувача.\n"
    )
    return text + notice


def _extract_error_type(error_text: str | None) -> str | None:
    if not error_text:
        return None
    import re as _re
    m = _re.search(r"([A-Za-z_]+Error):", error_text)
    return m.group(1) if m else None


def _detect_weak_topics(lesson_id: str, details: list[str], error_text: str | None) -> list[str]:
    topics = set(LESSON_TOPIC_MAP.get(lesson_id, []))
    error_type = _extract_error_type(error_text)
    if error_type and error_type in ERROR_TOPIC_MAP:
        topics.update(ERROR_TOPIC_MAP[error_type])
    # Якщо є конкретні фейли, повертаємо невеликий пріоритетний список
    if details:
        # lightweight heuristic: перші 3 теми уроку + error-based
        base = LESSON_TOPIC_MAP.get(lesson_id, [])[:3]
        if error_type:
            base = base + ERROR_TOPIC_MAP.get(error_type, [])
        return list(dict.fromkeys(base))[:4]
    return list(topics)[:4]


def _get_or_create_gamification(user_id: int, db: Session) -> UserGamification:
    item = db.query(UserGamification).filter(UserGamification.user_id == user_id).first()
    if item:
        return item
    item = UserGamification(user_id=user_id, xp=0, level=1, badges="[]", goal_preset="balanced")
    db.add(item)
    db.flush()
    return item


def _award_xp_and_badges(user_id: int, db: Session, passed: bool) -> dict:
    gm = _get_or_create_gamification(user_id, db)
    badges = _safe_json_load_list(gm.badges)
    gm.xp += 15 if passed else 3
    gm.level = 1 + (gm.xp // 200)
    if gm.xp >= 100 and "First 100 XP" not in badges:
        badges.append("First 100 XP")
    if gm.level >= 3 and "Level 3" not in badges:
        badges.append("Level 3")
    gm.badges = _safe_json_dump(badges)
    return {"xp": gm.xp, "level": gm.level, "badges": badges}


def _upsert_review_items(user_id: int, module_id: str, lesson_id: str, topics: list[str], db: Session) -> None:
    now = datetime.now(timezone.utc)
    for topic in topics:
        row = db.query(ReviewQueue).filter(
            ReviewQueue.user_id == user_id,
            ReviewQueue.module_id == module_id,
            ReviewQueue.lesson_id == lesson_id,
            ReviewQueue.topic == topic,
        ).first()
        if row:
            row.due_at = now
            row.interval_days = 1
            row.repetitions = 0
            row.last_result = 0
        else:
            db.add(ReviewQueue(
                user_id=user_id,
                module_id=module_id,
                lesson_id=lesson_id,
                topic=topic,
                due_at=now,
                interval_days=1,
                repetitions=0,
                last_result=0,
            ))


def _ordered_lessons() -> list[dict]:
    """Упорядкований список уроків за навчальною траєкторією."""
    order = []
    idx = 0
    for level in ("junior", "middle", "senior"):
        for mid in LEVELS_CONFIG[level]["modules"]:
            for lesson_id, title in LESSONS_CONFIG[mid]["lessons"]:
                idx += 1
                order.append({
                    "idx": idx,
                    "level": level,
                    "module_id": mid,
                    "lesson_id": lesson_id,
                    "title": title,
                    "topics": LESSON_TOPIC_MAP.get(lesson_id, []),
                })
    return order


def _recommend_next_lesson(
    completed_keys: set[str],
    weak_topics: list[dict],
    due_reviews: list[dict],
) -> dict | None:
    """Розумна рекомендація наступного уроку з урахуванням weak topics та черги review."""
    ordered = _ordered_lessons()
    weak_ordered = [w["topic"] for w in weak_topics[:5]]
    weak_set = set(weak_ordered)
    due_topic_set = {r["topic"] for r in due_reviews}
    due_lesson_set = {f"{r['module_id']}/{r['lesson_id']}" for r in due_reviews}

    best = None
    best_score = -10**9
    for item in ordered:
        key = f"{item['module_id']}/{item['lesson_id']}"
        if key in completed_keys:
            continue
        # Простий пререквізит: попередній урок у порядку має бути завершений
        prev_idx = item["idx"] - 1
        if prev_idx > 0:
            prev = ordered[prev_idx - 1]
            prev_key = f"{prev['module_id']}/{prev['lesson_id']}"
            if prev_key not in completed_keys:
                continue

        score = 0
        topics = set(item["topics"])
        weak_hits = len(topics & weak_set)
        if weak_hits:
            score += weak_hits * 8
        if key in due_lesson_set:
            score += 6
        if topics & due_topic_set:
            score += 4
        # Ранішим урокам невеликий пріоритет, щоб не ламати послідовність
        score -= item["idx"] * 0.05

        if score > best_score:
            reason_parts = []
            if weak_hits:
                reason_parts.append(f"покриває {weak_hits} слабк. тем")
            if key in due_lesson_set or (topics & due_topic_set):
                reason_parts.append("є повторення по темі")
            if not reason_parts:
                reason_parts.append("наступний крок траєкторії")
            best_score = score
            best = {
                "module_id": item["module_id"],
                "lesson_id": item["lesson_id"],
                "title": item["title"],
                "reason": ", ".join(reason_parts),
                "score": round(score, 2),
            }
    return best


def _recommend_lessons(
    completed_keys: set[str],
    weak_topics: list[dict],
    due_reviews: list[dict],
    top_n: int = 3,
) -> list[dict]:
    ordered = _ordered_lessons()
    weak_ordered = [w["topic"] for w in weak_topics[:8]]
    weak_set = set(weak_ordered)
    due_topic_set = {r["topic"] for r in due_reviews}
    due_lesson_set = {f"{r['module_id']}/{r['lesson_id']}" for r in due_reviews}

    candidates = []
    for item in ordered:
        key = f"{item['module_id']}/{item['lesson_id']}"
        if key in completed_keys:
            continue
        prev_idx = item["idx"] - 1
        if prev_idx > 0:
            prev = ordered[prev_idx - 1]
            prev_key = f"{prev['module_id']}/{prev['lesson_id']}"
            if prev_key not in completed_keys:
                continue
        topics = set(item["topics"])
        weak_hits = len(topics & weak_set)
        score = 0.0
        score += weak_hits * 8
        if key in due_lesson_set:
            score += 6
        if topics & due_topic_set:
            score += 4
        score -= item["idx"] * 0.05

        reason_parts = []
        if weak_hits:
            reason_parts.append(f"покриває {weak_hits} слабк. тем")
        if key in due_lesson_set or (topics & due_topic_set):
            reason_parts.append("є повторення по темі")
        if not reason_parts:
            reason_parts.append("наступний крок траєкторії")

        candidates.append({
            "module_id": item["module_id"],
            "lesson_id": item["lesson_id"],
            "title": item["title"],
            "reason": ", ".join(reason_parts),
            "score": round(score, 2),
        })
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_n]


def _build_smart_feedback(lesson_id: str, details: list[str], weak_topics: list[str]) -> dict:
    """Людинозрозумілий фідбек для check: що впало і що робити далі."""
    failed_steps = []
    for line in details:
        line_clean = str(line)
        if line_clean.startswith("✗") and "Завд." in line_clean:
            failed_steps.append(line_clean)
    guide = LESSON_SMART_FEEDBACK.get(lesson_id, {})
    next_actions = []
    for step in failed_steps:
        step_key = None
        for key in guide.keys():
            if key in step:
                step_key = key
                break
        if step_key:
            next_actions.append(guide[step_key])
    if not next_actions and weak_topics:
        next_actions = [f"Повтори тему: {topic}" for topic in weak_topics[:3]]
    if not next_actions:
        next_actions = [
            "Запусти код ще раз і виправ першу помилку у списку.",
            "Після виправлення знову натисни «Перевірити».",
        ]
    severity = "high" if failed_steps else ("medium" if weak_topics else "low")
    return {
        "severity": severity,
        "failed_steps": failed_steps[:5],
        "next_actions": list(dict.fromkeys(next_actions))[:5],
        "weak_topics": weak_topics[:5],
    }


def _build_quests(user_id: int, db: Session, goal_preset: str = "balanced") -> dict:
    """Daily/Weekly quests для мотиваційного шару."""
    now = datetime.now(timezone.utc)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = day_start - timedelta(days=day_start.weekday())  # Monday

    completed_today = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.completed_at >= day_start,
    ).count()
    completed_week = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.completed_at >= week_start,
    ).count()
    attempts_today = db.query(LessonAttempt).filter(
        LessonAttempt.user_id == user_id,
        LessonAttempt.created_at >= day_start,
    ).count()
    passed_today = db.query(LessonAttempt).filter(
        LessonAttempt.user_id == user_id,
        LessonAttempt.created_at >= day_start,
        LessonAttempt.passed == 1,
    ).count()
    passed_week = db.query(LessonAttempt).filter(
        LessonAttempt.user_id == user_id,
        LessonAttempt.created_at >= week_start,
        LessonAttempt.passed == 1,
    ).count()
    review_done_today = db.query(ReviewQueue).filter(
        ReviewQueue.user_id == user_id,
        ReviewQueue.updated_at >= day_start,
        ReviewQueue.last_result == 1,
    ).count()

    presets = {
        "easy": {"d_lessons": 1, "d_checks": 2, "d_reviews": 2, "w_lessons": 4, "w_pass": 6},
        "balanced": {"d_lessons": 2, "d_checks": 3, "d_reviews": 3, "w_lessons": 7, "w_pass": 10},
        "intensive": {"d_lessons": 3, "d_checks": 5, "d_reviews": 5, "w_lessons": 12, "w_pass": 18},
        "weekend": {"d_lessons": 1, "d_checks": 2, "d_reviews": 2, "w_lessons": 5, "w_pass": 8},
    }
    cfg = presets.get(goal_preset, presets["balanced"])

    return {
        "daily": [
            {
                "id": "daily_lessons_2",
                "title": f"Заверши {cfg['d_lessons']} урок(и) сьогодні",
                "target": cfg["d_lessons"],
                "progress": min(completed_today, cfg["d_lessons"]),
                "done": completed_today >= cfg["d_lessons"],
            },
            {
                "id": "daily_checks_3",
                "title": f"Зроби {cfg['d_checks']} перевірки коду",
                "target": cfg["d_checks"],
                "progress": min(attempts_today, cfg["d_checks"]),
                "done": attempts_today >= cfg["d_checks"],
            },
            {
                "id": "daily_reviews_3",
                "title": f"Закрий {cfg['d_reviews']} review-картки",
                "target": cfg["d_reviews"],
                "progress": min(review_done_today, cfg["d_reviews"]),
                "done": review_done_today >= cfg["d_reviews"],
            },
        ],
        "weekly": [
            {
                "id": "weekly_lessons_7",
                "title": f"Заверши {cfg['w_lessons']} уроків за тиждень",
                "target": cfg["w_lessons"],
                "progress": min(completed_week, cfg["w_lessons"]),
                "done": completed_week >= cfg["w_lessons"],
            },
            {
                "id": "weekly_pass_10",
                "title": f"Отримай {cfg['w_pass']} успішних перевірок",
                "target": cfg["w_pass"],
                "progress": min(passed_week, cfg["w_pass"]),
                "done": passed_week >= cfg["w_pass"],
            },
        ],
    }


def _lesson_title(module_id: str, lesson_id: str) -> str:
    for _lid, cfg in LEVELS_CONFIG.items():
        for mid in cfg["modules"]:
            if mid != module_id:
                continue
            for lid, title in LESSONS_CONFIG[mid]["lessons"]:
                if lid == lesson_id:
                    return title
    return lesson_id


def _build_weekly_plan(
    goal_preset: str,
    next_lessons: list[dict],
    reviews_due: list[dict],
    weak_topics: list[dict],
) -> list[dict]:
    """Генерує персональний план на 7 днів."""
    presets = {
        "easy": {"lessons_per_week": 4, "reviews_per_day": 2, "minutes": 20},
        "balanced": {"lessons_per_week": 7, "reviews_per_day": 3, "minutes": 35},
        "intensive": {"lessons_per_week": 12, "reviews_per_day": 5, "minutes": 55},
        "weekend": {"lessons_per_week": 5, "reviews_per_day": 2, "minutes": 25},
    }
    cfg = presets.get(goal_preset, presets["balanced"])
    today = datetime.now(timezone.utc).date()
    weak_top = [w["topic"] for w in weak_topics[:3]]
    reviews_pool = list(reviews_due)
    lessons_pool = list(next_lessons)

    days = []
    total_lessons_target = cfg["lessons_per_week"]
    lessons_assigned = 0

    for i in range(7):
        date = today + timedelta(days=i)
        is_weekend = date.weekday() >= 5
        day_lessons = []
        day_reviews = []
        day_practice = []

        # Weekend preset: major load on Sat/Sun
        lessons_for_day = 0
        if goal_preset == "weekend":
            if is_weekend:
                lessons_for_day = 2 if lessons_assigned + 2 <= total_lessons_target else max(0, total_lessons_target - lessons_assigned)
            else:
                lessons_for_day = 0
        else:
            remaining_days = max(1, 7 - i)
            remaining_lessons = max(0, total_lessons_target - lessons_assigned)
            lessons_for_day = min(2, (remaining_lessons + remaining_days - 1) // remaining_days)

        for _ in range(lessons_for_day):
            if not lessons_pool:
                break
            lesson = lessons_pool.pop(0)
            task_key = f"lesson:{lesson['module_id']}:{lesson['lesson_id']}"
            day_lessons.append({
                "task_key": task_key,
                "type": "lesson",
                "module_id": lesson["module_id"],
                "lesson_id": lesson["lesson_id"],
                "title": lesson.get("title") or _lesson_title(lesson["module_id"], lesson["lesson_id"]),
                "why": lesson.get("reason", "наступний крок"),
            })
            lessons_assigned += 1

        for _ in range(cfg["reviews_per_day"]):
            if not reviews_pool:
                break
            rev = reviews_pool.pop(0)
            task_key = f"review:{rev['module_id']}:{rev['lesson_id']}:{rev['topic']}"
            day_reviews.append({
                "task_key": task_key,
                "type": "review",
                "module_id": rev["module_id"],
                "lesson_id": rev["lesson_id"],
                "topic": rev["topic"],
            })

        # Micro-practice based on weak topics
        if weak_top:
            p_topic = weak_top[i % len(weak_top)]
            day_practice.append({
                "task_key": f"practice:{p_topic}:{date.isoformat()}",
                "type": "practice",
                "topic": p_topic,
                "title": "Мікро-практика 15 хв",
            })

        tasks = day_lessons + day_reviews + day_practice
        focus = "Закріплення та практика" if day_reviews else "Рух по нових уроках"
        days.append({
            "day_index": i + 1,
            "date": date.isoformat(),
            "focus": focus,
            "estimated_minutes": cfg["minutes"] + (10 if day_lessons else 0),
            "tasks": tasks,
        })
    return days


def _apply_plan_states(days: list[dict], states: list[WeeklyPlanTaskState]) -> list[dict]:
    """Накладає done/skip/snooze на план та переносить snooze на завтра."""
    if not days:
        return days

    day_index = {d["date"]: idx for idx, d in enumerate(days)}
    state_map = {(s.plan_date, s.task_key): s.action for s in states}

    # 1) Позначити статуси
    for d in days:
        for task in d.get("tasks", []):
            action = state_map.get((d["date"], task.get("task_key", "")))
            task["status"] = action or "pending"

    # 2) Обробити snooze: видалити з поточного дня і додати в наступний
    for s in states:
        if s.action != "snooze":
            continue
        idx = day_index.get(s.plan_date)
        if idx is None:
            continue
        # знайти task у поточному дні
        source_day = days[idx]
        source_tasks = source_day.get("tasks", [])
        task = next((t for t in source_tasks if t.get("task_key") == s.task_key), None)
        if not task:
            continue
        # прибираємо з поточного дня
        source_day["tasks"] = [t for t in source_tasks if t.get("task_key") != s.task_key]
        # додаємо в наступний день, якщо є
        if idx + 1 < len(days):
            moved = dict(task)
            moved["status"] = "pending"
            moved["carryover"] = True
            moved["rescheduled_from"] = s.plan_date
            # щоб не конфліктував зі станами наступного дня
            moved["task_key"] = f"{task.get('task_key')}::carry:{s.plan_date}"
            days[idx + 1]["tasks"].append(moved)

    # 3) Підрахунок прогресу дня
    for d in days:
        tasks = d.get("tasks", [])
        total = len(tasks)
        done = len([t for t in tasks if t.get("status") == "done"])
        d["progress"] = {"done": done, "total": total}

    return days

# Метадані: складність, час, пов'язані уроки
LESSON_META = {
    "lesson_01_hello": {"difficulty": "easy", "time": "15 хв", "prev": None, "next": "lesson_02_types"},
    "lesson_02_types": {"difficulty": "easy", "time": "20 хв", "prev": "lesson_01_hello", "next": "lesson_03_flow"},
    "lesson_03_flow": {"difficulty": "medium", "time": "25 хв", "prev": "lesson_02_types", "next": "lesson_04_functions"},
    "lesson_04_functions": {"difficulty": "medium", "time": "25 хв", "prev": "lesson_03_flow", "next": "lesson_01_lists"},
    "lesson_01_lists": {"difficulty": "medium", "time": "25 хв", "prev": "lesson_04_functions", "next": "lesson_02_dicts_sets"},
    "lesson_02_dicts_sets": {"difficulty": "medium", "time": "30 хв", "prev": "lesson_01_lists", "next": "lesson_03_comprehensions"},
    "lesson_03_comprehensions": {"difficulty": "medium", "time": "20 хв", "prev": "lesson_02_dicts_sets", "next": "lesson_01_classes"},
    "lesson_01_classes": {"difficulty": "medium", "time": "30 хв", "prev": "lesson_03_comprehensions", "next": "lesson_02_inheritance"},
    "lesson_02_inheritance": {"difficulty": "medium", "time": "30 хв", "prev": "lesson_01_classes", "next": "lesson_01_files"},
    "lesson_01_files": {"difficulty": "medium", "time": "25 хв", "prev": "lesson_02_inheritance", "next": "lesson_02_exceptions"},
    "lesson_02_exceptions": {"difficulty": "medium", "time": "25 хв", "prev": "lesson_01_files", "next": None},
}

# Шляхи до рішень (module_id, lesson_id) -> відносний шлях
SOLUTION_PATHS = {
    ("01_basics", "lesson_01_hello"): "01_junior/01_basics/solutions/task_01.py",
    ("01_basics", "lesson_02_types"): "01_junior/01_basics/solutions/task_02.py",
    ("01_basics", "lesson_03_flow"): "01_junior/01_basics/solutions/task_03.py",
    ("01_basics", "lesson_04_functions"): "01_junior/01_basics/solutions/task_04.py",
    ("02_data_structures", "lesson_01_lists"): "01_junior/02_data_structures/solutions/task_ds_01.py",
    ("02_data_structures", "lesson_02_dicts_sets"): "01_junior/02_data_structures/solutions/task_ds_02.py",
    ("02_data_structures", "lesson_03_comprehensions"): "01_junior/02_data_structures/solutions/task_ds_03.py",
    ("03_oop", "lesson_01_classes"): "01_junior/03_oop/solutions/task_oop_01.py",
    ("03_oop", "lesson_02_inheritance"): "01_junior/03_oop/solutions/task_oop_02.py",
    ("04_files_errors", "lesson_01_files"): "01_junior/04_files_errors/solutions/task_fe_01.py",
    ("04_files_errors", "lesson_02_exceptions"): "01_junior/04_files_errors/solutions/task_fe_02.py",
    ("02_middle", "lesson_01_oop_advanced"): "02_middle/solutions/task_m1_01.py",
    ("02_middle", "lesson_02_async"): "02_middle/solutions/task_m2_01.py",
    ("02_middle", "lesson_03_fastapi"): "02_middle/solutions/app_m3.py",
    ("02_middle", "lesson_04_databases"): "02_middle/solutions/task_m4_01.py",
    ("02_middle", "lesson_05_testing"): "02_middle/solutions/test_m5.py",
    ("03_senior", "lesson_01_architecture"): "03_senior/solutions/task_s1_01.py",
    ("03_senior", "lesson_02_design_patterns"): "03_senior/solutions/task_s2_01.py",
    ("03_senior", "lesson_03_system_design"): "03_senior/solutions/task_s3_01.py",
    ("03_senior", "lesson_05_security"): "03_senior/solutions/task_s5_01.py",
}


def get_lesson_path(module_id: str, lesson_id: str) -> Path:
    """Повертає шлях до папки уроку."""
    module_path = MODULE_PATHS.get(module_id)
    if not module_path:
        raise HTTPException(404, "Module not found")
    return BASE_DIR / module_path / lesson_id


def read_file_safe(path: Path) -> str:
    """Читає файл або повертає порожній рядок."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


# === Auth endpoints ===
@app.post("/api/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Реєстрація нового користувача."""
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(400, "Email вже зареєстровано")
    user = User(
        email=req.email,
        username=req.username,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"token": token, "user": {"id": user.id, "email": user.email, "username": user.username}}


@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Вхід."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Невірний email або пароль")
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"token": token, "user": {"id": user.id, "email": user.email, "username": user.username}}


@app.get("/api/auth/me")
def get_me(authorization: Optional[str] = Header(None)):
    """Поточний користувач."""
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")
    return {"user_id": payload.get("sub"), "email": payload.get("email")}


# === Progress endpoints ===
@app.get("/api/progress")
def get_progress(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Прогрес користувача з розбивкою по рівнях."""
    payload = get_current_user(authorization)
    total = get_total_lessons()
    if not payload:
        by_level = {lid: {"done": 0, "total": sum(len(LESSONS_CONFIG[mid]["lessons"]) for mid in cfg["modules"])}
                    for lid, cfg in LEVELS_CONFIG.items()}
        return {"completed": [], "total": total, "by_level": by_level}

    user_id = int(payload["sub"])
    items = db.query(Progress).filter(Progress.user_id == user_id).all()
    completed = [f"{p.module_id}/{p.lesson_id}" for p in items]

    by_level = {}
    for level_id, level_cfg in LEVELS_CONFIG.items():
        level_completed = 0
        level_total = 0
        for mid in level_cfg["modules"]:
            for lid, _ in LESSONS_CONFIG[mid]["lessons"]:
                level_total += 1
                if f"{mid}/{lid}" in completed:
                    level_completed += 1
        by_level[level_id] = {"done": level_completed, "total": level_total}
    return {"completed": completed, "total": total, "by_level": by_level}


@app.post("/api/progress")
def save_progress(
    req: ProgressRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Зберегти завершений урок."""
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")

    user_id = int(payload["sub"])
    progress = Progress(
        user_id=user_id,
        module_id=req.module_id,
        lesson_id=req.lesson_id,
        time_spent=max(0, req.time_spent),
    )
    db.add(progress)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Вже існує — оновлюємо час якщо переданий
        if req.time_spent > 0:
            existing = db.query(Progress).filter(
                Progress.user_id == user_id,
                Progress.module_id == req.module_id,
                Progress.lesson_id == req.lesson_id,
            ).first()
            if existing:
                existing.time_spent = (existing.time_spent or 0) + req.time_spent
                db.commit()
        return {"success": True, "message": "Вже збережено"}
    return {"success": True}


# === Code snapshots (збереження коду в БД) ===
@app.get("/api/code")
def get_code(
    module_id: str,
    lesson_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Отримати збережений код для уроку."""
    payload = get_current_user(authorization)
    if not payload:
        return {"code": None}

    user_id = int(payload["sub"])
    snap = db.query(CodeSnapshot).filter(
        CodeSnapshot.user_id == user_id,
        CodeSnapshot.module_id == module_id,
        CodeSnapshot.lesson_id == lesson_id,
    ).first()
    return {"code": snap.code if snap else None}


@app.post("/api/code")
def save_code(
    req: CodeRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Зберегти код для уроку в БД."""
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")

    user_id = int(payload["sub"])
    snap = db.query(CodeSnapshot).filter(
        CodeSnapshot.user_id == user_id,
        CodeSnapshot.module_id == req.module_id,
        CodeSnapshot.lesson_id == req.lesson_id,
    ).first()

    if snap:
        snap.code = req.code
    else:
        snap = CodeSnapshot(
            user_id=user_id,
            module_id=req.module_id,
            lesson_id=req.lesson_id,
            code=req.code,
        )
        db.add(snap)
    db.commit()
    return {"success": True}


# === Lessons (public) ===
@app.get("/api/levels")
def get_levels():
    """Список рівнів та модулів."""
    result = {}
    for level_id, level_cfg in LEVELS_CONFIG.items():
        result[level_id] = {
            "name": level_cfg["name"],
            "modules": [
                {
                    "id": mid,
                    "name": LESSONS_CONFIG[mid]["name"],
                    "lessons_count": len(LESSONS_CONFIG[mid]["lessons"]),
                }
                for mid in level_cfg["modules"]
            ],
        }
    return result


@app.get("/api/lessons/{module_id}")
def get_module_lessons(module_id: str):
    """Список уроків модуля."""
    if module_id not in LESSONS_CONFIG:
        raise HTTPException(404, "Module not found")
    return {
        "module": LESSONS_CONFIG[module_id]["name"],
        "lessons": [
            {"id": lid, "title": title}
            for lid, title in LESSONS_CONFIG[module_id]["lessons"]
        ],
    }


@app.get("/api/lessons/{module_id}/{lesson_id}")
def get_lesson_content(module_id: str, lesson_id: str):
    """Контент уроку: теорія, завдання, приклад, ресурси."""
    lesson_path = get_lesson_path(module_id, lesson_id)
    if not lesson_path.exists():
        raise HTTPException(404, "Lesson not found")

    resources = LESSON_RESOURCES.get(lesson_id, [])
    hints = LESSON_HINTS.get(lesson_id, [])
    meta = LESSON_META.get(lesson_id, {"difficulty": "medium", "time": "20 хв", "prev": None, "next": None})
    theory = _ensure_platform_local_notice(read_file_safe(lesson_path / "README.md"))
    task = _ensure_platform_local_notice(read_file_safe(lesson_path / "task.md"))
    return {
        "theory": theory,
        "task": task,
        "example": read_file_safe(lesson_path / "example.py"),
        "resources": resources,
        "hints": hints,
        "meta": meta,
    }


@app.get("/api/lessons/{module_id}/{lesson_id}/solution")
def get_lesson_solution(module_id: str, lesson_id: str):
    """Еталонне рішення (після успішної перевірки)."""
    path_key = (module_id, lesson_id)
    rel_path = SOLUTION_PATHS.get(path_key)
    if not rel_path:
        raise HTTPException(404, "Solution not found")
    full_path = BASE_DIR / rel_path
    if not full_path.exists():
        raise HTTPException(404, "Solution file not found")
    return {"solution": full_path.read_text(encoding="utf-8")}


@app.post("/api/run")
def run_user_code(req: RunCodeRequest, request: Request):
    """Запуск коду користувача."""
    ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(ip):
        raise HTTPException(429, "Забагато запитів. Зачекай хвилину.")
    try:
        result = run_code(req.code)
        return {
            "success": True,
            "output": result["output"],
            "error": result.get("error"),
            "debug": result.get("debug"),
        }
    except Exception as e:
        return {"success": False, "output": "", "error": str(e), "debug": None}


@app.post("/api/check")
def check_homework(
    req: CheckTaskRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Перевірка домашнього завдання."""
    try:
        result = check_task(req.lesson_id, req.code)
        payload = get_current_user(authorization)
        error_text = None
        if not result.get("passed") and result.get("details"):
            error_text = "\n".join(result.get("details", []))
        weak_topics = _detect_weak_topics(req.lesson_id, result.get("details", []), error_text)
        result["weak_topics"] = weak_topics
        result["smart_feedback"] = _build_smart_feedback(req.lesson_id, result.get("details", []), weak_topics)

        # Для авторизованих користувачів зберігаємо аналітику спроби
        if payload:
            user_id = int(payload["sub"])
            module_id = req.module_id or "unknown"
            attempt = LessonAttempt(
                user_id=user_id,
                module_id=module_id,
                lesson_id=req.lesson_id,
                passed=1 if result.get("passed") else 0,
                error_type=_extract_error_type(error_text),
                weak_topics=_safe_json_dump(weak_topics),
                feedback=result.get("message", ""),
            )
            db.add(attempt)
            # Spaced repetition: при невдачі одразу ставимо тему в review queue
            if not result.get("passed"):
                _upsert_review_items(user_id, module_id, req.lesson_id, weak_topics, db)
            # Мотивація: XP за кожну перевірку
            gamification = _award_xp_and_badges(user_id, db, bool(result.get("passed")))
            db.commit()
            result["gamification"] = gamification
        return result
    except Exception as e:
        return {"passed": False, "message": str(e), "details": []}


# === Time tracking ===
@app.post("/api/time")
def update_time(
    req: TimeRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Додати час до вже завершеного уроку."""
    payload = get_current_user(authorization)
    if not payload or req.seconds <= 0:
        return {"success": False}
    user_id = int(payload["sub"])
    prog = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.module_id == req.module_id,
        Progress.lesson_id == req.lesson_id,
    ).first()
    if prog:
        prog.time_spent = (prog.time_spent or 0) + req.seconds
        db.commit()
    return {"success": True}


# === Notes ===
@app.get("/api/notes")
def get_note(
    module_id: str,
    lesson_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Отримати нотатку для уроку."""
    payload = get_current_user(authorization)
    if not payload:
        return {"content": ""}
    user_id = int(payload["sub"])
    note = db.query(LessonNote).filter(
        LessonNote.user_id == user_id,
        LessonNote.module_id == module_id,
        LessonNote.lesson_id == lesson_id,
    ).first()
    return {"content": note.content if note else ""}


@app.post("/api/notes")
def save_note(
    req: NoteRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Зберегти нотатку для уроку."""
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")
    user_id = int(payload["sub"])
    note = db.query(LessonNote).filter(
        LessonNote.user_id == user_id,
        LessonNote.module_id == req.module_id,
        LessonNote.lesson_id == req.lesson_id,
    ).first()
    if note:
        note.content = req.content
    else:
        note = LessonNote(
            user_id=user_id,
            module_id=req.module_id,
            lesson_id=req.lesson_id,
            content=req.content,
        )
        db.add(note)
    db.commit()
    return {"success": True}


# === Code formatting ===
try:
    import black as _black
    _HAS_BLACK = True
except ImportError:
    _HAS_BLACK = False


@app.post("/api/format")
def format_code(req: RunCodeRequest):
    """Форматування Python-коду через black."""
    if not _HAS_BLACK:
        return {"success": False, "error": "black не встановлено"}
    try:
        formatted = _black.format_str(req.code, mode=_black.Mode())
        return {"success": True, "code": formatted}
    except Exception as e:
        return {"success": False, "error": str(e)}


# === Statistics ===
@app.get("/api/stats")
def get_stats(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Персональна статистика навчання."""
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")

    from collections import defaultdict
    from datetime import timezone as _tz

    user_id = int(payload["sub"])
    items = db.query(Progress).filter(Progress.user_id == user_id).all()

    total_completed = len(items)
    total_time = sum(p.time_spent or 0 for p in items)

    # Активність по днях
    daily: dict[str, int] = defaultdict(int)
    for p in items:
        if p.completed_at:
            day = p.completed_at.strftime("%Y-%m-%d")
            daily[day] += 1

    # Прогрес по рівнях
    by_level = {}
    for level_id, level_cfg in LEVELS_CONFIG.items():
        done = 0
        total_lvl = 0
        for mid in level_cfg["modules"]:
            for lid, _ in LESSONS_CONFIG[mid]["lessons"]:
                total_lvl += 1
                if any(p.module_id == mid and p.lesson_id == lid for p in items):
                    done += 1
        by_level[level_id] = {"done": done, "total": total_lvl, "name": level_cfg["name"]}

    # Час по урокам
    _epoch = datetime.min.replace(tzinfo=_tz.utc)
    lesson_times = [
        {
            "module_id": p.module_id,
            "lesson_id": p.lesson_id,
            "time_spent": p.time_spent or 0,
            "completed_at": p.completed_at.isoformat() if p.completed_at else None,
        }
        for p in sorted(items, key=lambda x: x.completed_at or _epoch)
    ]

    return {
        "total_completed": total_completed,
        "total_lessons": get_total_lessons(),
        "total_time_seconds": total_time,
        "by_level": by_level,
        "daily_activity": dict(daily),
        "lesson_times": lesson_times,
    }


@app.get("/api/adaptive/summary")
def adaptive_summary(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Зведення для adaptive route + weak topics + motivation."""
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")

    user_id = int(payload["sub"])
    completed_items = db.query(Progress).filter(Progress.user_id == user_id).all()
    completed_keys = {f"{p.module_id}/{p.lesson_id}" for p in completed_items}

    # weak topics з останніх невдалих спроб
    weak_counter: dict[str, int] = {}
    recent_fails = db.query(LessonAttempt).filter(
        LessonAttempt.user_id == user_id,
        LessonAttempt.passed == 0,
    ).order_by(LessonAttempt.created_at.desc()).limit(50).all()
    for attempt in recent_fails:
        for topic in _safe_json_load_list(attempt.weak_topics):
            weak_counter[topic] = weak_counter.get(topic, 0) + 1
    weak_topics = [{"topic": k, "count": v} for k, v in sorted(weak_counter.items(), key=lambda x: x[1], reverse=True)[:10]]

    # review queue
    now = datetime.now(timezone.utc)
    due_rows = db.query(ReviewQueue).filter(
        ReviewQueue.user_id == user_id,
        ReviewQueue.due_at <= now,
    ).order_by(ReviewQueue.due_at.asc()).limit(20).all()
    reviews_due = [{
        "module_id": r.module_id,
        "lesson_id": r.lesson_id,
        "topic": r.topic,
        "due_at": r.due_at.isoformat() if r.due_at else None,
        "repetitions": r.repetitions,
    } for r in due_rows]

    # next lessons recommendation (adaptive top-3)
    next_lessons = _recommend_lessons(completed_keys, weak_topics, reviews_due, top_n=3)
    next_lesson = next_lessons[0] if next_lessons else None

    # skill map
    done_lessons = {p.lesson_id for p in completed_items}
    skill_map = {}
    skill_lesson_matrix = {}
    for skill_name, skill_topics in SKILL_GROUPS.items():
        related_lessons = []
        for level in ("junior", "middle", "senior"):
            for mid in LEVELS_CONFIG[level]["modules"]:
                for lid, title in LESSONS_CONFIG[mid]["lessons"]:
                    topics = set(LESSON_TOPIC_MAP.get(lid, []))
                    if topics & skill_topics:
                        related_lessons.append((mid, lid, title))
        done_related = sum(1 for _mid, lid, _title in related_lessons if lid in done_lessons)
        total_related = len(related_lessons)
        skill_map[skill_name] = {
            "done": done_related,
            "total": total_related,
            "percent": round((done_related / total_related) * 100) if total_related else 0,
        }
        skill_lesson_matrix[skill_name] = [
            {
                "module_id": mid,
                "lesson_id": lid,
                "title": title,
                "done": lid in done_lessons,
            }
            for mid, lid, title in related_lessons
        ]

    gm = _get_or_create_gamification(user_id, db)
    badges = _safe_json_load_list(gm.badges)
    quests = _build_quests(user_id, db, gm.goal_preset or "balanced")
    db.commit()

    return {
        "weak_topics": weak_topics,
        "reviews_due_count": len(reviews_due),
        "reviews_due": reviews_due,
        "next_lesson": next_lesson,
        "next_lessons": next_lessons,
        "gamification": {"xp": gm.xp, "level": gm.level, "badges": badges, "goal_preset": gm.goal_preset or "balanced"},
        "quests": quests,
        "skill_map": skill_map,
        "skill_lesson_matrix": skill_lesson_matrix,
    }


@app.post("/api/review/complete")
def complete_review(
    req: ReviewCompleteRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Позначити повторення теми (spaced repetition update)."""
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")
    user_id = int(payload["sub"])
    row = db.query(ReviewQueue).filter(
        ReviewQueue.user_id == user_id,
        ReviewQueue.module_id == req.module_id,
        ReviewQueue.lesson_id == req.lesson_id,
        ReviewQueue.topic == req.topic,
    ).first()
    if not row:
        raise HTTPException(404, "Review item not found")

    if req.success:
        row.repetitions += 1
        row.interval_days = min(30, max(1, row.interval_days * 2))
        row.last_result = 1
    else:
        row.repetitions = 0
        row.interval_days = 1
        row.last_result = 0
    row.due_at = datetime.now(timezone.utc) + timedelta(days=row.interval_days)
    _award_xp_and_badges(user_id, db, req.success)
    db.commit()
    return {"success": True, "next_due_at": row.due_at.isoformat(), "interval_days": row.interval_days}


@app.get("/api/review/queue")
def get_review_queue(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Список тем для повторення (spaced repetition queue)."""
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")
    user_id = int(payload["sub"])
    now = datetime.now(timezone.utc)
    rows = db.query(ReviewQueue).filter(
        ReviewQueue.user_id == user_id,
    ).order_by(ReviewQueue.due_at.asc()).limit(200).all()

    def _is_overdue(dt: datetime | None) -> bool:
        if not dt:
            return False
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt <= now

    items = [{
        "module_id": r.module_id,
        "lesson_id": r.lesson_id,
        "topic": r.topic,
        "due_at": r.due_at.isoformat() if r.due_at else None,
        "overdue": _is_overdue(r.due_at),
        "interval_days": r.interval_days,
        "repetitions": r.repetitions,
        "last_result": r.last_result,
    } for r in rows]
    return {"items": items}


@app.post("/api/review/session")
def complete_review_session(
    req: ReviewSessionRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Завершення review-сесії (до 5 карток) з бонусом за серію."""
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")
    user_id = int(payload["sub"])
    now = datetime.now(timezone.utc)

    processed = 0
    successes = 0
    for item in req.items[:5]:
        row = db.query(ReviewQueue).filter(
            ReviewQueue.user_id == user_id,
            ReviewQueue.module_id == item.module_id,
            ReviewQueue.lesson_id == item.lesson_id,
            ReviewQueue.topic == item.topic,
        ).first()
        if not row:
            continue
        processed += 1
        if item.success:
            successes += 1
            row.repetitions += 1
            row.interval_days = min(30, max(1, row.interval_days * 2))
            row.last_result = 1
        else:
            row.repetitions = 0
            row.interval_days = 1
            row.last_result = 0
        row.due_at = now + timedelta(days=row.interval_days)

    # Базове XP за відповіді
    gm = _get_or_create_gamification(user_id, db)
    gm.xp += successes * 5 + (processed - successes) * 1

    bonus_xp = 0
    if processed >= 5 and successes >= 4:
        bonus_xp = 25
        gm.xp += bonus_xp
        badges = _safe_json_load_list(gm.badges)
        if "Review Sprint" not in badges:
            badges.append("Review Sprint")
        gm.badges = _safe_json_dump(badges)
    gm.level = 1 + (gm.xp // 200)
    db.commit()
    return {
        "success": True,
        "processed": processed,
        "successes": successes,
        "bonus_xp": bonus_xp,
        "xp": gm.xp,
        "level": gm.level,
    }


@app.get("/api/goals/preset")
def get_goal_preset(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")
    user_id = int(payload["sub"])
    gm = _get_or_create_gamification(user_id, db)
    db.commit()
    return {
        "preset": gm.goal_preset or "balanced",
        "available": ["easy", "balanced", "intensive", "weekend"],
    }


@app.get("/api/plan/weekly")
def get_weekly_plan(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Персональний план на 7 днів."""
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")

    user_id = int(payload["sub"])
    gm = _get_or_create_gamification(user_id, db)

    # Reuse adaptive ingredients
    completed_items = db.query(Progress).filter(Progress.user_id == user_id).all()
    completed_keys = {f"{p.module_id}/{p.lesson_id}" for p in completed_items}

    weak_counter: dict[str, int] = {}
    recent_fails = db.query(LessonAttempt).filter(
        LessonAttempt.user_id == user_id,
        LessonAttempt.passed == 0,
    ).order_by(LessonAttempt.created_at.desc()).limit(50).all()
    for attempt in recent_fails:
        for topic in _safe_json_load_list(attempt.weak_topics):
            weak_counter[topic] = weak_counter.get(topic, 0) + 1
    weak_topics = [{"topic": k, "count": v} for k, v in sorted(weak_counter.items(), key=lambda x: x[1], reverse=True)[:10]]

    now = datetime.now(timezone.utc)
    due_rows = db.query(ReviewQueue).filter(
        ReviewQueue.user_id == user_id,
        ReviewQueue.due_at <= now,
    ).order_by(ReviewQueue.due_at.asc()).limit(50).all()
    reviews_due = [{
        "module_id": r.module_id,
        "lesson_id": r.lesson_id,
        "topic": r.topic,
    } for r in due_rows]

    next_lessons = _recommend_lessons(completed_keys, weak_topics, reviews_due, top_n=10)
    days = _build_weekly_plan(gm.goal_preset or "balanced", next_lessons, reviews_due, weak_topics)
    # Накласти користувацькі дії по задачах плану
    date_set = {d["date"] for d in days}
    states = db.query(WeeklyPlanTaskState).filter(
        WeeklyPlanTaskState.user_id == user_id,
        WeeklyPlanTaskState.plan_date.in_(list(date_set)),
    ).all()
    days = _apply_plan_states(days, states)

    db.commit()
    return {
        "preset": gm.goal_preset or "balanced",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
    }


@app.post("/api/plan/task-action")
def plan_task_action(
    req: PlanTaskActionRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Відмітити задачу у плані: done/skip/snooze."""
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")
    allowed = {"done", "skip", "snooze", "pending"}
    if req.action not in allowed:
        raise HTTPException(400, "Невідома дія")
    user_id = int(payload["sub"])
    row = db.query(WeeklyPlanTaskState).filter(
        WeeklyPlanTaskState.user_id == user_id,
        WeeklyPlanTaskState.plan_date == req.plan_date,
        WeeklyPlanTaskState.task_key == req.task_key,
    ).first()
    if req.action == "pending":
        if row:
            db.delete(row)
    else:
        if row:
            row.action = req.action
        else:
            row = WeeklyPlanTaskState(
                user_id=user_id,
                plan_date=req.plan_date,
                task_key=req.task_key,
                action=req.action,
            )
            db.add(row)

    # Малий XP-бонус за done
    if req.action == "done":
        gm = _get_or_create_gamification(user_id, db)
        gm.xp += 4
        gm.level = 1 + (gm.xp // 200)

    db.commit()
    return {"success": True}


@app.post("/api/goals/preset")
def set_goal_preset(
    req: GoalPresetRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    payload = get_current_user(authorization)
    if not payload:
        raise HTTPException(401, "Не авторизовано")
    allowed = {"easy", "balanced", "intensive", "weekend"}
    if req.preset not in allowed:
        raise HTTPException(400, "Невідомий preset")
    user_id = int(payload["sub"])
    gm = _get_or_create_gamification(user_id, db)
    gm.goal_preset = req.preset
    db.commit()
    return {"success": True, "preset": gm.goal_preset}


# === Static files (Vue 3 SPA) ===
_BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = _BACKEND_DIR.parent / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"

if DIST_DIR.exists():
    # Production: serve Vite build output
    _assets_dir = DIST_DIR / "assets"
    if _assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="vue_assets")

    @app.get("/manifest.json")
    def manifest():
        return FileResponse(DIST_DIR / "manifest.json")

    @app.get("/sw.js")
    def service_worker():
        return FileResponse(
            DIST_DIR / "sw.js",
            headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"},
        )

    # SPA catch-all: all non-API routes return index.html
    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        index = DIST_DIR / "index.html"
        if index.exists():
            return FileResponse(index)
        raise HTTPException(status_code=404, detail="Frontend not built. Run: cd web/frontend && npm run build")

elif FRONTEND_DIR.exists():
    # Development fallback: old static file layout
    _static = FRONTEND_DIR / "static"
    if _static.exists():
        app.mount("/static", StaticFiles(directory=_static), name="static")

    @app.get("/manifest.json")
    def manifest_dev():
        return FileResponse(FRONTEND_DIR / "manifest.json")

    @app.get("/sw.js")
    def service_worker_dev():
        return FileResponse(
            FRONTEND_DIR / "sw.js",
            headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"},
        )

    @app.get("/{full_path:path}")
    def spa_fallback_dev(full_path: str):
        return FileResponse(FRONTEND_DIR / "index.html")
