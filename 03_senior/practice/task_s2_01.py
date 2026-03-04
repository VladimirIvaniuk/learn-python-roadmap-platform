"""
Практика — Урок 2 (Design Patterns)
Дивись lesson_02_design_patterns/task.md

Завдання 1: Factory для Exporter (json/csv)
Завдання 2: Strategy для валідації (email, length)
"""
import json
from abc import ABC, abstractmethod


# --- Factory (Завдання 1) ---

class Exporter(ABC):
    @abstractmethod
    def export(self, data: dict) -> str: ...


class JsonExporter(Exporter):
    def export(self, data: dict) -> str:
        # TODO: json.dumps(data)
        return ""


class CsvExporter(Exporter):
    def export(self, data: dict) -> str:
        # TODO: CSV-рядок (перший рядок — ключі, другий — значення)
        return ""


def create_exporter(format: str) -> Exporter:
    # TODO: if format == "json" -> JsonExporter, "csv" -> CsvExporter, інакше raise ValueError
    return JsonExporter()  # замини на повну реалізацію


# --- Strategy (Завдання 2) ---

class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, value: str) -> bool: ...


class EmailValidator(ValidationStrategy):
    def validate(self, value: str) -> bool:
        # TODO: перевір наявність @ та . після @
        return False


class LengthValidator(ValidationStrategy):
    def __init__(self, min_length: int) -> None:
        self.min_length = min_length

    def validate(self, value: str) -> bool:
        # TODO: len(value) >= min_length
        return False


class Validator:
    def __init__(self, strategy: ValidationStrategy) -> None:
        self._strategy = strategy

    def validate(self, value: str) -> bool:
        return self._strategy.validate(value)


# Перевірка
if __name__ == "__main__":
    exporter = create_exporter("json")
    print(exporter.export({"name": "Test", "score": 42}))
    v = Validator(EmailValidator())
    print(v.validate("test@mail.com"))  # True
    print(v.validate("invalid"))        # False
