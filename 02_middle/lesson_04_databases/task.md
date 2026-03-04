# Завдання — Бази даних

## Завдання 1 — Модель та CRUD
Створи SQLAlchemy модель `Product(id, name, price, category, in_stock, created_at)`.
Напиши функції:
- `create_product(db, data) → Product`
- `get_product(db, id) → Product | None`
- `list_products(db, category=None, min_price=None) → list[Product]`
- `update_price(db, id, new_price) → Product | None`
- `delete_product(db, id) → bool`

## Завдання 2 — Зв'язки
Модель `Author(id, name, bio)` та `Book(id, title, author_id, year, isbn)`.
Реалізуй `Many-to-Many` між `Book` та `Genre`.
Запит: знайти всіх авторів у яких є хоч одна книга жанру "Fantasy" після 2000 року.

## Завдання 3 — N+1 Fix
Ось код з N+1 проблемою — виправ:
```python
authors = db.execute(select(Author)).scalars().all()
for author in authors:
    print(f"{author.name}: {len(author.books)} книг")
```
Переконайся що виконується тільки 2 запити (не N+1).

## Завдання 4 — Агрегація
Використовуючи `func`, напиши запити:
1. Кількість продуктів по категоріях
2. Середня ціна по категоріях (тільки ті де > 5 продуктів)
3. Топ-3 найдорожчих продукти в кожній категорії

## Завдання 5 (Challenge) — Async репозиторій
Реалізуй `UserRepository` з async методами:
`create`, `get_by_id`, `get_by_email`, `update`, `delete`, `list(page, per_page)`.
Напиши тести для всіх методів використовуючи SQLite in-memory.
