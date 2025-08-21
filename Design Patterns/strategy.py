"""
You’re building a checkout system that supports multiple payment methods:
    Credit Card
    UPI
    PayPal
Your system should:
    Let the user select their preferred payment method at runtime.
    Use the Strategy Pattern to cleanly separate the payment logic.
"""

from abc import ABC, abstractmethod

class Payment(ABC):

    @abstractmethod
    def pay(self, amount: float):
        raise NotImplementedError("Must be implemented by abstract classes")

class CreditCard(Payment):

    def __init__(self, card_number: str):
        self.card_number = card_number

    def pay(self, amount: float):
        print(f"Paid via Credit Card {self.card_number}: Rs.{amount}/-")
        return True

class UPI(Payment):

    def __init__(self, upi_id: str):
        self.upi_id = upi_id

    def pay(self, amount: float):
        print(f"Paid via UPI {self.upi_id}: Rs.{amount}/-")
        return True

class PayPal(Payment):

    def __init__(self, account_num: str):
        self.account_num = account_num

    def pay(self, amount: float):
        print(f"Paid via PayPal {self.account_num}: Rs.{amount}/-")
        return True

class PaymentStrategy(Payment):

    def __init__(self, strategy: Payment):
        self.strategy = strategy

    def pay(self, amount: float):
        return self.strategy.pay(amount=amount)

    def set_strategy(self, strategy: Payment):
        self.strategy = strategy


if __name__=="__main__":

    cc = CreditCard("1234567890")
    up = UPI("abc@okhdfcbank")
    pp = PayPal("ASIA078999")

    ps = PaymentStrategy(pp)
    ps.pay(50.10)
    ps.set_strategy(up)
    ps.pay(60.20)
    ps.set_strategy(pp)
    ps.pay(70.30)
