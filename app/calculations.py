def add(a: int, b: int):
    return a + b


def substract(a: int, b: int):
    return a - b


def multiply(a: int, b: int):
    return a * b


def divide(a: int, b: int):
    return a / b


class BankAccount:
    def __init__(self, starting_balance=0):
        self.balance = starting_balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFunds("Insufficient operation")
        self.balance -= amount

    def collect_interest(self):
        self.balance *= 1.1


class InsufficientFunds(Exception):
    pass
