# Урок 3 — System Design: Кешування, черги, масштабування

## Що вивчимо
- Кешування: Redis, TTL-стратегії, cache invalidation
- Черги повідомлень: RQ, Celery, asyncio.Queue
- Rate limiting алгоритми: Token Bucket, Fixed Window
- Горизонтальне масштабування: stateless API, load balancing
- CAP теорема та BASE vs ACID
- Profiling: виявлення вузьких місць

---

## Теорія

### 1. Кешування

```python
import time, hashlib, json
from typing import Any, Callable
from functools import wraps

# In-memory cache (простий)
class InMemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        if key not in self._store:
            return None
        value, expires_at = self._store[key]
        if expires_at and time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        expires_at = time.time() + ttl if ttl else None
        self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

# Cache decorator — Cache-Aside pattern
cache = InMemoryCache()

def cached(ttl: int = 60, key_prefix: str = ""):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix or func.__name__}:{hash(str(args) + str(kwargs))}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix or func.__name__}:{hash(str(args) + str(kwargs))}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        import asyncio
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Використання
@cached(ttl=300)
def get_user(user_id: int) -> dict:
    print(f"  DB query for user {user_id}...")   # виводиться тільки раз
    return {"id": user_id, "name": "Alice"}

print(get_user(1))   # DB query...
print(get_user(1))   # З кешу
print(get_user(1))   # З кешу

# Cache invalidation — найважча проблема в CS
def update_user(user_id: int, data: dict) -> dict:
    # Оновити в БД
    updated = {"id": user_id, **data}
    # Інвалідувати кеш
    cache.delete(f"get_user:{hash(str((user_id,)) + str({}))}")
    return updated
```

**Redis (реальний проєкт):**
```python
import redis.asyncio as redis

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379"):
        self._client = redis.from_url(url, decode_responses=True)

    async def get(self, key: str) -> Any | None:
        value = await self._client.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        await self._client.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        keys = await self._client.keys(pattern)
        if keys:
            await self._client.delete(*keys)
```

---

### 2. Rate Limiting

```python
import time
from collections import deque

# Token Bucket алгоритм
class TokenBucket:
    """
    Маємо відро з токенами.
    Наповнюється зі швидкістю rate/секунду.
    Максимум capacity токенів.
    Кожен запит витрачає 1 токен.
    """

    def __init__(self, capacity: int, rate: float) -> None:
        self.capacity = capacity
        self.rate = rate          # токенів/секунду
        self.tokens = capacity    # починаємо повними
        self.last_refill = time.time()

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True   # запит дозволено
        return False      # занадто багато запитів

# Sliding Window Counter
class SlidingWindowRateLimiter:
    """Лічильник у ковзному вікні часу."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._requests: dict[str, deque] = {}

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        if client_id not in self._requests:
            self._requests[client_id] = deque()

        window = self._requests[client_id]

        # Видалити запити поза вікном
        while window and window[0] < now - self.window:
            window.popleft()

        if len(window) < self.max_requests:
            window.append(now)
            return True
        return False

# FastAPI Rate Limit Middleware
from fastapi import Request, Response

class RateLimitMiddleware:
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        self.app = app
        self.limiter = SlidingWindowRateLimiter(max_requests, window)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            client_ip = request.client.host

            if not self.limiter.is_allowed(client_ip):
                response = Response(
                    content='{"error": "Rate limit exceeded"}',
                    status_code=429,
                    media_type="application/json",
                )
                response.headers["Retry-After"] = "60"
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
```

---

### 3. Черги завдань (Task Queue)

```python
import asyncio
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class Task:
    func: Callable
    args: tuple
    kwargs: dict
    priority: int = 0

class AsyncTaskQueue:
    """Проста async черга з worker-пулом."""

    def __init__(self, workers: int = 4) -> None:
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._workers_count = workers
        self._workers: list[asyncio.Task] = []

    async def enqueue(self, func: Callable, *args, priority: int = 0, **kwargs) -> None:
        task = Task(func, args, kwargs, priority)
        await self._queue.put((priority, task))

    async def _worker(self, name: str) -> None:
        while True:
            _, task = await self._queue.get()
            try:
                if asyncio.iscoroutinefunction(task.func):
                    await task.func(*task.args, **task.kwargs)
                else:
                    task.func(*task.args, **task.kwargs)
            except Exception as e:
                print(f"[{name}] Task failed: {e}")
            finally:
                self._queue.task_done()

    async def start(self) -> None:
        self._workers = [
            asyncio.create_task(self._worker(f"Worker-{i}"))
            for i in range(self._workers_count)
        ]

    async def stop(self) -> None:
        await self._queue.join()
        for w in self._workers:
            w.cancel()

# Використання
async def send_email(to: str, subject: str) -> None:
    await asyncio.sleep(0.1)   # симуляція
    print(f"  Email sent to {to}: {subject}")

async def demo_queue():
    q = AsyncTaskQueue(workers=2)
    await q.start()

    await q.enqueue(send_email, "alice@example.com", "Welcome!")
    await q.enqueue(send_email, "bob@example.com", "Your order")
    await q.enqueue(send_email, "carol@example.com", "Invoice")

    await q.stop()

asyncio.run(demo_queue())
```

---

### 4. CAP теорема та вибір БД

```
CAP: Consistency, Availability, Partition tolerance
     (можна забезпечити максимум 2 з 3)

CP (Consistency + Partition tolerance):
   MongoDB, HBase, Zookeeper
   → Може бути недоступна, але дані завжди консистентні

AP (Availability + Partition tolerance):
   Cassandra, DynamoDB, CouchDB
   → Завжди доступна, але можуть бути застарілі дані

CA (Consistency + Availability):
   Традиційні RDBMS (PostgreSQL, MySQL)
   → В реальних розподілених системах CA = теорія
```

```python
# ACID (Реляційні БД)
# Atomicity, Consistency, Isolation, Durability

with db.begin():   # транзакція
    user.balance -= 100
    account.balance += 100
# Або обидва зміни, або жоден

# BASE (NoSQL)
# Basically Available, Soft state, Eventually consistent
# Дані врешті-решт стануть консистентними (не одразу)
```

---

### 5. Profiling

```python
import cProfile, pstats, io, time

# cProfile — виявлення гарячих точок
def profile(func):
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
        ps.print_stats(10)  # топ 10 функцій
        print(s.getvalue())
        return result
    return wrapper

@profile
def slow_function():
    return sum(x**2 for x in range(100_000))

# timeit — точне вимірювання
import timeit

# Порівняння підходів
list_comp = timeit.timeit("[x**2 for x in range(1000)]", number=1000)
map_call  = timeit.timeit("list(map(lambda x: x**2, range(1000)))", number=1000)
print(f"List comp: {list_comp:.4f}с, map: {map_call:.4f}с")

# memory_profiler
# pip install memory-profiler
# @profile (line-by-line memory)
# def memory_heavy():
#     big_list = [0] * 1_000_000
#     ...
```

---

## Що маєш вміти після уроку
- [ ] Написати Cache-Aside декоратор
- [ ] Реалізувати Token Bucket або Sliding Window rate limiter
- [ ] Пояснити CAP теорему і назвати де застосовується AP/CP
- [ ] Запрофілювати функцію та знайти вузьке місце
- [ ] Описати різницю ACID і BASE

---

## Що далі
`task.md`. Потім — **Урок 4: Code Quality**.
