"""
Рішення — Урок 1 (Файли)

Дивись після того, як спробував сам!
"""
import os

PRACTICE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_PATH = os.path.join(PRACTICE_DIR, "notes.txt")


# Завдання 1
def create_notes():
    with open(NOTES_PATH, "w", encoding="utf-8") as f:
        f.write("Замітка 1\n")
        f.write("Замітка 2\n")
        f.write("Замітка 3\n")


# Завдання 2
def read_notes():
    with open(NOTES_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines, 1):
        print(f"{i}. {line.strip()}")


# Завдання 3
def append_line(filename: str, text: str) -> None:
    with open(filename, "a", encoding="utf-8") as f:
        f.write(text + "\n")


# Перевірка
create_notes()
read_notes()
append_line(NOTES_PATH, "Замітка 4")
print("\nПісля append:")
read_notes()
