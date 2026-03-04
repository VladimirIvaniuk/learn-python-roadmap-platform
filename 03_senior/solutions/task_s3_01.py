"""
Рішення — Урок 3 (Кеш з TTL)

Дивись після того, як спробував сам!
"""
import time
from threading import Lock


class TTLCache:
    def __init__(self) -> None:
        self._data: dict[str, tuple[object, float]] = {}
        self._lock = Lock()

    def get(self, key: str) -> object | None:
        with self._lock:
            if key not in self._data:
                return None
            value, expires_at = self._data[key]
            if time.time() > expires_at:
                del self._data[key]
                return None
            return value

    def set(self, key: str, value: object, ttl_seconds: float) -> None:
        with self._lock:
            self._data[key] = (value, time.time() + ttl_seconds)


cache = TTLCache()
cache.set("x", 42, ttl_seconds=1)
print(cache.get("x"))
time.sleep(2)
print(cache.get("x"))
