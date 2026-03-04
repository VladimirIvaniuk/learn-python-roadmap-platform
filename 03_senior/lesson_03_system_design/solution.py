"""
Розв'язки — System Design (Senior)
"""
from __future__ import annotations
import asyncio
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable)

# ── Завдання 1 — LRU Cache ───────────────────────────────────────────────────
class LRUCache:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be > 0")
        self._cap = capacity
        self._cache: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Any:
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)
        return self._cache[key]

    def put(self, key: str, value: Any) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self._cap:
            evicted = self._cache.popitem(last=False)
            print(f"  [LRU] evicted: {evicted[0]}")

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        return key in self._cache

cache = LRUCache(3)
for k, v in [("a", 1), ("b", 2), ("c", 3)]:
    cache.put(k, v)
print(f"a={cache.get('a')}")  # a accessed → moved to end
cache.put("d", 4)             # should evict 'b'
print(f"b={cache.get('b')}, d={cache.get('d')}")

# ── Завдання 2 — Token Bucket ─────────────────────────────────────────────────
class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float) -> None:
        self._capacity = capacity
        self._tokens = float(capacity)
        self._refill_rate = refill_rate  # tokens per second
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_rate)
        self._last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

def rate_limit(bucket: TokenBucket):
    def decorator(func: F) -> F:
        from functools import wraps
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not bucket.consume():
                raise RuntimeError("Rate limit exceeded")
            return func(*args, **kwargs)
        return wrapper  # type: ignore
    return decorator

bucket = TokenBucket(capacity=5, refill_rate=2.0)

@rate_limit(bucket)
def api_call(n: int) -> str:
    return f"ok-{n}"

allowed = blocked = 0
for i in range(10):
    try:
        api_call(i)
        allowed += 1
    except RuntimeError:
        blocked += 1

print(f"\nToken Bucket: allowed={allowed}, blocked={blocked}")

# ── Завдання 2 — Sliding Window Rate Limiter ──────────────────────────────────
class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._requests: list[float] = []
        self._lock = threading.Lock()

    def allow(self) -> bool:
        with self._lock:
            now = time.monotonic()
            self._requests = [t for t in self._requests if now - t < self._window]
            if len(self._requests) < self._max:
                self._requests.append(now)
                return True
            return False

sw = SlidingWindowLimiter(3, 1.0)
results = [sw.allow() for _ in range(5)]
print(f"Sliding Window (3 req/s): {results}")

# ── Завдання 3 — @cached decorator ───────────────────────────────────────────
class SimpleCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str, ttl: float) -> Any:
        if key in self._store:
            value, ts = self._store[key]
            if time.monotonic() - ts < ttl:
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (value, time.monotonic())

    def invalidate(self, prefix: str) -> int:
        keys = [k for k in self._store if k.startswith(prefix)]
        for k in keys:
            del self._store[k]
        return len(keys)

_global_cache = SimpleCache()

def cached(ttl: float = 60.0, key_prefix: str = ""):
    def decorator(func: F) -> F:
        from functools import wraps
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{key_prefix}{func.__name__}:{args}:{sorted(kwargs.items())}"
            cached_val = _global_cache.get(key, ttl)
            if cached_val is not None:
                print(f"  [cache hit] {func.__name__}{args}")
                return cached_val
            result = func(*args, **kwargs)
            _global_cache.set(key, result)
            print(f"  [cache miss] {func.__name__}{args}")
            return result
        return wrapper  # type: ignore
    return decorator

@cached(ttl=5.0)
def get_user(user_id: int) -> dict:
    time.sleep(0.01)  # simulated DB call
    return {"id": user_id, "name": f"User-{user_id}"}

print(f"\nCached:")
print(get_user(1))
print(get_user(1))  # hit
print(get_user(2))

# ── Завдання 4 — ConnectionPool ──────────────────────────────────────────────
class ConnectionPool:
    def __init__(self, size: int) -> None:
        self._size = size
        self._sem: asyncio.Semaphore | None = None
        self._connections: list[dict] = []

    async def __aenter__(self) -> "ConnectionPool":
        self._sem = asyncio.Semaphore(self._size)
        self._connections = [{"id": i, "busy": False} for i in range(self._size)]
        return self

    async def __aexit__(self, *_) -> None:
        print(f"  [pool] closed {len(self._connections)} connections")

    async def acquire(self) -> dict:
        assert self._sem is not None
        await self._sem.acquire()
        conn = next(c for c in self._connections if not c["busy"])
        conn["busy"] = True
        return conn

    def release(self, conn: dict) -> None:
        conn["busy"] = False
        assert self._sem is not None
        self._sem.release()

async def use_pool():
    async with ConnectionPool(3) as pool:
        tasks = []
        for i in range(6):
            async def task(n=i):
                conn = await pool.acquire()
                await asyncio.sleep(0.05)
                pool.release(conn)
                return f"task-{n} done"
            tasks.append(asyncio.create_task(task()))
        results = await asyncio.gather(*tasks)
        print(f"\n[pool] {results}")

asyncio.run(use_pool())

# ── Завдання 5 (Challenge) — AtomicCounter ───────────────────────────────────
class AtomicCounter:
    def __init__(self, initial: int = 0) -> None:
        self._value = initial
        self._lock = threading.Lock()

    def increment(self, by: int = 1) -> int:
        with self._lock:
            self._value += by
            return self._value

    def decrement(self, by: int = 1) -> int:
        with self._lock:
            self._value -= by
            return self._value

    @property
    def value(self) -> int:
        with self._lock:
            return self._value

counter = AtomicCounter()
threads = [threading.Thread(target=lambda: [counter.increment() for _ in range(1000)])
           for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()
print(f"\nAtomicCounter final value: {counter.value}")  # expected: 10000
