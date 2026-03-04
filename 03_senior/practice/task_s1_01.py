"""
Практика — Урок 1 (Архітектура та SOLID)
Дивись lesson_01_architecture/task.md

Завдання 1: Logger (ABC) + ConsoleLogger + FileLogger + App (DI)
Завдання 2: знайди і вини DRY у своєму коді
Завдання 3: опиши SRP для UserManager (текстом у коментарі)
"""
from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    def log(self, message: str) -> None:
        """Логувати повідомлення."""


class ConsoleLogger(Logger):
    def log(self, message: str) -> None:
        # TODO: print з префіксом [CONSOLE]
        pass


class FileLogger(Logger):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def log(self, message: str) -> None:
        # TODO: записати в файл
        pass


class App:
    def __init__(self, logger: Logger) -> None:
        # TODO: зберегти logger
        pass

    def run(self) -> None:
        # TODO: logger.log("App started")
        pass


# Перевірка (заповни TODO вище)
if __name__ == "__main__":
    app1 = App(ConsoleLogger())
    app1.run()
    # app2 = App(FileLogger("app.log"))
    # app2.run()

# Завдання 3 — SRP для UserManager:
# TODO: напиши коментар — як би ти розбив клас, що відправляє email і зберігає в БД?
