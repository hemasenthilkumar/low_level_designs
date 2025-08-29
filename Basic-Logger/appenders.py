"""
Destination for logs
Observer Pattern
Thread safe:
    - while printing to console
    - while writing to file
"""
from threading import Thread, Lock
from filelock import FileLock
from abc import ABC, abstractmethod

class LogAppender(ABC):

    @abstractmethod
    def append(self, formatted_msg: str):
        pass 


class ConsoleAppender(LogAppender):

    def __init__(self):
        self.lock = Lock()
    
    def append(self, formatted_msg: str):
        with self.lock:
            print(formatted_msg)

class FileAppender(LogAppender):

    def __init__(self, file_name: str):
        self.file_name = file_name 
        self.lock_file = f"{self.file_name}.lock"
        self.lock = FileLock(self.lock_file)
    
    def append(self, formatted_msg: str):

        with self.lock:
            with open(self.file_name, 'a', encoding='utf-8') as fp:
                fp.write(formatted_msg+"\n")
                fp.flush() # immediately writes the data to the file

if __name__ == "__main__":
    ca = ConsoleAppender()
    ca.append("[29-08-25 20:0535] [Thread-33852] [INFO] Application started")

    fa = FileAppender("test.txt")
    fa.append("[29-08-25 20:0535] [Thread-33852] [INFO] Application started")