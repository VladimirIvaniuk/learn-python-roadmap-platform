"""
Рішення — Урок 2 (Наслідування)

Дивись після того, як спробував сам!
"""


class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return "..."


class Dog(Animal):
    def speak(self) -> str:
        return "Гав!"


class Vehicle:
    def __init__(self, brand: str, model: str) -> None:
        self.brand = brand
        self.model = model

    def info(self) -> str:
        return f"{self.brand} {self.model}"


class Car(Vehicle):
    def __init__(self, brand: str, model: str, doors: int) -> None:
        super().__init__(brand, model)
        self.doors = doors

    def info(self) -> str:
        return f"{self.brand} {self.model}, {self.doors} дверей"


class Product:
    def __init__(self) -> None:
        self._price = 0.0

    def get_price(self) -> float:
        return self._price

    def set_price(self, amount: float) -> None:
        if amount >= 0:
            self._price = amount


# Перевірка
dog = Dog("Рекс")
print(dog.speak())

car = Car("Toyota", "Camry", 4)
print(car.info())

prod = Product()
prod.set_price(99.99)
print("Ціна:", prod.get_price())
