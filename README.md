# Python: від нуля до Senior Developer

Повний курс навчання Python з чіткою структурою модулів, практичними проєктами та критеріями оцінки прогресу.

## Структура проєкту

```
learn_python/
├── 01_junior/           # Модулі 1.1–1.7 (3–6 місяців)
│   ├── 01_basics/       # Вступ, типи, керування потоком, функції
│   ├── 02_data_structures/
│   ├── 03_oop/
│   ├── 04_files_errors/
│   └── projects/       # Калькулятор, TODO-list, CSV парсер
├── 02_middle/           # Модулі 2.1–2.6 (6–12 місяців)
│   ├── 01_oop_advanced/
│   ├── 02_async/
│   ├── fastapi_demo/
│   ├── databases/
│   ├── 03_testing/
│   ├── 04_devops/
│   └── projects/
├── 03_senior/           # Модулі 3.1–3.6 (12+ місяців)
│   ├── 01_architecture/
│   ├── 02_design_patterns/
│   ├── 03_system_design/
│   ├── 04_code_quality/
│   ├── 05_security/
│   ├── 06_soft_skills/
│   └── projects/
├── requirements.txt
└── README.md
```

## Як почати

1. **Встановіть Python 3.12+** — [python.org](https://www.python.org/downloads/)
2. **Створіть віртуальне середовище:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # або: venv\Scripts\activate  # Windows
   ```
3. **Встановіть залежності:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Почніть з модуля 1.1** — `01_junior/01_basics/`
   - Прочитайте [HOW_TO_PRACTICE.md](01_junior/01_basics/HOW_TO_PRACTICE.md)
   - Уроки: `lesson_01_hello/`, `lesson_02_types/` тощо

5. **Middle** — [02_middle/README.md](02_middle/README.md) — 6 уроків
6. **Senior** — [03_senior/README.md](03_senior/README.md) — 6 уроків

## Принципи навчання

- **Практика > теорія** — 70% коду, 30% читання
- **Проєкти** — кожен модуль завершувати приватним проєктом
- **Консистентність** — щоденні короткі сесії краще за рідкісні довгі

## Ресурси

- [Документація Python](https://docs.python.org/3/)
- [Real Python](https://realpython.com/)
- [Exercism](https://exercism.org/tracks/python)
