# Урок 2 — Паттерни проєктування

## Що вивчимо
- Creational: Factory, Abstract Factory, Singleton, Builder
- Structural: Adapter, Decorator, Facade, Proxy
- Behavioral: Strategy, Observer, Command, Chain of Responsibility, Template Method
- Коли застосовувати (і коли НЕ варто)
- Антипаттерни: God Object, Magic Numbers, Primitive Obsession

---

## Теорія

### 1. Creational Patterns

#### Factory Method
```python
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message: str, recipient: str) -> None: ...

class EmailNotification(Notification):
    def send(self, message: str, recipient: str) -> None:
        print(f"Email → {recipient}: {message}")

class SMSNotification(Notification):
    def send(self, message: str, recipient: str) -> None:
        print(f"SMS → {recipient}: {message}")

class PushNotification(Notification):
    def send(self, message: str, recipient: str) -> None:
        print(f"Push → {recipient}: {message}")

# Factory
class NotificationFactory:
    _registry: dict[str, type[Notification]] = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification,
    }

    @classmethod
    def create(cls, channel: str) -> Notification:
        if channel not in cls._registry:
            raise ValueError(f"Unknown channel: {channel}")
        return cls._registry[channel]()

    @classmethod
    def register(cls, name: str, cls_: type[Notification]) -> None:
        cls._registry[name] = cls_

# Використання
notif = NotificationFactory.create("email")
notif.send("Ваше замовлення готове!", "alice@example.com")
```

#### Builder
```python
class QueryBuilder:
    """SQL Query Builder."""

    def __init__(self, table: str) -> None:
        self._table = table
        self._select: list[str] = ["*"]
        self._where: list[str] = []
        self._order_by: list[str] = []
        self._limit: int | None = None
        self._offset: int | None = None

    def select(self, *columns: str) -> "QueryBuilder":
        self._select = list(columns)
        return self   # method chaining!

    def where(self, condition: str) -> "QueryBuilder":
        self._where.append(condition)
        return self

    def order_by(self, column: str, desc: bool = False) -> "QueryBuilder":
        self._order_by.append(f"{column} {'DESC' if desc else 'ASC'}")
        return self

    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n
        return self

    def offset(self, n: int) -> "QueryBuilder":
        self._offset = n
        return self

    def build(self) -> str:
        sql = f"SELECT {', '.join(self._select)} FROM {self._table}"
        if self._where:
            sql += f" WHERE {' AND '.join(self._where)}"
        if self._order_by:
            sql += f" ORDER BY {', '.join(self._order_by)}"
        if self._limit:
            sql += f" LIMIT {self._limit}"
        if self._offset:
            sql += f" OFFSET {self._offset}"
        return sql

# Fluent interface
query = (
    QueryBuilder("users")
    .select("id", "username", "email")
    .where("is_active = TRUE")
    .where("age >= 18")
    .order_by("username")
    .limit(20)
    .offset(40)
    .build()
)
print(query)
# SELECT id, username, email FROM users WHERE is_active = TRUE AND age >= 18 ORDER BY username ASC LIMIT 20 OFFSET 40
```

#### Singleton
```python
class DatabasePool:
    _instance: "DatabasePool | None" = None

    def __new__(cls) -> "DatabasePool":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connections = []
        return cls._instance

# Thread-safe singleton
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:   # double-checked locking
                    cls._instance = super().__new__(cls)
        return cls._instance

# ✅ Краще — module-level singleton (Python idiom)
# config.py
class _Config:
    def __init__(self): self.debug = False

config = _Config()   # одиночний екземпляр на рівні модуля
```

---

### 2. Structural Patterns

#### Decorator (паттерн, не Python decorator)
```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    @abstractmethod
    def process(self, data: str) -> str: ...

class TextProcessor(DataProcessor):
    def process(self, data: str) -> str:
        return data

class ProcessorDecorator(DataProcessor):
    def __init__(self, wrapped: DataProcessor) -> None:
        self._wrapped = wrapped

    def process(self, data: str) -> str:
        return self._wrapped.process(data)

class CompressionDecorator(ProcessorDecorator):
    def process(self, data: str) -> str:
        result = self._wrapped.process(data)
        return f"[COMPRESSED:{len(result)}]{result}"

class EncryptionDecorator(ProcessorDecorator):
    def process(self, data: str) -> str:
        result = self._wrapped.process(data)
        return f"[ENCRYPTED]{result[::-1]}"

class LoggingDecorator(ProcessorDecorator):
    def process(self, data: str) -> str:
        print(f"Processing: {len(data)} chars")
        result = self._wrapped.process(data)
        print(f"Processed: {len(result)} chars")
        return result

# Гнучке комбінування
processor = LoggingDecorator(
    EncryptionDecorator(
        CompressionDecorator(
            TextProcessor()
        )
    )
)
result = processor.process("Hello, World!")
```

