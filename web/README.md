# Learn Python - Веб-платформа

Повноцінна платформа для навчання Python: уроки, редактор коду, автоперевірка, прогрес, adaptive-рекомендації, review queue та план навчання.

## 1) Вимоги

- Python 3.12+
- Node.js 20+ і npm
- Git

## 2) Швидкий локальний запуск (development)

### 2.1 Backend

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/learn_python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 web/run.py
```

Backend стартує на `http://localhost:8000`.

### 2.2 Frontend (Vite dev server)

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/learn_python/web/frontend
npm ci
npm run dev
```

Frontend dev-сервер: `http://localhost:5173`  
API-проксі налаштований на `http://localhost:8000` (див. `web/frontend/vite.config.ts`).

## 3) Production-збірка і запуск

### 3.1 Збірка frontend

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/learn_python/web/frontend
npm ci
npm run build
```

Після цього створюється `web/frontend/dist`, який FastAPI віддає як SPA.

### 3.2 Запуск backend без reload

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/learn_python
source .venv/bin/activate
uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --workers 2
```

## 4) База даних (важливо)

### 4.1 Яка БД використовується зараз

Проєкт за замовчуванням використовує **SQLite**:

- файл БД: `web/learn_python.db`
- підключення: `sqlite:///.../web/learn_python.db` (див. `web/backend/database.py`)

### 4.2 Ініціалізація схеми

Окрему команду для міграцій запускати не потрібно:

- при старті backend викликається `init_db()`
- таблиці створюються автоматично (`Base.metadata.create_all`)
- легкі ALTER-міграції виконуються в `_migrate_db()`

### 4.3 Основні таблиці

- `users`
- `progress`
- `code_snapshots`
- `lesson_notes`
- `lesson_attempts`
- `review_queue`
- `user_gamification`
- `weekly_plan_task_states`

### 4.4 Перевірка БД локально

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/learn_python
sqlite3 web/learn_python.db ".tables"
sqlite3 web/learn_python.db "SELECT id,email,username,created_at FROM users LIMIT 10;"
```

### 4.5 Backup/restore БД

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/learn_python
sqlite3 web/learn_python.db ".backup 'web/backups/learn_python-$(date +%F).db'"
```

Restore:

```bash
cp web/backups/learn_python-YYYY-MM-DD.db web/learn_python.db
```

### 4.6 Скидання БД (тільки для dev)

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/learn_python
rm -f web/learn_python.db
python3 web/run.py
```

Після restart backend БД створиться заново.

## 5) Змінні середовища

Файл: `.env` у корені репозиторію.

Обов'язково:

- `SECRET_KEY` - секрет для підпису JWT токенів.

Створення безпечного ключа:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Потім встав у `.env`:

```env
SECRET_KEY=<your-generated-secret>
```

## 6) Деплой на Linux (systemd + nginx)

Нижче базовий production-патерн.

### 6.1 systemd service

Створи `/etc/systemd/system/learn-python.service`:

```ini
[Unit]
Description=Learn Python FastAPI
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/learn_python
EnvironmentFile=/opt/learn_python/.env
ExecStart=/opt/learn_python/.venv/bin/uvicorn web.backend.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Команди:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now learn-python
sudo systemctl status learn-python
```

### 6.2 nginx reverse proxy

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Після цього ввімкни HTTPS (Let's Encrypt certbot).

## 7) Перевірка після розгортання

Backend API:

```bash
curl -s http://127.0.0.1:8000/api/levels | python3 -m json.tool
```

Frontend build smoke test:

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/learn_python/web/frontend
npm run test:e2e
```

## 8) Безпека та експлуатація

- Не використовуй дефолтний `SECRET_KEY` у production.
- Доступ на запис до `web/learn_python.db` має бути тільки у користувача сервісу.
- Регулярно роби backup SQLite-файлу.
- Не запускай прод із `--reload`.
- CI/CodeQL/Dependabot вже увімкнені в GitHub.
