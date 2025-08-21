"""
Problem:
You're building a stock price monitor. Multiple users want to subscribe to a
stock and get notified when its price changes.

Requirements:
Stock is the Subject. It allows users to subscribe/unsubscribe.

Investor is the Observer. They get notified of price changes.

When the stock price is updated, all subscribed investors are notified.
"""

from abc import ABC, abstractmethod

class AbstractStock(ABC):

    @abstractmethod
    def notify(self, msg: str):
        raise NotImplementedError("Must be implemented by concrete class")

class AbstractInvestor(ABC):

    @abstractmethod
    def recieve(self, msg: str):
        raise NotImplementedError("Must be implemented by concrete class")

class Investor(AbstractInvestor):

    def __init__(self, name: str):
        self.name = name

    def recieve(self, msg: str):
        print(msg)

class Stock(AbstractStock):

    def __init__(self, stock_name: str, price: float):
        self.name = stock_name
        self.price = price
        self.observers = []

    def add_observer(self, observer: Investor):
        self.observers.append(observer)

    def update_price(self, new_price: float):
        self.price = new_price
        msg = f"The price of {self.name} stock has been changed to {self.price}"
        self.notify(msg)

    def notify(self, msg: str):
        for ob in self.observers:
            ob.recieve(f"Hi {ob.name} " + msg)

if __name__=="__main__":

    s1 = Stock("NIFTY50", 191.12)
    s2 = Stock("GOLDBEES",72.0)
    i1 = Investor("Hema")
    i2 = Investor("Vasanth")

    s1.add_observer(i1)
    s1.add_observer(i2)
    s2.add_observer(i1)
    s2.add_observer(i2)

    s1.update_price(200)
    s2.update_price(74)
