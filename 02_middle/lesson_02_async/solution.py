"""
Розв'язки — Async Programming (Middle)
"""
import asyncio
import time
import random

# ── Завдання 1 — sync vs async ────────────────────────────────────────────────
async def async_task(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} done"

async def run_concurrent():
    t0 = time.perf_counter()
    results = await asyncio.gather(
        async_task("A", 1.0),
        async_task("B", 1.5),
        async_task("C", 0.5),
    )
    elapsed = time.perf_counter() - t0
    print(f"Concurrent: {elapsed:.2f}s — {results}")

asyncio.run(run_concurrent())

# ── Завдання 2 — Rate limiter з Semaphore ─────────────────────────────────────
async def fetch_url(session_id: int, sem: asyncio.Semaphore) -> str:
    async with sem:
        delay = random.uniform(0.1, 0.3)
        await asyncio.sleep(delay)
        return f"response-{session_id}"

async def run_rate_limited():
    sem = asyncio.Semaphore(3)
    t0 = time.perf_counter()
    tasks = [fetch_url(i, sem) for i in range(10)]
    results = await asyncio.gather(*tasks)
    print(f"\nRate limited 10 tasks in {time.perf_counter()-t0:.2f}s")
    print(f"  {results[:3]}...")

asyncio.run(run_rate_limited())

# ── Завдання 3 — Producer / Consumer ─────────────────────────────────────────
async def producer(queue: asyncio.Queue, items: list):
    for item in items:
        await asyncio.sleep(0.05)
        await queue.put(item)
        print(f"  produced: {item}")
    await queue.put(None)  # sentinel

async def consumer(queue: asyncio.Queue, results: list):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        await asyncio.sleep(0.02)
        results.append(item * 2)
        print(f"  consumed: {item} → {item * 2}")
        queue.task_done()

async def run_pipeline():
    q: asyncio.Queue = asyncio.Queue(maxsize=5)
    results: list = []
    items = [1, 2, 3, 4, 5]
    await asyncio.gather(
        producer(q, items),
        consumer(q, results),
    )
    print(f"\nPipeline results: {results}")

asyncio.run(run_pipeline())

# ── Завдання 4 — fetch_with_retry + timeout ───────────────────────────────────
async def fake_api(url: str) -> dict:
    """Симулює нестабільне API."""
    await asyncio.sleep(random.uniform(0.1, 0.5))
    if random.random() < 0.4:
        raise ConnectionError(f"Connection failed: {url}")
    return {"url": url, "status": 200}

async def fetch_with_retry(url: str, retries: int = 3, timeout: float = 0.4) -> dict:
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return await asyncio.wait_for(fake_api(url), timeout=timeout)
        except (ConnectionError, asyncio.TimeoutError) as e:
            last_exc = e
            wait = 0.1 * 2 ** (attempt - 1)
            print(f"  [attempt {attempt}] {type(e).__name__}: retry in {wait:.2f}s")
            await asyncio.sleep(wait)
    raise RuntimeError(f"Failed after {retries} retries: {last_exc}")

async def run_fetch():
    for url in ["https://api.example.com/data", "https://api.example.com/users"]:
        try:
            result = await fetch_with_retry(url)
            print(f"  ✓ {result}")
        except RuntimeError as e:
            print(f"  ✗ {e}")

asyncio.run(run_fetch())

# ── Завдання 5 (Challenge) — Async Pipeline ───────────────────────────────────
async def pipeline_stage(
    name: str,
    in_q: asyncio.Queue,
    out_q: asyncio.Queue,
    transform,
):
    while True:
        item = await in_q.get()
        if item is None:
            in_q.task_done()
            await out_q.put(None)
            break
        result = await transform(item)
        await out_q.put(result)
        in_q.task_done()

async def parse_stage(item):
    await asyncio.sleep(0.01)
    return int(item)

async def compute_stage(item):
    await asyncio.sleep(0.01)
    return item ** 2

async def run_multi_stage():
    raw: asyncio.Queue = asyncio.Queue()
    parsed: asyncio.Queue = asyncio.Queue()
    computed: asyncio.Queue = asyncio.Queue()

    for i in ["1", "2", "3", "4", "5", None]:
        await raw.put(i)

    results = []
    async def collect():
        while True:
            item = await computed.get()
            if item is None:
                break
            results.append(item)

    await asyncio.gather(
        pipeline_stage("parse",   raw,    parsed,   parse_stage),
        pipeline_stage("compute", parsed, computed, compute_stage),
        collect(),
    )
    print(f"\nAsync pipeline: {results}")

asyncio.run(run_multi_stage())
