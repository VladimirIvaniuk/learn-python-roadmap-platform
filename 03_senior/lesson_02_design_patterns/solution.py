"""
Розв'язки — Design Patterns (Senior)
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Any
import threading

# ── Завдання 1 — NotificationFactory ─────────────────────────────────────────
class Notification(ABC):
    def __init__(self, recipient: str, message: str) -> None:
        self.recipient = recipient
        self.message = message

    @abstractmethod
    def send(self) -> str: ...

class EmailNotification(Notification):
    def send(self) -> str:
        return f"[Email → {self.recipient}] {self.message}"

class SMSNotification(Notification):
    def send(self) -> str:
        return f"[SMS → {self.recipient}] {self.message}"

class PushNotification(Notification):
    def send(self) -> str:
        return f"[Push → {self.recipient}] {self.message}"

class SlackNotification(Notification):
    def send(self) -> str:
        return f"[Slack → #{self.recipient}] {self.message}"

class NotificationFactory:
    _registry: dict[str, type[Notification]] = {
        "email": EmailNotification,
        "sms":   SMSNotification,
        "push":  PushNotification,
        "slack": SlackNotification,
    }

    @classmethod
    def create(cls, channel: str, recipient: str, message: str) -> Notification:
        klass = cls._registry.get(channel)
        if not klass:
            raise ValueError(f"Unknown channel: {channel!r}")
        return klass(recipient, message)

    @classmethod
    def register(cls, channel: str, klass: type[Notification]) -> None:
        cls._registry[channel] = klass

for ch in ["email", "sms", "push", "slack"]:
    n = NotificationFactory.create(ch, "user@example.com", "Тест")
    print(n.send())

# ── Завдання 2 — ResponseBuilder ─────────────────────────────────────────────
class HTTPResponse:
    def __init__(
        self, status: int, body: Any,
        headers: dict[str, str], cookies: dict[str, str],
    ) -> None:
        self.status = status
        self.body = body
        self.headers = headers
        self.cookies = cookies

    def __repr__(self) -> str:
        return f"HTTPResponse(status={self.status}, headers={self.headers})"

class ResponseBuilder:
    def __init__(self) -> None:
        self._status = 200
        self._body: Any = None
        self._headers: dict[str, str] = {}
        self._cookies: dict[str, str] = {}

    def status(self, code: int) -> "ResponseBuilder":
        self._status = code
        return self

    def json(self, data: Any) -> "ResponseBuilder":
        import json
        self._body = json.dumps(data)
        self._headers["Content-Type"] = "application/json"
        return self

    def header(self, key: str, value: str) -> "ResponseBuilder":
        self._headers[key] = value
        return self

    def cookie(self, key: str, value: str) -> "ResponseBuilder":
        self._cookies[key] = value
        return self

    def build(self) -> HTTPResponse:
        return HTTPResponse(self._status, self._body, self._headers, self._cookies)

resp = (
    ResponseBuilder()
    .status(201)
    .json({"id": 1, "name": "Іван"})
    .header("X-Request-Id", "abc-123")
    .cookie("session", "xyz")
    .build()
)
print(f"\n{resp}")

# ── Завдання 3 — EventBus (Observer) ─────────────────────────────────────────
class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[Callable]] = {}

    def subscribe(self, event: str, handler: Callable) -> None:
        self._subs.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        if event in self._subs:
            self._subs[event] = [h for h in self._subs[event] if h != handler]

    def publish(self, event: str, *args, **kwargs) -> None:
        for handler in self._subs.get(event, []):
            handler(*args, **kwargs)

bus = EventBus()

def on_user_created(user: dict):
    print(f"\n[EventBus] user.created: {user['name']}")

def on_user_created_email(user: dict):
    print(f"[EventBus] send welcome email → {user['email']}")

bus.subscribe("user.created", on_user_created)
bus.subscribe("user.created", on_user_created_email)
bus.publish("user.created", {"name": "Катя", "email": "k@test.com"})

# ── Завдання 4 — Chain of Responsibility ─────────────────────────────────────
class Handler(ABC):
    def __init__(self) -> None:
        self._next: Handler | None = None

    def set_next(self, handler: "Handler") -> "Handler":
        self._next = handler
        return handler

    def handle(self, request: dict) -> dict | None:
        if self._next:
            return self._next.handle(request)
        return request

class AuthHandler(Handler):
    def handle(self, request: dict) -> dict | None:
        if not request.get("token"):
            request["error"] = "Unauthorized"
            return request
        request["user"] = {"id": 1}
        return super().handle(request)

class RateLimitHandler(Handler):
    def __init__(self, limit: int = 5) -> None:
        super().__init__()
        self._counts: dict[str, int] = {}
        self._limit = limit

    def handle(self, request: dict) -> dict | None:
        ip = request.get("ip", "unknown")
        self._counts[ip] = self._counts.get(ip, 0) + 1
        if self._counts[ip] > self._limit:
            request["error"] = "Rate limit exceeded"
            return request
        return super().handle(request)

class LoggingHandler(Handler):
    def handle(self, request: dict) -> dict | None:
        print(f"[Log] request: {request.get('path', '/')}")
        return super().handle(request)

auth = AuthHandler()
rate = RateLimitHandler()
log = LoggingHandler()
auth.set_next(rate).set_next(log)

print(f"\nChain 1: {auth.handle({'path': '/api', 'token': 'abc', 'ip': '1.2.3.4'})}")
print(f"Chain 2: {auth.handle({'path': '/api', 'ip': '1.2.3.4'})}")

# ── Завдання 5 (Challenge) — Composite (File System) ─────────────────────────
class FSNode(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def display(self, indent: int = 0) -> None: ...

class File(FSNode):
    def __init__(self, name: str, size_bytes: int) -> None:
        super().__init__(name)
        self._size = size_bytes

    def size(self) -> int:
        return self._size

    def display(self, indent: int = 0) -> None:
        print(f"{'  ' * indent}📄 {self.name} ({self._size}B)")

class Directory(FSNode):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._children: list[FSNode] = []

    def add(self, node: FSNode) -> "Directory":
        self._children.append(node)
        return self

    def size(self) -> int:
        return sum(c.size() for c in self._children)

    def display(self, indent: int = 0) -> None:
        print(f"{'  ' * indent}📁 {self.name}/ ({self.size()}B)")
        for child in self._children:
            child.display(indent + 1)

root = Directory("project")
src = Directory("src")
src.add(File("main.py", 1024)).add(File("utils.py", 512))
root.add(src).add(File("README.md", 256)).add(File("requirements.txt", 128))
print()
root.display()
print(f"Total: {root.size()}B")
