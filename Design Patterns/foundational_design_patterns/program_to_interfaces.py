"""
Focusing too much on code can lead to tight coupling

Interface - defines a contract for classes, specifying a set of methods to be implemented
- Code against a interface rather than a concrete class

Benefits:
- Flexibility
- Maintainability
- Testability

Techniques:
- using ABC abstract base classes 
- protocols
"""
#### Example 1 ####

from abc import ABC, abstractmethod 

class MyInterface(ABC):

    @abstractmethod
    def do_something(self,some_param: str):
        pass  

class MyClass(MyInterface):

    def do_something(self, some_param: str):
        print(some_param)
    

#### Example 2 ####

"""
Using protocols
- structural duck typing
- usually type compatability at run time, but this allows type checking at runtime
- easier to debug and more robust
- object's behavior is more important than actual type
"""

from typing import Protocol, runtime_checkable

class Flyer(Protocol):
    def fly(self):  #--> now any class has fly would be considered as Flyer
        pass 

# Logger example
from abc import ABC, abstractmethod 

class Logger(ABC):

    @abstractmethod 
    def log(self, message: str):
        pass 

class ConsoleLogger(Logger):
    def log(self, message: str):
        print(f"Console: {message}")

class FileLogger(Logger):
    def log(self, message: str):
        with open('log.txt', 'w') as fp:
            fp.write(message)

# Same example logger using protocols

@runtime_checkable
class Logger_P(Protocol):
    def log_message(self, message: str):
        pass 
class Console_Logger():
    def log_message(self, message: str):
        print(f"Console: {message}")
class File_Logger():
    def log_message(self, message: str):
        print(f"File: {message}")

if __name__ == "__main__":
    cl = MyClass()
    cl.do_something("Hello")

    logger = ConsoleLogger()
    logger.log("Welcome!")

    flogger = File_Logger()
    flogger.log_message("Hi!!!!")
    print(isinstance(File_Logger(), Logger_P))  # ✅ True