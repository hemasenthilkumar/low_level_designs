"""
Inheritance can get complex & tightly coupled

- So its better to composing objects from smaller classes instead of inheriting at base class
- Build complex objects by combining simpler ones

Benefits:
- Flexibility
- Reusability
- Ease of maintenance

Techniques
- Has-a relationship
"""

class Engine:
    def start(self):
        print("Engine started")

class Car:

    def __init__(self):
        self.engine = Engine()
    
    def start(self):
        self.engine.start()
        print("Car started")
    
if __name__ == "__main__":
    car = Car()
    car.start()
