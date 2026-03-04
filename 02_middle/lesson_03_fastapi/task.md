# Завдання — FastAPI

## Завдання 1 — CRUD для TODO
Реалізуй повноцінний CRUD для `Todo`:
- `GET /todos/` — список з query: `done: bool | None`, `page`, `per_page`
- `GET /todos/{id}` — один (404 якщо немає)
- `POST /todos/` — створити (201)
- `PUT /todos/{id}` — оновити повністю
- `PATCH /todos/{id}` — оновити частково
- `DELETE /todos/{id}` — видалити (204)

Pydantic схеми: `TodoCreate`, `TodoUpdate`, `TodoResponse`.

## Завдання 2 — Валідація Pydantic
Схема `UserRegistration`:
- `username`: 3-50 символів, тільки [a-zA-Z0-9_]
- `email`: валідний email
- `password`: мінімум 8 символів, хоч одна цифра, хоч одна велика буква
- `birth_date`: дата, вік 13-120 років
- `@model_validator`: переконатись що `password != username`

## Завдання 3 — Depends ланцюг
Напиши залежності:
- `get_db()` — повертає InMemory dict "БД"
- `get_current_user(token, db)` — декодує token (просто `"user:{id}"`), повертає user
- `require_admin(user)` — перевіряє role

Захисти `DELETE /users/{id}` через `require_admin`.

## Завдання 4 — Middleware
Напиши middleware що:
1. Додає заголовок `X-Request-ID: <uuid>` до кожної відповіді
2. Логує `METHOD PATH → STATUS (Xms)`
3. Повертає 429 якщо більше 10 запитів за 60 секунд з одного IP

## Завдання 5 (Challenge) — Повноцінний мінімальний блог API
`POST /register`, `POST /login` (JWT), `GET /me`,
`GET/POST /posts/`, `GET/PUT/DELETE /posts/{id}` (тільки автор),
`POST /posts/{id}/like`, `GET /posts/{id}/likes`.
