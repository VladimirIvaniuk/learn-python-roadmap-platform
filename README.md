# Python: від нуля до Senior Developer

Репозиторій поєднує:

- навчальні модулі (`Junior` -> `Middle` -> `Senior`)
- веб-платформу для проходження уроків, запуску коду та трекінгу прогресу

## Швидкий старт веб-платформи (для користувачів репозиторію)

### 1) Вимоги

- Python 3.12+
- Node.js 20+
- npm

### 2) Запуск backend

```bash
git clone https://github.com/VladimirIvaniuk/learn-python-roadmap-platform.git
cd learn-python-roadmap-platform
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 web/run.py
```

Backend буде доступний на `http://localhost:8000`.

### 3) Запуск frontend (в окремому терміналі)

```bash
cd web/frontend
npm ci
npm run dev
```

Frontend буде доступний на `http://localhost:5173`.

### 4) Що з базою даних

- за замовчуванням використовується **SQLite**
- файл БД: `web/learn_python.db`
- схема створюється автоматично при старті backend (`init_db()`)

Перевірити таблиці:

```bash
sqlite3 web/learn_python.db ".tables"
```

## Повне розгортання (prod + backup + systemd/nginx)

Детальна інструкція для production:

- [web/README.md](web/README.md)

## Для контриб'юторів та операційки

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [docs/ops/runbook.md](docs/ops/runbook.md)
- [CHANGELOG.md](CHANGELOG.md)

## Troubleshooting

### 1) `Address already in use` (порт зайнятий)

- Backend за замовчуванням: `8000`
- Frontend dev: `5173`

Перевірка процесів:

```bash
lsof -i :8000
lsof -i :5173
```

### 2) Попередження про `SECRET_KEY`

Якщо бачиш warning про дефолтний ключ, створи `.env`:

```bash
cp .env.example .env
python3 -c "import secrets; print(secrets.token_hex(32))"
```

І встав значення у `.env`:

```env
SECRET_KEY=<your-generated-secret>
```

### 3) Frontend не стартує (`npm`/залежності)

У каталозі `web/frontend` виконай:

```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### 4) E2E тести падають через браузер Playwright

Встанови браузер Chromium:

```bash
cd web/frontend
npx playwright install --with-deps chromium
npm run test:e2e
```

### 5) Помилки доступу до SQLite (`web/learn_python.db`)

Переконайся, що поточний користувач має права на запис у `web/`:

```bash
ls -la web
```

Для dev-скидання БД:

```bash
rm -f web/learn_python.db
python3 web/run.py
```

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
├── web/                 # Backend + Frontend платформи
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

