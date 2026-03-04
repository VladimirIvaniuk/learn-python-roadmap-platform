# Завдання — Asyncio

## Завдання 1 — Порівняння sync vs async
Напиши `fetch_urls_sync(urls)` (через `time.sleep(0.5)` замість HTTP)
і `fetch_urls_async(urls)` (через `asyncio.sleep(0.5)`).
Порівняй час для 10 URL через `time.perf_counter()`.

## Завдання 2 — Rate limiter
Напиши `rate_limited_fetch(urls, max_concurrent=3)` що одночасно
виконує максимум 3 запити через `asyncio.Semaphore`.

## Завдання 3 — Producer/Consumer
Реалізуй обробник задач:
- `producer` генерує числа від 1 до 20 з паузою 0.1с, кладе в `Queue`
- 3 `worker`-и читають з черги, рахують квадрат числа (пауза 0.2с), виводять
- Після 20 чисел все зупиняється

## Завдання 4 — Timeout та retry
Напиши `fetch_with_retry(url, retries=3, timeout=2.0)` що:
- Виконує "запит" (mock: 50% шанс `asyncio.TimeoutError`)
- Повторює до `retries` разів при помилці
- Чекає 2^attempt секунди між спробами (exponential backoff)

## Завдання 5 (Challenge) — Async pipeline
Побудуй async pipeline: `source → filter → transform → sink`
де кожен крок — окрема корутина + `Queue`.
`source`: числа 1-50, `filter`: тільки непарні, `transform`: x**2, `sink`: виводить результати.
