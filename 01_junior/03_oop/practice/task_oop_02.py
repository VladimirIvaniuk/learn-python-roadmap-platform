"""
Практика — Урок 2 (Наслідування)
Див. lesson_02_inheritance/task.md

Завдання 1: Animal + Dog (speak)
Завдання 2: Vehicle + Car (info з super)
Завдання 3: Product (_price, get_price, set_price)
"""


class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return "..."


class Dog(Animal):
    def speak(self) -> str:
        # TODO: поверни "Гав!"
        return "..."


class Vehicle:
    def __init__(self, brand: str, model: str) -> None:
        # TODO
        pass

    def info(self) -> str:
        # TODO: "brand model"
        return ""


class Car(Vehicle):
    def __init__(self, brand: str, model: str, doors: int) -> None:
        # TODO: super().__init__ + self.doors
        pass

    def info(self) -> str:
        # TODO: super().info() + ", N дверей"
        return ""


class Product:
    def __init__(self) -> None:
        self._price = 0

    def get_price(self) -> float:
        return self._price

    def set_price(self, amount: float) -> None:
        # TODO: якщо amount >= 0
        pass


if __name__ == "__main__":
    dog = Dog("Рекс")
    print(dog.speak())
