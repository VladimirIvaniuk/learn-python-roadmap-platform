# Завдання — Безпека

## Завдання 1 — JWT повна реалізація
Реалізуй `TokenService` з:
- `create_access_token(user_id, role)` — TTL 15 хвилин
- `create_refresh_token(user_id)` — TTL 30 днів
- `verify_token(token)` — перевіряє підпис, термін, тип
- `refresh(refresh_token)` — видає новий access token
- `revoke(token)` — додає в blacklist (InMemory Set)

## Завдання 2 — Password Policy
Клас `PasswordPolicy` з правилами:
- Мінімальна довжина
- Обов'язкові символи (цифри, спецсимволи, великі)
- Перевірка на популярні паролі (простий список)
- `validate(password)` → `list[str]` помилки або `[]`
Хешуй через bcrypt.

## Завдання 3 — SQL Injection Demo
Напиши функцію `safe_search(query: str) -> list`:
- Приймає рядок пошуку
- Показує ВРАЗЛИВУ версію (через f-string у raw SQL)
- Показує БЕЗПЕЧНУ версію (параметризований запит)
- Демонструй атаку: `query = "' OR '1'='1"` на вразливу версію

## Завдання 4 — Input Sanitization
Напиши `FileUploadValidator`:
- Перевірка розширення через whitelist (не blacklist!)
- Перевірка magic bytes (перші байти файлу)
- Захист від path traversal (`../../../etc/passwd`)
- Обмеження розміру файлу

## Завдання 5 (Challenge) — Security Audit
Проведи аудит `web/backend/main.py`:
- Знайди всі потенційні security вразливості
- Класифікуй за OWASP категоріями
- Запропонуй і реалізуй виправлення
