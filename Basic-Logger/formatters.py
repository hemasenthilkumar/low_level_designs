"""
Formatters
"""

import json
from abc import ABC, abstractmethod 
from log_message import LogMessage
from log_level import LogLevel

class LogFormatter(ABC):

    @abstractmethod
    def format(self, message: LogMessage):
        pass

class PlainFormatter(LogFormatter):

    def __init__(self):
        print("Initializing plain formatter")

    def format(self, message: LogMessage):
        msg_format = f"[{message.timestamp}] [Thread-{message.thread_id}] [{message.level.name}] {message.message}"
        return msg_format

class JSONFormatter(LogFormatter):

    def __init__(self):
        print("Intializing JSON formatter")

    def format(self, message: LogMessage):
        log = message.__dict__()
        return json.dumps(log)

if __name__ == "__main__":

    lm = LogMessage(LogLevel.INFO, "Application started")

    pf = PlainFormatter()
    fm = pf.format(lm)
    print(fm)

    jf = JSONFormatter()
    jm = jf.format(lm)
    print(jm)