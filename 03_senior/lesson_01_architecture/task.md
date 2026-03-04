# Завдання — Архітектура

## Завдання 1 — SOLID рефакторинг
Дано "God Object":
```python
class ECommerceSystem:
    def register_user(self, email, password): ...
    def login(self, email, password): ...
    def send_email(self, to, subject): ...
    def create_order(self, user_id, items): ...
    def calculate_tax(self, amount, country): ...
    def process_payment(self, order_id, card): ...
    def generate_invoice(self, order_id): ...
    def save_to_db(self, table, data): ...
```
Рефакторуй за SRP — мінімум 5 окремих класів.

## Завдання 2 — Repository Pattern
Реалізуй абстрактний `UserRepository[T]` (Generic) з методами CRUD.
Реалізуй `InMemoryUserRepository` та `FileUserRepository` (зберігає у JSON).
Напиши `UserService` що залежить тільки від абстрактного `UserRepository`.

## Завдання 3 — Strategy Pattern для знижок
Реалізуй `DiscountStrategy` (ABC) і стратегії:
`NoDiscount`, `PercentageDiscount(percent)`, `FixedDiscount(amount)`, `BulkDiscount(qty_threshold, percent)`.
Додай реєстр стратегій та `DiscountCalculator`.

## Завдання 4 — DI Container
Напиши простий `Container` клас що:
- Реєструє залежності через `register(name, factory)`
- Вирішує їх через `resolve(name)`
- Підтримує singleton (один об'єкт) і transient (новий щоразу)

## Завдання 5 (Challenge) — Clean Architecture
Побудуй мінімальний шар-за-шаром:
- Domain: `User` entity + `UserCreatedEvent`
- Application: `RegisterUserUseCase(repo, hasher, event_bus)`
- Infrastructure: `InMemoryUserRepo`, `BcryptHasher`, `InMemoryEventBus`
- Interface: FastAPI endpoint що використовує use case
