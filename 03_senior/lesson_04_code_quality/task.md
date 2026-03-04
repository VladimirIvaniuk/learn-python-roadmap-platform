# Завдання — Якість коду

## Завдання 1 — mypy строгий режим
Візьми будь-який файл з Junior/Middle рівня і:
1. Запусти `mypy --strict`
2. Виправ всі помилки типів
3. Додай `reveal_type()` для кількох виразів і поясни результати

## Завдання 2 — ruff налаштування
Налаштуй `pyproject.toml` для проєкту:
- Правила: E, F, I, N, UP, B, SIM
- line-length: 100
- Запусти `ruff check --fix .` і `ruff format .`
- Поясни що означає кожна виправлена помилка

## Завдання 3 — pre-commit pipeline
Налаштуй `.pre-commit-config.yaml` з:
- pre-commit-hooks (trailing whitespace, end-of-file, check-yaml)
- ruff check + format
- Перевір що невалідний код блокує коміт

## Завдання 4 — Рефакторинг CC>10
Знайди функцію з цикломатичною складністю > 7 (або напиши навмисно складну).
Рефакторуй через Early Return, Extract Method, Strategy паттерн.
Виміряй CC до і після через `radon cc -a .`

## Завдання 5 (Challenge) — Code Review Simulation
Відкрий будь-який Junior рівень example.py і проведи code review:
- Знайди мінімум 5 місць для покращення
- Для кожного: рівень (nit/suggestion/blocking), пояснення, пропозиція
- Виправ "blocking" проблеми
