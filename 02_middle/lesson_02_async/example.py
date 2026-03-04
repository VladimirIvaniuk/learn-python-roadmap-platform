"""
Урок Middle 2 — Приклади: asyncio та async/await
"""
import asyncio
import time
import random


# ── Базовий async/await ───────────────────────────────────────────────────────
async def fetch_data(name: str, delay: float) -> dict:
    """Симулює HTTP запит з затримкою."""
    await asyncio.sleep(delay)
    return {"source": name, "data": random.randint(1, 100)}


async def sequential_vs_concurrent():
    print("=== Sequential vs Concurrent ===")

    # Sequential: час = сума всіх затримок
    t0 = time.perf_counter()
    r1 = await fetch_data("API-1", 0.5)
    r2 = await fetch_data("API-2", 0.5)
    r3 = await fetch_data("API-3", 0.5)
    print(f"Sequential: {time.perf_counter()-t0:.2f}с (очікуємо ~1.5с)")

    # Concurrent: час = максимальна затримка
    t0 = time.perf_counter()
    r1, r2, r3 = await asyncio.gather(
        fetch_data("API-1", 0.5),
        fetch_data("API-2", 0.5),
        fetch_data("API-3", 0.5),
    )
    print(f"Concurrent: {time.perf_counter()-t0:.2f}с (очікуємо ~0.5с)")


# ── create_task та TaskGroup ──────────────────────────────────────────────────
async def task_demo():
    print("\n=== Tasks ===")

    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fetch_data("fast", 0.1))
        t2 = tg.create_task(fetch_data("slow", 0.5))

    print(f"Task 1: {t1.result()}")
    print(f"Task 2: {t2.result()}")


# ── Semaphore — rate limiting ─────────────────────────────────────────────────
sem = asyncio.Semaphore(3)   # max 3 паралельних

async def rate_limited_fetch(url: str) -> str:
    async with sem:
        await asyncio.sleep(0.2)   # симуляція HTTP
        return f"OK: {url}"

async def rate_limit_demo():
    print("\n=== Rate Limiting (max 3 concurrent) ===")
    urls = [f"https://api.example.com/item/{i}" for i in range(10)]
    t0 = time.perf_counter()
    results = await asyncio.gather(*[rate_limited_fetch(u) for u in urls])
    print(f"10 запитів, max 3 паралельних: {time.perf_counter()-t0:.2f}с")
    print(f"Результати: {len(results)} (перші 3: {results[:3]})")


# ── Producer / Consumer ───────────────────────────────────────────────────────
async def producer(queue: asyncio.Queue, items: list) -> None:
    for item in items:
        await queue.put(item)
        await asyncio.sleep(0.05)
    await queue.put(None)   # sentinel

async def worker(queue: asyncio.Queue, worker_id: int) -> None:
    while True:
        item = await queue.get()
        if item is None:
            await queue.put(None)   # передаємо іншим worker-ам
            break
        result = item ** 2
        print(f"  Worker-{worker_id}: {item}² = {result}")
        await asyncio.sleep(0.1)
        queue.task_done()

async def producer_consumer_demo():
    print("\n=== Producer/Consumer ===")
    q: asyncio.Queue[int | None] = asyncio.Queue(maxsize=5)
    await asyncio.gather(
        producer(q, list(range(1, 7))),
        worker(q, 1),
        worker(q, 2),
    )


# ── Timeout ───────────────────────────────────────────────────────────────────
async def timeout_demo():
    print("\n=== Timeout ===")
    try:
        result = await asyncio.wait_for(fetch_data("slow", 5.0), timeout=0.5)
        print(f"Отримали: {result}")
    except asyncio.TimeoutError:
        print("  TimeoutError! Запит тривав більше 0.5с")


# ── Async context manager ─────────────────────────────────────────────────────
class AsyncPool:
    def __init__(self, size: int) -> None:
        self.size = size

    async def __aenter__(self) -> "AsyncPool":
        await asyncio.sleep(0.01)   # підключення
        print(f"\nПул з {self.size} з'єднань відкритий")
        return self

    async def __aexit__(self, *args) -> None:
        await asyncio.sleep(0.01)   # відключення
        print("Пул закрито")

    async def execute(self, query: str) -> list:
        await asyncio.sleep(0.05)
        return [{"result": query}]


async def async_cm_demo():
    async with AsyncPool(5) as pool:
        results = await pool.execute("SELECT * FROM users")
        print(f"  Запит виконано: {results}")


# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    await sequential_vs_concurrent()
    await task_demo()
    await rate_limit_demo()
    await producer_consumer_demo()
    await timeout_demo()
    await async_cm_demo()


asyncio.run(main())
