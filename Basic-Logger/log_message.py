"""
Log Message Class
"""
import threading
from log_level import LogLevel
from datetime import datetime

class LogMessage:

    def __init__(self, level: LogLevel,  message: str, timestamp: datetime = None, thread_id: int = None,
                 metadata: dict = None):
        self.level = level
        self.message = message
        self.timestamp = timestamp if timestamp else datetime.now().strftime('%d-%m-%y %H:%M%S')
        self.thread_id = thread_id if thread_id else threading.get_ident()
        self.metadata = metadata if metadata else {}
    
    def __str__(self):
        string = f"""
                    Log Level: {self.level.name}
                    Message: {self.message}
                    Timestamp: {self.timestamp}
                    Thread ID: {self.thread_id}
                    Metadata: {self.metadata}
        """
        return string

    def __dict__(self):
        log_dict = {
            'log_level': self.level.name, 
            'message': self.message,
            'timestamp': self.timestamp, 
            'thread_id': self.thread_id, 
            'metadata': self.metadata
        }
        return log_dict


if __name__ == "__main__":
    logm = LogMessage(LogLevel.INFO, "Hello")
    print(logm.__str__())
    print(logm.__dict__())