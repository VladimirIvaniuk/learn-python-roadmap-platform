# Завдання — Design Patterns

## Завдання 1 — Factory Registry
Реалізуй `NotificationFactory` з реєстром каналів.
Підтримай реєстрацію нових каналів без модифікації фабрики (`register(name, cls)`).
Канали: Email, SMS, Telegram, Push.

## Завдання 2 — Builder для HTTP Response
`ResponseBuilder` з методами:
`.status(code)`, `.header(key, value)`, `.body(data)`, `.paginate(page, total, per_page)`.
`.build()` повертає `dict` з відповідним форматом.

## Завдання 3 — Observer: Event Bus
Реалізуй `EventBus` з підтримкою:
- `subscribe(event_name, handler)` — підписатись
- `emit(event_name, **data)` — оповістити
- `unsubscribe(event_name, handler)` — відписатись
- Підтримка async handlers

## Завдання 4 — Chain of Responsibility
Побудуй pipeline обробки HTTP запиту:
`AuthHandler → RateLimitHandler → ValidationHandler → BusinessLogicHandler`
Кожен або передає далі або повертає помилку.
Запит = `dict(headers, body, ip)`.

## Завдання 5 (Challenge) — Composite паттерн
Реалізуй дерево файлової системи:
`File(name, size)` та `Directory(name, [children])`.
Методи: `total_size()`, `find(name)`, `print_tree(indent=0)`.
Використовуй рекурсію.
