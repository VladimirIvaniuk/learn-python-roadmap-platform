# Learn Python — Веб-платформа

Повноцінна веб-платформа для навчання Python з теорією, практикою та автоматичною перевіркою.

## Запуск

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/learn_python
python3 web/run.py
```

Відкрий у браузері: **http://localhost:8000**

## Можливості

- **Теорія** — Markdown з поясненнями
- **Завдання** — опис практичних вправ
- **Приклад** — готовий код
- **Редактор** — CodeMirror з підсвіткою Python
- **Запустити** — виконання коду на сервері
- **Перевірити** — автоматична перевірка за тестами
- **Прогрес** — збереження у localStorage

## Структура

```
web/
├── backend/
│   ├── main.py      # FastAPI, API уроків
│   └── executor.py  # Виконання та перевірка коду
├── frontend/
│   ├── index.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── run.py
└── README.md
```

## Безпека

Код виконується в ізольованому підпроцесі з timeout 5 сек. Заборонено: os.system, subprocess, eval, exec.
