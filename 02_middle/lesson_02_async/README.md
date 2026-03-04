# Урок 2 — Асинхронність: asyncio, async/await

## Що вивчимо
- Чому асинхронність (event loop, I/O-bound vs CPU-bound)
- `async def`, `await`, `asyncio.run()`
- `asyncio.gather()`, `asyncio.create_task()`, `asyncio.TaskGroup`
- `asyncio.Queue`, `asyncio.Lock`, `asyncio.Semaphore`
- Типові пастки: blocking calls в async, cancellation
- `aiofiles`, `httpx` — async I/O у реальних проєктах
- `threading` та `multiprocessing` — коротко коли що

---

## Теорія

### 1. Навіщо асинхронність?

```
Синхронний (блокуючий):
  Запит 1 →→→→→→→→→→ відповідь 1
                               Запит 2 →→→→→→→→→→ відповідь 2
  Загальний час: 10с + 10с = 20с

Асинхронний (не блокуючий):
  Запит 1 →→ (чекаємо, перемикаємось) →→ відповідь 1
  Запит 2 →→ (чекаємо одночасно)     →→ відповідь 2
  Загальний час: ~10с (паралельно!)
```

**Event Loop** — серце asyncio. Це нескінченний цикл, що:
1. Бере задачу
2. Виконує до `await`
3. Якщо `await` чекає — бере наступну задачу
4. Повертається до першої задачі, коли очікування завершилось

---

### 2. Базовий синтаксис

```python
import asyncio

# async def → coroutine function, при виклику повертає coroutine object
async def fetch_user(user_id: int) -> dict:
    await asyncio.sleep(0.1)   # імітація HTTP запиту
    return {"id": user_id, "name": f"User {user_id}"}

async def main():
    # await чекає результат корутини
    user = await fetch_user(42)
    print(user)

# asyncio.run() — єдина точка входу в event loop
asyncio.run(main())

# Перевір: coroutine ТРЕБА await, інакше вона не виконається!
async def demo():
    result = fetch_user(1)   # ❌ Warning: coroutine was never awaited
    result = await fetch_user(1)   # ✅
```

---

### 3. `asyncio.gather()` — паралельне виконання

```python
import asyncio, time

async def slow_task(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} готово"

async def sequential():
    t = time.perf_counter()
    r1 = await slow_task("A", 1.0)
    r2 = await slow_task("B", 1.0)
    r3 = await slow_task("C", 1.0)
    print(f"Sequential: {time.perf_counter()-t:.2f}с")   # ~3с

async def concurrent():
    t = time.perf_counter()
    results = await asyncio.gather(
        slow_task("A", 1.0),
        slow_task("B", 1.0),
        slow_task("C", 1.0),
    )
    print(f"Concurrent: {time.perf_counter()-t:.2f}с")   # ~1с
    return results

# asyncio.gather з обробкою помилок
async def safe_gather():
    results = await asyncio.gather(
        slow_task("OK", 0.5),
        asyncio.sleep(100),   # занадто довго
        slow_task("OK2", 0.3),
        return_exceptions=True,   # помилки = результати, не виключення
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"  Помилка: {r}")
        else:
            print(f"  OK: {r}")

asyncio.run(sequential())
asyncio.run(concurrent())
```

---

### 4. `asyncio.create_task()` та `TaskGroup`

```python
import asyncio

# create_task — запускає корутину "у фоні" не чекаючи
async def background_job():
    await asyncio.sleep(2)
    print("Фонова задача завершена")

async def main_with_task():
    task = asyncio.create_task(background_job())
    print("Продовжуємо роботу...")
    await asyncio.sleep(0.5)
    print("Ще щось робимо...")
    await task   # чекаємо завершення фонової задачі

# TaskGroup (Python 3.11+) — безпечніший варіант
async def main_task_group():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(slow_task("A", 1.0))
        t2 = tg.create_task(slow_task("B", 0.5))
    # Тут обидві задачі завершені
    print(t1.result(), t2.result())

# Timeout
async def with_timeout():
    try:
        result = await asyncio.wait_for(
            slow_task("довго", 5.0),
            timeout=2.0
        )
    except asyncio.TimeoutError:
        print("Час вийшов!")
```

---

### 5. Синхронізація: `Lock`, `Semaphore`, `Queue`

