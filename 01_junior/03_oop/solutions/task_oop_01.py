"""
Рішення — Урок 1 (Класи та об'єкти)

Дивись після того, як спробував сам!
"""


class Book:
    def __init__(self, title: str, author: str) -> None:
        self.title = title
        self.author = author

    def info(self) -> str:
        return f"Книга: {self.title}, автор: {self.author}"


class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


class BankAccount:
    def __init__(self, balance: float) -> None:
        self.balance = balance

    def deposit(self, amount: float) -> None:
        if amount > 0:
            self.balance += amount

    def get_balance(self) -> float:
        return self.balance


# Перевірка
book = Book("1984", "Оруелл")
print(book.info())

rect = Rectangle(5, 10)
print("Площа:", rect.area())

acc = BankAccount(100)
acc.deposit(50)
print("Баланс:", acc.get_balance())
