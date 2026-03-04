"""
Розв'язки — SQLAlchemy Databases (Middle)
"""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Column, ForeignKey, Integer, String, Float, DateTime, Table,
    create_engine, select, func, update, and_
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship,
    Session, selectinload
)

engine = create_engine("sqlite:///:memory:", echo=False)

# ─────────────── Models ───────────────────────────────────────────────────────
class Base(DeclarativeBase): pass

book_genre = Table(
    "book_genre", Base.metadata,
    Column("book_id",  ForeignKey("books.id"),  primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    books: Mapped[list["Book"]] = relationship("Book", back_populates="author",
                                               lazy="selectin")

    def __repr__(self) -> str:
        return f"Author({self.name!r})"

class Genre(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    books: Mapped[list["Book"]] = relationship("Book", secondary=book_genre,
                                               back_populates="genres")

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(Float, default=0.0)
    year: Mapped[int] = mapped_column(Integer, default=2024)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship("Author", back_populates="books")
    genres: Mapped[list["Genre"]] = relationship("Genre", secondary=book_genre,
                                                  back_populates="books")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# ─────────────── Seed ─────────────────────────────────────────────────────────
def seed():
    with Session(engine) as s:
        fiction = Genre(name="Fiction")
        sci_fi  = Genre(name="Sci-Fi")
        classic = Genre(name="Classic")

        orwell = Author(name="Orwell")
        tolkien = Author(name="Tolkien")

        book1 = Book(title="1984", price=9.99, year=1949, author=orwell,
                     genres=[fiction, classic])
        book2 = Book(title="Animal Farm", price=7.99, year=1945, author=orwell,
                     genres=[fiction, classic])
        book3 = Book(title="LOTR", price=24.99, year=1954, author=tolkien,
                     genres=[fiction, sci_fi])

        for p in [Product(name="Keyboard", price=79.99, stock=15),
                  Product(name="Monitor", price=349.99, stock=5),
                  Product(name="Mouse", price=29.99, stock=30)]:
            s.add(p)

        s.add_all([book1, book2, book3])
        s.commit()

seed()

# ── Завдання 1 — Product CRUD ─────────────────────────────────────────────────
with Session(engine) as s:
    # Read all
    products = s.scalars(select(Product)).all()
    print("Products:", [p.name for p in products])

    # Update price
    s.execute(update(Product).where(Product.name == "Mouse").values(price=34.99))
    s.commit()

    # Aggregate
    agg = s.execute(
        select(func.count(), func.min(Product.price), func.max(Product.price), func.avg(Product.price))
    ).one()
    print(f"Agg: count={agg[0]}, min={agg[1]}, max={agg[2]}, avg={agg[3]:.2f}")

# ── Завдання 2 — Author/Book/Genre ────────────────────────────────────────────
with Session(engine) as s:
    authors = s.scalars(select(Author).options(selectinload(Author.books))).all()
    for a in authors:
        print(f"\n{a}: {len(a.books)} book(s)")
        for b in a.books:
            print(f"  - {b.title} ({b.year})")

# ── Завдання 3 — N+1 fix already done via selectin ───────────────────────────
with Session(engine) as s:
    books = s.scalars(
        select(Book).options(selectinload(Book.genres))
    ).all()
    print("\n[eager load] genres per book:")
    for b in books:
        print(f"  {b.title}: {[g.name for g in b.genres]}")

# ── Завдання 4 — Aggregation queries ─────────────────────────────────────────
with Session(engine) as s:
    # Кількість книг на автора
    author_books = s.execute(
        select(Author.name, func.count(Book.id).label("cnt"))
        .join(Book, Book.author_id == Author.id)
        .group_by(Author.id)
        .order_by(func.count(Book.id).desc())
    ).all()
    print("\nBooks per author:")
    for row in author_books:
        print(f"  {row.name}: {row.cnt}")

    # Середня ціна по жанру
    from sqlalchemy import Float as SAFloat
    avg_by_genre = s.execute(
        select(Genre.name, func.avg(Book.price).label("avg_price"))
        .join(book_genre, Genre.id == book_genre.c.genre_id)
        .join(Book, Book.id == book_genre.c.book_id)
        .group_by(Genre.id)
    ).all()
    print("\nAvg price per genre:")
    for row in avg_by_genre:
        print(f"  {row.name}: {row.avg_price:.2f}")