```python
import asyncio

# asyncio.Lock — взаємне виключення
lock = asyncio.Lock()
shared_data = []

async def safe_append(item: int):
    async with lock:
        await asyncio.sleep(0.01)   # симуляція роботи
        shared_data.append(item)

# asyncio.Semaphore — обмеження кількості паралельних операцій
sem = asyncio.Semaphore(3)   # максимум 3 одночасно

async def rate_limited_request(url: str) -> str:
    async with sem:
        await asyncio.sleep(0.1)   # HTTP запит
        return f"Response from {url}"

# asyncio.Queue — producer/consumer паттерн
async def producer(queue: asyncio.Queue, items: list):
    for item in items:
        await queue.put(item)
        await asyncio.sleep(0.1)
    await queue.put(None)   # sentinel для зупинки

async def consumer(queue: asyncio.Queue, name: str):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"[{name}] обробляю: {item}")
        await asyncio.sleep(0.2)
        queue.task_done()

async def pipeline():
    q = asyncio.Queue(maxsize=5)
    await asyncio.gather(
        producer(q, list(range(10))),
        consumer(q, "Worker-1"),
        consumer(q, "Worker-2"),
    )
```

---

### 6. Async context manager та iterator

```python
import asyncio

class AsyncDatabase:
    """Імітація async з'єднання з БД."""

    async def __aenter__(self):
        await asyncio.sleep(0.01)   # підключення
        print("DB: підключено")
        return self

    async def __aexit__(self, *args):
        await asyncio.sleep(0.01)   # відключення
        print("DB: відключено")

    async def fetch(self, query: str) -> list:
        await asyncio.sleep(0.05)
        return [{"id": i} for i in range(3)]

async def use_db():
    async with AsyncDatabase() as db:
        rows = await db.fetch("SELECT * FROM users")
        return rows

# Async generator
async def async_range(n: int):
    for i in range(n):
        await asyncio.sleep(0.01)
        yield i

async def consume_async_gen():
    async for i in async_range(5):
        print(i, end=" ")
    print()
```

---

### 7. Типові пастки

```python
import asyncio, time

# ❌ Пастка 1: Blocking call в async функції — блокує весь event loop!
async def bad_sleep():
    time.sleep(1)   # БЛОКУЄ! Жодна інша корутина не виконується!

async def good_sleep():
    await asyncio.sleep(1)   # ✅ Event loop продовжує роботу

# ❌ Пастка 2: Requests в async (блокуюча бібліотека)
import requests   # НЕ async!

async def bad_request(url):
    return requests.get(url)   # блокує event loop!

# ✅ Використовуй httpx або aiohttp
import httpx

async def good_request(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ❌ Пастка 3: CPU-bound у async (не вирішується asyncio)
async def cpu_bound():
    # Це НЕ стане паралельним через asyncio!
    result = sum(x**2 for x in range(10_000_000))
    return result

# ✅ Для CPU-bound: run_in_executor
async def cpu_bound_proper():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,   # executor (None = ThreadPoolExecutor)
        lambda: sum(x**2 for x in range(10_000_000))
    )
    return result

# ❌ Пастка 4: "Забув await"
async def forgot_await():
    result = slow_task("X", 1.0)   # coroutine object, не виконана!
    return result   # повертає coroutine, не результат

# ❌ Пастка 5: Скасування задачі без обробки
async def cancel_example():
    task = asyncio.create_task(slow_task("X", 10.0))
    await asyncio.sleep(1)
    task.cancel()
    # без await task тут — CancelledError може "просочитись"
    try:
        await task
    except asyncio.CancelledError:
        print("Задачу скасовано коректно")
```

---

### 8. Threading vs Multiprocessing vs Asyncio

| | `asyncio` | `threading` | `multiprocessing` |
|---|---|---|---|
| Тип задач | I/O-bound | I/O-bound (з блокуванням) | CPU-bound |
| GIL | Не релевантний | Є (1 потік одночасно) | Немає |
| Паралелізм | Конкурентний | Псевдо-паралельний | Справжній |
| Складність | Середня | Висока | Висока |
| Пам'ять | Мало | Більше | Набагато більше |

```python
# CPU-bound: multiprocessing
from multiprocessing import Pool

def calculate(n):
    return sum(x**2 for x in range(n))

with Pool(4) as pool:   # 4 процеси
    results = pool.map(calculate, [1_000_000] * 8)

# I/O-bound з blocking libs: concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(requests.get, url): url for url in urls}
    for future in as_completed(futures):
        url = futures[future]
        response = future.result()
```

---

## Що маєш вміти після уроку
- [ ] Пояснити що таке event loop і навіщо async
- [ ] Написати кілька корутин і виконати їх паралельно через `gather()`
- [ ] Використати `asyncio.Semaphore` для rate limiting
- [ ] Пояснити чому `time.sleep()` в async функції — погано
- [ ] Вибрати між asyncio / threading / multiprocessing для задачі

---

## Що далі
`task.md`. Потім — **Урок 3: FastAPI**.
