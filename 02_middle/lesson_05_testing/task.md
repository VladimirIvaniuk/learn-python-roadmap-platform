# Завдання — Тестування

## Завдання 1 — Unit тести
Напиши pytest тести для функцій:
- `calculate_bmi(weight_kg, height_m) → float` (ValueError якщо <= 0)
- `classify_bmi(bmi: float) → str` ("underweight"/"normal"/"overweight"/"obese")
- `safe_divide(a, b) → float | None`

Вимоги: мінімум 3 тести на функцію, один тест — `parametrize`.

## Завдання 2 — Мокування
Є функція:
```python
def get_weather(city: str, api_key: str) -> dict:
    response = requests.get(f"https://api.weather.com/v1/{city}?key={api_key}")
    return response.json()
```
Напиши тест що мокає `requests.get` і перевіряє:
- Правильний URL передається
- Результат повертається як є
- При `ConnectionError` функція повертає `None`

## Завдання 3 — FastAPI тести
Напиши тести для ендпоінтів (з TestClient та SQLite in-memory):
- `POST /register` — успіх, дублікат email, валідаційна помилка
- `POST /login` — успіх, невірний пароль, користувач не знайдений
- `GET /me` — без токена, з токеном

## Завдання 4 — Фікстури та scope
Напиши `conftest.py` з фікстурами:
- `scope="session"`: SQLite engine, сіяч тестових даних
- `scope="function"`: сесія з автоматичним rollback
- `scope="function"`: авторизований `TestClient` (з токеном у headers)

## Завдання 5 (Challenge) — TDD
Implement через TDD (спочатку тест, потім код):
`PasswordValidator` з правилами: мінімум 8 символів, велика літера, цифра, спецсимвол.
Спочатку напиши 10 тестів (червоних), потім реалізацію щоб всі позеленіли.
