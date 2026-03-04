# Завдання — System Design

## Завдання 1 — LRU Cache
Реалізуй `LRUCache(capacity)` з O(1) get/put:
- `get(key)` → value або -1
- `put(key, value)` → якщо capacity досягнуто, видаляє least recently used
Підказка: `OrderedDict` або Doubly Linked List + HashMap.

## Завдання 2 — Rate Limiter
Реалізуй `TokenBucketLimiter(capacity, refill_rate)` і `SlidingWindowLimiter(max_req, window_sec)`.
Напиши декоратор `@rate_limit(limiter)` для FastAPI ендпоінту.
Тест: 10 запитів за 5 секунд при ліміті 3/секунду.

## Завдання 3 — Кешування API результатів
Напиши `@cached(ttl=60, key_fn=None)` декоратор що:
- Генерує ключ кешу з назви функції + аргументів
- Підтримує кастомний `key_fn`
- Підтримує інвалідацію за префіксом (`cache.invalidate_prefix("user:")`)

## Завдання 4 — Connection Pool
Реалізуй простий `ConnectionPool(factory, min_size, max_size)`:
- `acquire()` → повертає з'єднання (чекає якщо всі зайняті)
- `release(conn)` → повертає в пул
- Через async context manager

## Завдання 5 (Challenge) — Distributed Counter
Реалізуй thread-safe лічильник використовуючи:
a) `threading.Lock`  b) `asyncio.Lock`  c) `threading.atomic` (через Queue)
Перевір race conditions: 100 потоків × 1000 інкрементів = рівно 100,000.
