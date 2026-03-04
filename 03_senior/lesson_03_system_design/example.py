"""
Senior 3 — Приклади: кешування, rate limiting, profiling
"""
import time
import threading
import asyncio
from collections import OrderedDict, deque
from functools import wraps


# ── LRU Cache (O(1)) ──────────────────────────────────────────────────────────
class LRUCache:
    """O(1) get/put через OrderedDict."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._cache: OrderedDict[str, any] = OrderedDict()

    def get(self, key: str) -> any:
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)   # оновлюємо "нещодавно використаний"
        return self._cache[key]

    def put(self, key: str, value: any) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.capacity:
                self._cache.popitem(last=False)   # видаляємо LRU (перший)
        self._cache[key] = value

    def __repr__(self) -> str:
        return f"LRUCache({dict(self._cache)})"


cache = LRUCache(3)
for key, val in [("a", 1), ("b", 2), ("c", 3)]:
    cache.put(key, val)

print("=== LRU Cache ===")
print(f"  get(a)={cache.get('a')}")   # 'a' стає найновішим
cache.put("d", 4)                      # 'b' виганяється (LRU)
print(f"  Після put(d): {cache}")
print(f"  get(b)={cache.get('b')}")   # None — виганяли


# ── Token Bucket Rate Limiter ─────────────────────────────────────────────────
class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float) -> None:
        self.capacity = capacity
        self.tokens = capacity
        self.rate = refill_rate  # токенів/секунду
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def consume(self, tokens: float = 1.0) -> bool:
        with self._lock:
            now = time.monotonic()
            self.tokens = min(self.capacity, self.tokens + (now - self._last) * self.rate)
            self._last = now
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

bucket = TokenBucket(capacity=5, refill_rate=2)  # 5 токенів, 2/с відновлення

print("\n=== Token Bucket (5 capacity, 2/s refill) ===")
for i in range(8):
    allowed = bucket.consume()
    print(f"  Запит {i+1}: {'✅ дозволено' if allowed else '❌ відхилено'}")
    time.sleep(0.1)


# ── Sliding Window Rate Limiter ───────────────────────────────────────────────
class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_req = max_requests
        self.window = window_seconds
        self._clients: dict[str, deque] = {}

    def is_allowed(self, client_id: str) -> bool:
        now = time.monotonic()
        q = self._clients.setdefault(client_id, deque())
        while q and q[0] < now - self.window:
            q.popleft()
        if len(q) < self.max_req:
            q.append(now)
            return True
        return False

limiter = SlidingWindowLimiter(max_requests=3, window_seconds=1.0)

print("\n=== Sliding Window (3 req/1s) ===")
for i in range(5):
    ok = limiter.is_allowed("192.168.1.1")
    print(f"  Запит {i+1}: {'✅' if ok else '❌'}")


# ── Cache Decorator ───────────────────────────────────────────────────────────
class SimpleCache:
    def __init__(self) -> None:
        self._data: dict[str, tuple[any, float]] = {}

    def get(self, key: str) -> any:
        if key in self._data:
            val, exp = self._data[key]
            if exp == 0 or time.monotonic() < exp:
                return val
            del self._data[key]
        return None

    def set(self, key: str, val: any, ttl: int = 0) -> None:
        exp = (time.monotonic() + ttl) if ttl else 0
        self._data[key] = (val, exp)

_global_cache = SimpleCache()

def cached(ttl: int = 60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            result = _global_cache.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            _global_cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator

_call_count = 0

@cached(ttl=5)
def expensive_query(user_id: int) -> dict:
    global _call_count
    _call_count += 1
    time.sleep(0.01)   # симуляція DB
    return {"id": user_id, "name": f"User {user_id}"}

print("\n=== Cache Decorator ===")
for i in range(3):
    expensive_query(42)
    expensive_query(42)
    expensive_query(99)
print(f"  DB викликано {_call_count} разів (з 6 запитів)")


# ── Thread-Safe Counter ───────────────────────────────────────────────────────
class AtomicCounter:
    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def increment(self) -> int:
        with self._lock:
            self._value += 1
            return self._value

    @property
    def value(self) -> int:
        return self._value

counter = AtomicCounter()

def worker(n: int) -> None:
    for _ in range(n):
        counter.increment()

print("\n=== Thread-Safe Counter ===")
threads = [threading.Thread(target=worker, args=(1000,)) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()
print(f"  10 потоків × 1000 = {counter.value} (очікуємо 10000)")
