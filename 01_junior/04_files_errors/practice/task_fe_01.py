"""
Практика — Урок 1 (Файли)
Див. lesson_01_files/task.md

Заповни TODO. Потім порівняй з solutions/task_fe_01.py
"""
import os

PRACTICE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_PATH = os.path.join(PRACTICE_DIR, "notes.txt")

# Завдання 1 — створи notes.txt з "Замітка 1", "Замітка 2", "Замітка 3"
# TODO: with open(NOTES_PATH, "w", encoding="utf-8") as f: ...

# Завдання 2 — прочитай і виведи з нумерацією (1. Замітка 1, ...)
# TODO: with open(NOTES_PATH, "r", encoding="utf-8") as f: ...


def append_line(filename: str, text: str) -> None:
    """Додає рядок text у кінець файлу."""
    # TODO: open з режимом "a"
    pass


# Перевірка — заповни TODO, потім запусти
if __name__ == "__main__":
    pass  # викликай функції для перевірки
