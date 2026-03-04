"""
Рішення — Урок 1 (Архітектура)

Дивись після того, як спробував сам!
"""
from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    def log(self, message: str) -> None: ...


class ConsoleLogger(Logger):
    def log(self, message: str) -> None:
        print(f"[CONSOLE] {message}")


class FileLogger(Logger):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def log(self, message: str) -> None:
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")


class App:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    def run(self) -> None:
        self._logger.log("App started")


app1 = App(ConsoleLogger())
app1.run()

app2 = App(FileLogger("app.log"))
app2.run()