#### Adapter
```python
# Старий клас (не можемо змінити)
class LegacyXMLParser:
    def parse_xml(self, xml: str) -> dict:
        return {"parsed_from_xml": xml}

# Новий інтерфейс
class DataParser(Protocol):
    def parse(self, data: str) -> dict: ...

# Адаптер — прокидаємо міст між інтерфейсами
class XMLParserAdapter:
    def __init__(self, xml_parser: LegacyXMLParser) -> None:
        self._parser = xml_parser

    def parse(self, data: str) -> dict:
        return self._parser.parse_xml(data)

# Тепер LegacyXMLParser можна використати там де потрібен DataParser
adapter: DataParser = XMLParserAdapter(LegacyXMLParser())
result = adapter.parse("<user>Alice</user>")
```

---

### 3. Behavioral Patterns

#### Strategy
```python
from typing import Protocol

class SortStrategy(Protocol):
    def sort(self, data: list) -> list: ...

class BubbleSort:
    def sort(self, data: list) -> list:
        d = data.copy()
        for i in range(len(d)):
            for j in range(len(d)-i-1):
                if d[j] > d[j+1]:
                    d[j], d[j+1] = d[j+1], d[j]
        return d

class QuickSort:
    def sort(self, data: list) -> list:
        if len(data) <= 1:
            return data
        pivot = data[len(data)//2]
        left = [x for x in data if x < pivot]
        mid = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + mid + self.sort(right)

class Sorter:
    def __init__(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def sort(self, data: list) -> list:
        return self._strategy.sort(data)

sorter = Sorter(QuickSort())
print(sorter.sort([3, 1, 4, 1, 5, 9, 2, 6]))

sorter.set_strategy(BubbleSort())
print(sorter.sort([3, 1, 4, 1, 5, 9, 2, 6]))
```

#### Observer
```python
from abc import ABC, abstractmethod
from typing import Any

class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data: Any) -> None: ...

class Subject:
    def __init__(self) -> None:
        self._observers: dict[str, list[Observer]] = {}

    def subscribe(self, event: str, observer: Observer) -> None:
        self._observers.setdefault(event, []).append(observer)

    def unsubscribe(self, event: str, observer: Observer) -> None:
        if event in self._observers:
            self._observers[event].remove(observer)

    def notify(self, event: str, data: Any = None) -> None:
        for obs in self._observers.get(event, []):
            obs.update(event, data)

class UserService(Subject):
    def register(self, email: str) -> dict:
        user = {"id": 1, "email": email}
        self.notify("user.registered", user)
        return user

    def deactivate(self, user_id: int) -> None:
        self.notify("user.deactivated", {"id": user_id})

class WelcomeEmailObserver(Observer):
    def update(self, event: str, data: Any) -> None:
        if event == "user.registered":
            print(f"📧 Відправляємо welcome email → {data['email']}")

class AuditLogObserver(Observer):
    def update(self, event: str, data: Any) -> None:
        print(f"📝 Audit log: {event} | data={data}")

service = UserService()
service.subscribe("user.registered", WelcomeEmailObserver())
service.subscribe("user.registered", AuditLogObserver())
service.subscribe("user.deactivated", AuditLogObserver())

service.register("alice@example.com")
service.deactivate(1)
```

#### Command
```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...

class Document:
    def __init__(self, text: str = "") -> None:
        self.text = text

class InsertCommand(Command):
    def __init__(self, doc: Document, pos: int, text: str) -> None:
        self.doc = doc
        self.pos = pos
        self.text = text

    def execute(self) -> None:
        self.doc.text = self.doc.text[:self.pos] + self.text + self.doc.text[self.pos:]

    def undo(self) -> None:
        self.doc.text = self.doc.text[:self.pos] + self.doc.text[self.pos + len(self.text):]

class Editor:
    def __init__(self, doc: Document) -> None:
        self.doc = doc
        self._history: list[Command] = []

    def execute(self, command: Command) -> None:
        command.execute()
        self._history.append(command)

    def undo(self) -> None:
        if self._history:
            self._history.pop().undo()

doc = Document("Hello World")
editor = Editor(doc)
editor.execute(InsertCommand(doc, 5, ", Python"))
print(doc.text)   # Hello, Python World
editor.undo()
print(doc.text)   # Hello World
```

---

### Антипаттерни

```python
# ❌ God Object — знає про все і робить все
class ApplicationManager:
    def handle_login(self): ...
    def send_email(self): ...
    def render_html(self): ...
    def validate_form(self): ...
    def connect_to_db(self): ...
    def calculate_tax(self): ...
    # 50+ методів...

# ❌ Magic Numbers
if status_code == 404:    # що таке 404?
    pass

# ✅
HTTP_NOT_FOUND = 404
if status_code == HTTP_NOT_FOUND:
    pass

# ❌ Primitive Obsession — рядки замість типів
def transfer(from_account: str, to_account: str, amount: float): ...

# ✅
@dataclass(frozen=True)
class AccountId:
    value: str

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "UAH"

def transfer(from_account: AccountId, to_account: AccountId, amount: Money): ...
```

---

## Що маєш вміти після уроку
- [ ] Реалізувати Factory Method для різних типів сповіщень
- [ ] Написати QueryBuilder через Builder паттерн
- [ ] Реалізувати Observer для подієвої системи
- [ ] Пояснити різницю Strategy і Template Method
- [ ] Розпізнати і назвати антипаттерни у коді

---

## Що далі
`task.md`. Потім — **Урок 3: System Design**.
