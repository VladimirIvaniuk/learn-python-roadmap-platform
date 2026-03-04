# Урок 6 — Soft Skills: Ментор, Code Review, Технічне інтерв'ю

## Що вивчимо
- Як бути хорошим ментором і менторуватись
- Культура code review
- Технічна документація: README, API docs, ADR
- Технічне інтерв'ю: як готуватись і що очікувати
- Комунікація з командою та стейкхолдерами
- Особистий ріст: learning plan, зона некомфорту

---

## Теорія

### 1. Ментор і менті

**Ролі ментора:**
```
Mentor ≠ Boss
Mentor = Guide + Supporter + Challenger

Що роблять хороші ментори:
✅ Задають питання, не дають одразу відповідь
✅ "Спробуй спочатку самостійно, потім розберемось"
✅ Пояснюють ЧОМУ, а не тільки ЩО
✅ Показують свій процес думання
✅ Дають конкретний actionable фідбек
✅ Celebrate wins — помічають прогрес
✅ Помиляються публічно — нормалізують помилки

❌ Відповідають на всі питання відразу
❌ "Роби так бо я сказав"
❌ Критикують особу, а не код
❌ Мікроменеджмент
```

**Задавати правильні питання:**
```python
# ❌ "Чому ти написав це так?"  → захисна реакція

# ✅ Сократівські питання:
"Що цей код робить коли [edge case]?"
"Як ти думаєш, що станеться якщо список порожній?"
"Чи є інший підхід? Які плюси і мінуси кожного?"
"Як ми можемо написати тест для цього?"
"Що б ти змінив якщо б міг?"
```

**Feedback формула:**
```
SBI (Situation — Behavior — Impact):
"На вчорашньому code review [Situation]
ти пояснив рішення з документацією [Behavior]
— це допомогло мені зрозуміти контекст набагато швидше [Impact]"

"На PR #42 [Situation]
функція login() містить 80 рядків і 3 різні відповідальності [Behavior]
— це важко тестувати і майбутні зміни зачеплять багато коду [Impact]
Пропоную розбити на [конкретна пропозиція]"
```

---

### 2. Культура Code Review

**Для автора PR:**
```markdown
## Опис PR (шаблон)
### Що змінено
- Додано JWT refresh token логіку
- Виправлено race condition у session management

### Чому
Іcсue #123: Користувачі виходять кожні 15 хвилин

### Як тестував
- [x] Unit tests для TokenService
- [x] Integration test: login → use API → refresh → use API again
- [x] Manual test в dev середовищі

### Скріншоти (для UI змін)

### Checklist
- [x] Тести написані та проходять
- [x] mypy перевірено
- [x] Немає secrets у коді
- [x] Документацію оновлено
```

**Для рев'ювера:**
```python
# Рівні коментарів (використовуй префікси)
"""
nit: незначна дрібниця — необов'язково виправляти
    "nit: можна скоротити до list comprehension, але це ok"

suggestion: пропозиція — бажано
    "suggestion: врахуй що sorted() створює новий список,
    .sort() швидше якщо оригінал не потрібен"

blocking: обов'язково виправити
    "blocking: SQL Injection! Використай параметризований запит"

question: уточнення (не проблема)
    "question: чому 15 хвилин для TTL? Є ліміти від зовнішнього API?"

praise: добре зроблено
    "praise: відмінне рішення з Cache-Aside! Набагато чистіше ніж минулий PR"
"""

# Золоті правила:
# 1. Критикуй код, а не людину
# 2. Пояснюй ЧОМУ
# 3. Пропонуй альтернативу
# 4. Approve якщо OK — не тримай PR безкінечно
# 5. Відповідай протягом 24 годин
```

---

### 3. Технічна документація

**README (структура):**
```markdown
# Назва проєкту

Короткий опис (1-2 речення) що це таке.

## Швидкий старт

```bash
git clone ...
cd project
make dev       # встановити залежності
make run       # запустити
```

## Вимоги
- Python 3.12+
- Docker (для БД)

## Встановлення
...

## Конфігурація
| Змінна | Опис | За замовчуванням |
|--------|------|-----------------|
| SECRET_KEY | JWT ключ | (обов'язково) |

## API
Документація: http://localhost:8000/docs

## Тести
```bash
make test
```

## Deployment
...
```

