"""
Thread Safe Efficient Logger Class
"""

import time
import threading
from queue import Queue, Full, Empty
from log_message import LogMessage
from log_level import LogLevel
from threading import Thread, Lock
from formatters import PlainFormatter
from appenders import ConsoleAppender, FileAppender

class Logger:

    _instance = None 
    _lock = Lock()

    def __new__(cls):

        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    # then initialize it 
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False # because we already initialized  
        return cls._instance
    
    def __init__(self):

        if self._initialized:
            print("Already one instance available!")
            return  # if we have to initialize also no need to initialize again
        
        self._initialized = True
        self.min_level = LogLevel.TRACE 
        self.formatter = PlainFormatter()
        self.appenders = []
        
        self.queue = Queue(maxsize = 1000)

        self.shutdown_event = threading.Event()
        self.consumer_thread = threading.Thread(target = self._consume_logs, daemon=True)
        self.consumer_thread.start()
        self.batch_size = 100
        self.batch_timeout = 1.0

        print("Logger initialized!")

    def set_min_level(self, min_level: LogLevel):
        self.min_level = min_level 
        return self
    
    def set_formatter(self, formatter):
        self.formatter = formatter 
        return self
    
    def set_appender(self, appender):
        self.appenders.append(appender)
        return self

    def _log(self, msg: str, log_level: LogLevel, metadata: dict = None):
        """
        1. Check the log level
        2. Create log message
        3. Format the message
        4. Send to all appenders
        """
        if self._should_log(log_level):

            log_message = LogMessage(log_level, msg, metadata = metadata)
            try:
                self.queue.put(log_message, timeout = 0.1)
            except Full:
                self._handle_queue_full(msg)

    
    def _should_log(self, log_level: LogLevel) -> bool:
        """
        Logs should be printed only if log_level >= min_level
        """
        return log_level.value >= self.min_level.value

    def trace(self, msg: str, metadata: dict = None):
        self._log(msg, LogLevel.TRACE, metadata)

    def debug(self, msg: str, metadata: dict = None):
        self._log(msg, LogLevel.DEBUG, metadata)

    def info(self, msg: str, metadata: dict = None):
        self._log(msg, LogLevel.INFO, metadata) 
    
    def warn(self, msg: str,  metadata: dict = None):
        self._log(msg, LogLevel.WARNING, metadata)

    def error(self, msg: str, metadata: dict = None):
        self._log(msg, LogLevel.ERROR, metadata)

    def fatal(self, msg: str, metadata: dict = None):
        self._log(msg, LogLevel.FATAL, metadata)

    def _handle_queue_full(self, log_msg: LogMessage):

        print(f"WARNING: Queue is FULL, dropping this current message {log_msg.__str__()}")

    def _consume_logs(self):

        batch = []
        last_flush_time = time.time()
        while not self.shutdown_event.is_set():
            try:
                try:
                    msg = self.queue.get(timeout=0.1)
                    batch.append(msg)
                except Empty:
                    continue 
                
                should_flush = (len(batch) >= self.batch_size) or \
                    (batch and last_flush_time - time.time() >= self.batch_timeout)

                if should_flush:
                    self._flush(batch)
                    batch = []
                    last_flush_time = time.time()

            except Exception as exp:
                print(f"Unable to process logs due to {exp}")
            
        # if still batch has some items 
        if batch:
            self._flush(batch)

    def _flush(self, batch):
        try:
            for msg in batch:
                formatted_msg = self.formatter.format(msg)

                for app in self.appenders:
                    app.append(formatted_msg)
        except Exception as exp:
            print(f"Unable to append logs due to {exp}")

    def shutdown(self):
        self.shutdown_event.set()
        self.consumer_thread.join()


if __name__ == "__main__":
    pf = PlainFormatter()
    ca = ConsoleAppender()
    fa = FileAppender('test_log.log')
    log = Logger().set_min_level(LogLevel.DEBUG).set_formatter(pf).set_appender(ca).set_appender(fa)

    #print(log.min_level)
    #print(log.formatter)
    #print(len(log.appenders))

    # Step 3: Log some events
    log.info("Application started")
    log.debug("Processing data...", metadata={"user": "hema"})
    log.warn("Low disk space warning")
    log.error("Something went wrong", metadata={"error_code": 500})

    # Worker function
    def worker(thread_id: int):
        for i in range(5):
            log.info(f"Thread {thread_id} logging message {i}")
            time.sleep(0.1)

    # Step 3: Launch multiple threads
    threads = []
    for t_id in range(5):  # 5 worker threads
        t = threading.Thread(target=worker, args=(t_id,))
        threads.append(t)
        t.start()

    # Step 4: Wait for all threads to finish
    for t in threads:
        t.join()

    # Step 5: Clean shutdown
    log.shutdown()