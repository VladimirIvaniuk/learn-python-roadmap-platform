"""
Урок Middle 4 — Приклади: SQLAlchemy ORM
"""
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import (
    String, Integer, Boolean, ForeignKey, DateTime, Text,
    create_engine, select, func, and_, desc
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship,
    Session, selectinload
)


# ── Моделі ────────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    posts: Mapped[list[Post]] = relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped[User] = relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"Post(id={self.id}, title={self.title!r})"


# ── Ініціалізація ─────────────────────────────────────────────────────────────
engine = create_engine("sqlite:///:memory:", echo=False)
Base.metadata.create_all(engine)


def seed():
    with Session(engine) as db:
        users = [
            User(username="alice", email="alice@example.com"),
            User(username="bob",   email="bob@example.com"),
            User(username="carol", email="carol@example.com"),
        ]
        db.add_all(users)
        db.flush()

        posts = [
            Post(title="Hello Python", body="Python is great!", published=True, author_id=users[0].id),
            Post(title="FastAPI tips",  body="Use Depends!",     published=True, author_id=users[0].id),
            Post(title="Draft post",    body="Work in progress", published=False, author_id=users[1].id),
            Post(title="SQL basics",    body="SELECT * ...",     published=True, author_id=users[1].id),
        ]
        db.add_all(posts)
        db.commit()

seed()

# ── CRUD ──────────────────────────────────────────────────────────────────────
with Session(engine) as db:
    print("=== READ ===")

    # get by pk
    user = db.get(User, 1)
    print(f"User by id: {user}")

    # select з умовою
    stmt = select(User).where(User.is_active == True).order_by(User.username)
    users = db.execute(stmt).scalars().all()
    print(f"Active users: {users}")

    # scalar_one_or_none
    alice = db.execute(select(User).where(User.username == "alice")).scalar_one_or_none()
    print(f"Alice: {alice}")

    print("\n=== N+1 FIX: Eager Loading ===")
    # ✅ selectinload — дозволяє уникнути N+1
    stmt = (
        select(User)
        .options(selectinload(User.posts))
        .where(User.is_active == True)
    )
    users_with_posts = db.execute(stmt).scalars().all()
    for u in users_with_posts:
        print(f"  {u.username}: {len(u.posts)} постів")

    print("\n=== AGGREGATION ===")
    result = db.execute(
        select(User.username, func.count(Post.id).label("post_count"))
        .join(Post, Post.author_id == User.id)
        .group_by(User.id)
        .order_by(desc("post_count"))
    ).all()
    for username, count in result:
        print(f"  {username}: {count} постів")

    print("\n=== UPDATE ===")
    alice = db.get(User, 1)
    alice.is_active = False
    db.commit()
    db.refresh(alice)
    print(f"Alice active: {alice.is_active}")

    print("\n=== Bulk operations ===")
    from sqlalchemy import update as sa_update
    db.execute(
        sa_update(User).where(User.is_active == False).values({"is_active": True})
    )
    db.commit()
    print("Всі користувачі знову активні")