**ADR (Architecture Decision Record):**
```markdown
# ADR-001: Вибір FastAPI замість Django REST Framework

**Дата:** 2026-03-01
**Статус:** Прийнято

## Контекст
Потрібен Python HTTP API framework для Learn Python платформи.

## Рішення
Обрано FastAPI 0.111.

## Причини
- Async native (SQLAlchemy 2.0 async-first)
- Автоматична OpenAPI документація
- Pydantic для валідації (стандарт у 2026)
- 300% швидше за Flask у benchmarks

## Альтернативи
- Django REST Framework: занадто важкий для SPA API
- Flask: немає async, немає type hints by default

## Наслідки
+ Сучасний стек, легко наймати
+ Відмінна документація
- Молодша екосистема ніж Django
- Потребує async розуміння від команди
```

---

### 4. Технічне інтерв'ю

**Структура типового Python інтерв'ю:**
```
1. Скринінг (30хв)
   - Розкажи про себе + проєкт
   - 2-3 технічних питання Python basics

2. Технічний раунд 1 (60хв)
   - Coding task: LeetCode-style або практичне
   - Data structures, algorithms

3. Технічний раунд 2 (60хв)
   - System Design (для Senior)
   - Code Review — знайди проблеми

4. Behavioral (30хв)
   - STAR method для конфліктів, досягнень
   - "Розкажи про свій найскладніший баг"
```

**Приклади Python питань:**
```python
# Q: Що виведе цей код?
def append(item, lst=[]):
    lst.append(item)
    return lst

print(append(1))   # [1]
print(append(2))   # [1, 2]  ← не [2]!

# A: Мутабельний default argument — shared між викликами

# Q: GIL — що це?
# A: Global Interpreter Lock — м'ютекс що дозволяє тільки 1 потоку
# виконувати Python bytecode одночасно.
# Обходи: multiprocessing (окремі процеси), asyncio (для I/O)

# Q: Що таке генератор і навіщо?
# A: Функція з yield — повертає ітератор що обчислює значення ліниво.
# Перевага: O(1) пам'ять для великих послідовностей

# Q: __new__ vs __init__
class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance   # __init__ викликається ПІСЛЯ __new__

# Q: Чому list comprehension швидше за map()?
# A: LC — bytecode оптимізований, уникає Python function call overhead

# Q: Що таке descriptor?
class ValidatedAttribute:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"{self.name} must be non-negative int")
        obj.__dict__[self.name] = value
```

**STAR Method для behavioral:**
```
S — Situation: Опиши контекст
T — Task: Яка була твоя задача/відповідальність
A — Action: Що конкретно ти зробив
R — Result: Який результат (з числами якщо можливо)

Приклад:
S: "В нас було API що відповідало 5+ секунд під навантаженням"
T: "Я відповідав за оптимізацію продуктивності"
A: "Профілював через cProfile, знайшов N+1 у списку постів.
    Додав selectinload, потім Redis кеш для топ-100 запитів"
R: "Час відповіді знизився з 5с до 200мс (25x). 
    Навантаження БД знизилось на 80%"
```

---

### 5. Особистий ріст

**Learning Plan на рік:**
```
Q1 (Поточний рівень → Middle):
  - Завершити всі уроки Junior + Middle
  - Побудувати 1 Pet Project з FastAPI + DB
  - Зробити 50 LeetCode задач (Easy/Medium)

Q2 (Middle → Senior):
  - Вивчити system design (книга: "Designing Data-Intensive Applications")
  - Зробити 1 Open Source contribution
  - Написати 3 технічних статті

Q3 (Senior skills):
  - Вивчити Kubernetes basics
  - Менторувати 1 junior розробника
  - Підготуватись до Senior interview

Q4 (Interview + Job):
  - 5 mock interviews
  - Подати 20+ заявок
  - Negotiate salary!
```

**10 000 годин — реалістично:**
```
5 годин/день × 365 днів = 1825 годин/рік
Щоб стати Senior: 3-5 років наполегливої практики

Але якість > кількість:
- Deliberate practice — виходь за межі зони комфорту
- Build → Break → Fix → Understand
- Teach others — найкращий спосіб закріпити знання
```

---

## Що маєш вміти після уроку
- [ ] Провести code review використовуючи SBI feedback
- [ ] Написати якісний PR description за шаблоном
- [ ] Відповісти на 10 типових Python interview питань
- [ ] Скласти особистий learning plan на 6 місяців
- [ ] Написати ADR для технічного рішення в своєму проєкті

---

## Вітаємо — ти завершив Senior рівень!
Тепер: практикуй, будуй, ментор, розповідай іншим.  
Найкращий спосіб навчитись — це навчати.  
**Good luck! 🚀**
