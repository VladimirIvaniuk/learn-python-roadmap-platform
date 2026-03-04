"""
Рішення — Урок 2 (Design Patterns)

Дивись після того, як спробував сам!
"""
import json
import csv
from io import StringIO
from abc import ABC, abstractmethod


class Exporter(ABC):
    @abstractmethod
    def export(self, data: dict) -> str: ...


class CsvExporter(Exporter):
    def export(self, data: dict) -> str:
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)
        return output.getvalue()


class JsonExporter(Exporter):
    def export(self, data: dict) -> str:
        return json.dumps(data, ensure_ascii=False)


def create_exporter(format: str) -> Exporter:
    if format == "csv":
        return CsvExporter()
    if format == "json":
        return JsonExporter()
    raise ValueError(f"Unknown format: {format}")


class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, value: str) -> bool: ...


class EmailValidator(ValidationStrategy):
    def validate(self, value: str) -> bool:
        return "@" in value and "." in value.split("@")[-1]


class LengthValidator(ValidationStrategy):
    def __init__(self, min_length: int) -> None:
        self.min_length = min_length

    def validate(self, value: str) -> bool:
        return len(value) >= self.min_length


class Validator:
    def __init__(self, strategy: ValidationStrategy) -> None:
        self._strategy = strategy

    def validate(self, value: str) -> bool:
        return self._strategy.validate(value)


print(create_exporter("json").export({"a": 1, "b": 2}))
v = Validator(EmailValidator())
print(v.validate("test@mail.com"))
