"""
Практика — Урок 3 (Системний дизайн)
Дивись lesson_03_system_design/task.md

Завдання: TTLCache — кеш з TTL (time-to-live)
get(key) -> значення або None (None, якщо TTL минув)
set(key, value, ttl_seconds)
"""
import time


class TTLCache:
    def __init__(self) -> None:
        # _data: {key: (value, expires_at)}
        self._data: dict = {}

    def get(self, key: str) -> object | None:
        # TODO: якщо ключ не існує — None
        # TODO: якщо time.time() > expires_at — видали і поверни None
        # TODO: інакше поверни value
        return None

    def set(self, key: str, value: object, ttl_seconds: float) -> None:
        # TODO: зберегти (value, time.time() + ttl_seconds)
        pass


# Перевірка
if __name__ == "__main__":
    cache = TTLCache()
    cache.set("user:1", {"name": "Alice"}, ttl_seconds=1)
    print(cache.get("user:1"))   # {'name': 'Alice'}
    time.sleep(1.1)
    print(cache.get("user:1"))   # None (TTL минув)
