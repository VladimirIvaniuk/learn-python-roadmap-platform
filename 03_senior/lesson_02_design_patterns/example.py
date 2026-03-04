"""
Senior 2 — Приклади: Design Patterns
"""
from abc import ABC, abstractmethod
from typing import Any, Callable


# ── Factory Method ─────────────────────────────────────────────────────────────
class Notification(ABC):
    @abstractmethod
    def send(self, to: str, message: str) -> None: ...

class EmailNotification(Notification):
    def send(self, to: str, message: str) -> None:
        print(f"  📧 Email → {to}: {message[:30]}...")

class SMSNotification(Notification):
    def send(self, to: str, message: str) -> None:
        print(f"  📱 SMS → {to}: {message[:30]}...")

class PushNotification(Notification):
    def send(self, to: str, message: str) -> None:
        print(f"  🔔 Push → {to}: {message[:30]}...")

class NotificationFactory:
    _registry: dict[str, type[Notification]] = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification,
    }

    @classmethod
    def register(cls, name: str, cls_: type[Notification]) -> None:
        cls._registry[name] = cls_

    @classmethod
    def create(cls, channel: str) -> Notification:
        if channel not in cls._registry:
            raise ValueError(f"Unknown: {channel}. Available: {list(cls._registry)}")
        return cls._registry[channel]()

print("=== Factory ===")
for channel in ["email", "sms", "push"]:
    n = NotificationFactory.create(channel)
    n.send("alice@example.com", "Ваше замовлення готове до видачі!")


# ── Builder ───────────────────────────────────────────────────────────────────
class QueryBuilder:
    def __init__(self, table: str) -> None:
        self._table = table
        self._select: list[str] = ["*"]
        self._where: list[str] = []
        self._joins: list[str] = []
        self._order_by: list[str] = []
        self._limit: int | None = None
        self._offset: int | None = None

    def select(self, *cols: str) -> "QueryBuilder":
        self._select = list(cols); return self

    def join(self, table: str, on: str) -> "QueryBuilder":
        self._joins.append(f"JOIN {table} ON {on}"); return self

    def where(self, cond: str) -> "QueryBuilder":
        self._where.append(cond); return self

    def order_by(self, col: str, desc: bool = False) -> "QueryBuilder":
        self._order_by.append(f"{col} {'DESC' if desc else 'ASC'}"); return self

    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n; return self

    def offset(self, n: int) -> "QueryBuilder":
        self._offset = n; return self

    def build(self) -> str:
        sql = f"SELECT {', '.join(self._select)} FROM {self._table}"
        if self._joins: sql += " " + " ".join(self._joins)
        if self._where: sql += " WHERE " + " AND ".join(self._where)
        if self._order_by: sql += " ORDER BY " + ", ".join(self._order_by)
        if self._limit: sql += f" LIMIT {self._limit}"
        if self._offset: sql += f" OFFSET {self._offset}"
        return sql

print("\n=== Builder ===")
q = (QueryBuilder("users")
     .select("u.id", "u.username", "p.count")
     .join("posts p", "p.author_id = u.id")
     .where("u.is_active = TRUE")
     .order_by("p.count", desc=True)
     .limit(10)
     .build())
print(f"  {q}")


# ── Observer / Event Bus ──────────────────────────────────────────────────────
class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = {}

    def subscribe(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        if event in self._handlers:
            self._handlers[event].remove(handler)

    def emit(self, event: str, **data: Any) -> None:
        for handler in self._handlers.get(event, []):
            handler(**data)

bus = EventBus()
bus.subscribe("user.registered", lambda email, **_: print(f"  📧 Welcome email → {email}"))
bus.subscribe("user.registered", lambda email, user_id, **_: print(f"  📝 Audit: new user {user_id}"))
bus.subscribe("order.placed", lambda order_id, **_: print(f"  🚀 Processing order {order_id}"))

print("\n=== Observer / Event Bus ===")
bus.emit("user.registered", email="alice@example.com", user_id=42)
bus.emit("order.placed", order_id=100, amount=299.99)


# ── Strategy ─────────────────────────────────────────────────────────────────
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool: ...

class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number: str) -> None:
        self.last4 = card_number[-4:]
    def pay(self, amount: float) -> bool:
        print(f"  💳 Card *{self.last4}: {amount:.2f} грн")
        return True

class CryptoPayment(PaymentStrategy):
    def __init__(self, wallet: str) -> None:
        self.wallet = wallet[:8] + "..."
    def pay(self, amount: float) -> bool:
        print(f"  ₿ Crypto {self.wallet}: {amount:.2f} USDT")
        return True

class CheckoutService:
    def __init__(self, strategy: PaymentStrategy) -> None:
        self._strategy = strategy

    def set_payment_method(self, s: PaymentStrategy) -> None:
        self._strategy = s

    def checkout(self, amount: float) -> bool:
        return self._strategy.pay(amount)

print("\n=== Strategy ===")
checkout = CheckoutService(CreditCardPayment("1234567890121234"))
checkout.checkout(99.99)
checkout.set_payment_method(CryptoPayment("0x1234abcd5678ef90"))
checkout.checkout(99.99)


# ── Command ───────────────────────────────────────────────────────────────────
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...

class TextBuffer:
    def __init__(self) -> None:
        self.text = ""

class AppendCommand(Command):
    def __init__(self, buf: TextBuffer, text: str) -> None:
        self.buf = buf
        self.text = text
    def execute(self) -> None:
        self.buf.text += self.text
    def undo(self) -> None:
        self.buf.text = self.buf.text[:-len(self.text)]

class Editor:
    def __init__(self) -> None:
        self.buf = TextBuffer()
        self._history: list[Command] = []

    def run(self, cmd: Command) -> None:
        cmd.execute()
        self._history.append(cmd)
        print(f"  Text: '{self.buf.text}'")

    def undo(self) -> None:
        if self._history:
            self._history.pop().undo()
            print(f"  Undo → '{self.buf.text}'")

print("\n=== Command + Undo ===")
ed = Editor()
ed.run(AppendCommand(ed.buf, "Hello"))
ed.run(AppendCommand(ed.buf, ", World"))
ed.run(AppendCommand(ed.buf, "!"))
ed.undo()
ed.undo()
