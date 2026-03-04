# Урок 4 — Бази даних: SQLAlchemy та SQL

## Що вивчимо
- Що таке ORM і навіщо
- Декларативні моделі SQLAlchemy 2.0
- Основні типи зв'язків: One-to-Many, Many-to-Many
- CRUD операції через ORM та raw SQL
- Міграції через Alembic
- Async SQLAlchemy з FastAPI
- N+1 проблема та eager loading
- Індекси та оптимізація запитів

---

## Теорія

### 1. Навіщо ORM?

```python
# Без ORM — вручну SQL і маппінг
import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Аліса", "a@b.com"))
conn.commit()
row = cursor.execute("SELECT * FROM users WHERE id = 1").fetchone()
user = {"id": row[0], "name": row[1], "email": row[2]}   # ручний маппінг!

# З SQLAlchemy ORM — Python класи замість SQL
user = User(name="Аліса", email="a@b.com")
db.add(user)
db.commit()
db.refresh(user)   # отримуємо id і defaults з БД
user = db.get(User, 1)   # → автоматично User об'єкт
```

---

### 2. Декларативні моделі (SQLAlchemy 2.0)

```python
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # One-to-Many: user → posts
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author",
                                                cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False)

    # Many-to-One: post → user
    author: Mapped[User] = relationship("User", back_populates="posts")
    # Many-to-Many: post ↔ tags
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary="post_tags", back_populates="posts")


# Association table для Many-to-Many
from sqlalchemy import Table, Column
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    posts: Mapped[list[Post]] = relationship("Post", secondary="post_tags", back_populates="tags")
```

---

### 3. CRUD операції

```python
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///app.db", echo=False)
Base.metadata.create_all(engine)

with Session(engine) as db:
    # CREATE
    user = User(username="alice", email="alice@example.com", hashed_password="hash")
    db.add(user)
    db.flush()    # відправляє SQL без commit (id вже доступний)
    print(user.id)  # є!
    db.commit()
    db.refresh(user)

    # READ (SQLAlchemy 2.0 стиль)
    stmt = select(User).where(User.is_active == True).order_by(User.username)
    users = db.execute(stmt).scalars().all()

    # Один запис
    user = db.get(User, 1)                              # по primary key
    user = db.execute(
        select(User).where(User.username == "alice")
    ).scalar_one_or_none()                              # None якщо немає

    # UPDATE
    user.is_active = False
    db.commit()   # ORM автоматично трекає зміни (Unit of Work)

    # Bulk update (ефективніше для великих наборів)
    db.execute(
        update(User).where(User.is_active == False).values({"role": "inactive"})
    )
    db.commit()

    # DELETE
    db.delete(user)
    db.commit()

    # Bulk delete
    db.execute(delete(User).where(User.created_at < some_date))
    db.commit()
```

---

### 4. Складніші запити

```python
from sqlalchemy import func, and_, or_, desc, asc

with Session(engine) as db:
    # JOIN
    stmt = (
        select(Post, User.username)
        .join(User, Post.author_id == User.id)
        .where(Post.published == True)
        .order_by(desc(Post.id))
        .limit(10)
    )
    posts_with_authors = db.execute(stmt).all()

    # Агрегація
    result = db.execute(
        select(User.is_active, func.count(User.id).label("count"))
        .group_by(User.is_active)
    ).all()

    # Підзапити
    avg_posts = select(func.avg(func.count(Post.id))).scalar_subquery()

    # Фільтри
    stmt = select(User).where(
        and_(
            User.is_active == True,
            or_(
                User.username.like("%admin%"),
                User.email.endswith("@company.com"),
            )
        )
    )

    # Пагінація
    page, per_page = 2, 20
    stmt = select(Post).order_by(Post.id).offset((page-1)*per_page).limit(per_page)
```

---

### 5. N+1 проблема та eager loading

```python
# ❌ N+1 — 1 запит для списку + N запитів для кожного зв'язаного об'єкта
users = db.execute(select(User)).scalars().all()
for user in users:
    print(user.posts)   # ← КОЖЕН раз новий SQL запит!
# Загалом 1 + N запитів

# ✅ Eager loading — всі дані в одному запиті
from sqlalchemy.orm import selectinload, joinedload

# selectinload — окремий SELECT ... IN (ids)  (для lists)
stmt = select(User).options(selectinload(User.posts))
users = db.execute(stmt).scalars().all()
for user in users:
    print(user.posts)   # вже в пам'яті, нових запитів немає!

# joinedload — JOIN (для single object)
stmt = select(Post).options(joinedload(Post.author))
posts = db.execute(stmt).scalars().unique().all()
```

---

### 6. Async SQLAlchemy з FastAPI

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///app.db", echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Dependency для FastAPI
async def get_db():
    async with async_session() as session:
        yield session

# CRUD з async
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Не знайдено")
    return user

@app.get("/users/")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .options(selectinload(User.posts))
        .where(User.is_active == True)
        .order_by(User.id)
    )
    return result.scalars().all()
```

---

### 7. Alembic — міграції

```bash
# Ініціалізація
pip install alembic
alembic init alembic

# alembic/env.py — підключаємо модель
from models import Base
target_metadata = Base.metadata

# Створення міграції
alembic revision --autogenerate -m "add users table"

# Застосування
alembic upgrade head

# Відкат на одну версію назад
alembic downgrade -1

# Перегляд історії
alembic history
```

---

### Типові помилки

```python
# ❌ Відкритий session без закриття
db = Session(engine)
user = db.get(User, 1)
# db.close() забули! — витік з'єднань

# ✅ Завжди через with або FastAPI Depends
with Session(engine) as db:
    user = db.get(User, 1)

# ❌ Detached instance — звернення до lazy-loaded після закриття сесії
with Session(engine) as db:
    user = db.get(User, 1)
user.posts   # ← DetachedInstanceError! session вже закрита

# ✅ Eager load або тримай сесію відкритою
with Session(engine) as db:
    user = db.execute(select(User).options(selectinload(User.posts))
                      .where(User.id == 1)).scalar_one()
posts = user.posts   # OK — вже завантажені

# ❌ N+1 без помітки
for user in db.execute(select(User)).scalars():
    send_email_to(user, user.posts)   # N+1!
```

---

## Що маєш вміти після уроку
- [ ] Написати SQLAlchemy модель з типовими зв'язками
- [ ] Виконати всі CRUD операції через ORM
- [ ] Пояснити і виправити N+1 проблему через `selectinload`
- [ ] Написати async SQLAlchemy dependency для FastAPI
- [ ] Створити міграцію через Alembic

---

## Що далі
`task.md`. Потім — **Урок 5: Тестування**.
