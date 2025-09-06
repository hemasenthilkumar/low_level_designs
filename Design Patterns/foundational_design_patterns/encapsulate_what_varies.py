"""
Principle: Encapsulate what varies
------------------------
Challenges
- dealing with change
- adapt to change without any ripple effect

What?
- isolate parts of code which can change & encapsulate it
- creating a protective barrier that shields the other code from this changeable code

Benefits
- Ease of maintenance
- Enhanced flexibility
- Improved readability - it becomes more organized so its easy to read

Techniques
1. Polymorphism
2. Getters and Setters

Polymorphism
- allows objects of different classes to be treated as object of a common superclass
- enables single interface for different types
- helps implementing strategy pattern

Getters and Setters
- enable controlled access to attribute values
- we can implement using python's @property technique
- @attribute_name.setter -> invokes the setter method when we try to change the value
"""

#### Example 1 ####

class PaymentBase:

    def __init__(self, amount: int):
        self.amount = amount 
    
    def process_payment(self):
        pass 

class CreditCard(PaymentBase):

    def process_payment(self):
        print(f"Paid using credit card: {self.amount}")

class PayPal(PaymentBase):

    def process_payment(self):
        print(f"Paid using PayPal: {self.amount}")


#### Example 2 ####

class Circle:

    def __init__(self, radius: int):
        self._radius = radius 
    
    @property 
    def radius(self):
        return self._radius 

    @radius.setter 
    def radius(self, value: int):
        if value < 0:
            raise ValueError("Radius cannot be negative!")
        self._radius = value

if __name__ == "__main__":
    circle = Circle(5)
    print(f"Initial radius: {circle.radius}")
    circle.radius = 16
    print(f"Current radius: {circle.radius}")
    circle.radius = -15






if __name__ == "__main__":
    payments = [CreditCard(100), PayPal(200)]
    for payment in payments:
        payment.process_payment()