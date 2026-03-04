"""
База даних: користувачі та прогрес навчання.
"""
from pathlib import Path
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, UniqueConstraint, text
from sqlalchemy.orm import declarative_base, sessionmaker

_BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = _BASE_DIR / "web" / "learn_python.db"

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)


class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    module_id = Column(String(50), nullable=False)
    lesson_id = Column(String(50), nullable=False)
    completed_at = Column(DateTime(timezone=True), default=_now)
    time_spent = Column(Integer, default=0)  # секунди

    __table_args__ = (
        UniqueConstraint("user_id", "module_id", "lesson_id", name="uq_progress_user_module_lesson"),
    )


class CodeSnapshot(Base):
    """Збережений код користувача для уроку."""
    __tablename__ = "code_snapshots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    module_id = Column(String(50), nullable=False)
    lesson_id = Column(String(50), nullable=False)
    code = Column(Text, nullable=False, default="")
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        UniqueConstraint("user_id", "module_id", "lesson_id", name="uq_snapshot_user_module_lesson"),
    )


class LessonNote(Base):
    """Особисті нотатки користувача до уроку."""
    __tablename__ = "lesson_notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    module_id = Column(String(50), nullable=False)
    lesson_id = Column(String(50), nullable=False)
    content = Column(Text, nullable=False, default="")
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        UniqueConstraint("user_id", "module_id", "lesson_id", name="uq_note_user_module_lesson"),
    )


class LessonAttempt(Base):
    """Історія перевірок/спроб користувача для адаптивного навчання."""
    __tablename__ = "lesson_attempts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    module_id = Column(String(50), nullable=False)
    lesson_id = Column(String(50), nullable=False)
    passed = Column(Integer, nullable=False, default=0)  # 0/1 для SQLite сумісності
    error_type = Column(String(80), nullable=True)
    weak_topics = Column(Text, nullable=False, default="[]")  # JSON list[str]
    feedback = Column(Text, nullable=False, default="")       # коротке пояснення/summary
    created_at = Column(DateTime(timezone=True), default=_now)


class ReviewQueue(Base):
    """Черга повторення тем (spaced repetition)."""
    __tablename__ = "review_queue"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    module_id = Column(String(50), nullable=False)
    lesson_id = Column(String(50), nullable=False)
    topic = Column(String(120), nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    interval_days = Column(Integer, nullable=False, default=1)
    repetitions = Column(Integer, nullable=False, default=0)
    last_result = Column(Integer, nullable=False, default=0)  # 0=fail, 1=pass
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        UniqueConstraint("user_id", "module_id", "lesson_id", "topic", name="uq_review_user_lesson_topic"),
    )


class UserGamification(Base):
    """Мотиваційний шар: XP, рівень, бейджі."""
    __tablename__ = "user_gamification"
    user_id = Column(Integer, primary_key=True)
    xp = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    badges = Column(Text, nullable=False, default="[]")  # JSON list[str]
    goal_preset = Column(String(20), nullable=False, default="balanced")  # easy|balanced|intensive|weekend
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class WeeklyPlanTaskState(Base):
    """Стан задачі у персональному плані (done/skip/snooze)."""
    __tablename__ = "weekly_plan_task_states"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    plan_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    task_key = Column(String(255), nullable=False)
    action = Column(String(20), nullable=False)  # done|skip|snooze
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    __table_args__ = (
        UniqueConstraint("user_id", "plan_date", "task_key", name="uq_plan_task_state"),
    )


def _migrate_db() -> None:
    """Легкі міграції для існуючих БД (додаємо нові колонки)."""
    with engine.connect() as conn:
        for stmt in [
            "ALTER TABLE progress ADD COLUMN time_spent INTEGER DEFAULT 0",
            "ALTER TABLE user_gamification ADD COLUMN goal_preset VARCHAR(20) DEFAULT 'balanced'",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                pass  # Колонка вже існує


def init_db() -> None:
    Base.metadata.create_all(engine)
    _migrate_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
