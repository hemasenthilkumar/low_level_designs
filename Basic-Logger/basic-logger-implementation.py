#!/usr/bin/env python3
"""
FAANG LLD: Basic Thread-Safe Logger Implementation
Key Concepts: Singleton, Factory, Strategy, Observer, Threading

This implementation covers:
1. Thread-safe Singleton logger
2. Multiple log levels and formatters
3. Producer-Consumer pattern with queues
4. Basic batching mechanism
"""

import threading
import queue
import time
import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any
from datetime import datetime
import sys


class LogLevel(Enum):
    """Log levels with priority ordering"""
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5


class LogMessage:
    """Represents a single log message"""
    def __init__(self, level: LogLevel, message: str, timestamp: float = None, 
                 thread_id: int = None, metadata: Dict = None):
        self.level = level
        self.message = message
        self.timestamp = timestamp or time.time()
        self.thread_id = thread_id or threading.get_ident()
        self.metadata = metadata or {}


# STRATEGY PATTERN: Different formatters
class LogFormatter(ABC):
    """Abstract base class for log formatters"""
    
    @abstractmethod
    def format(self, log_message: LogMessage) -> str:
        pass


class PlainTextFormatter(LogFormatter):
    """Plain text log formatter"""
    
    def format(self, log_message: LogMessage) -> str:
        dt = datetime.fromtimestamp(log_message.timestamp)
        return f"[{dt.isoformat()}] [{log_message.level.name}] [Thread-{log_message.thread_id}] {log_message.message}"


class JSONFormatter(LogFormatter):
    """JSON log formatter"""
    
    def format(self, log_message: LogMessage) -> str:
        log_dict = {
            'timestamp': log_message.timestamp,
            'level': log_message.level.name,
            'thread_id': log_message.thread_id,
            'message': log_message.message,
            'metadata': log_message.metadata
        }
        return json.dumps(log_dict)


# OBSERVER PATTERN: Multiple appenders
class LogAppender(ABC):
    """Abstract base class for log appenders"""
    
    @abstractmethod
    def append(self, formatted_message: str):
        pass


class ConsoleAppender(LogAppender):
    """Writes logs to console"""
    
    def __init__(self):
        self._lock = threading.Lock()
    
    def append(self, formatted_message: str):
        with self._lock:
            print(formatted_message)


class FileAppender(LogAppender):
    """Writes logs to file"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self._lock = threading.Lock()
    
    def append(self, formatted_message: str):
        with self._lock:
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(formatted_message + '\n')
                f.flush()  # Ensure immediate write


# FACTORY PATTERN: Create different loggers
class LoggerFactory:
    """Factory to create different types of loggers"""
    
    @staticmethod
    def create_console_logger(formatter: LogFormatter = None) -> 'Logger':
        formatter = formatter or PlainTextFormatter()
        appender = ConsoleAppender()
        return Logger.get_instance().add_appender(appender).set_formatter(formatter)
    
    @staticmethod
    def create_file_logger(filename: str, formatter: LogFormatter = None) -> 'Logger':
        formatter = formatter or PlainTextFormatter()
        appender = FileAppender(filename)
        return Logger.get_instance().add_appender(appender).set_formatter(formatter)


# SINGLETON PATTERN: Thread-safe singleton logger
class Logger:
    """Thread-safe singleton logger with async processing"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.min_level = LogLevel.INFO
        self.formatter = PlainTextFormatter()
        self.appenders: List[LogAppender] = []
        
        # Producer-Consumer setup for async logging
        self.log_queue = queue.Queue(maxsize=10000)  # Bounded queue for backpressure
        self.batch_size = 100
        self.batch_timeout = 5.0  # seconds
        self.shutdown_event = threading.Event()
        
        # Start consumer thread
        self.consumer_thread = threading.Thread(target=self._consume_logs, daemon=True)
        self.consumer_thread.start()
        
        # Register cleanup on exit
        import atexit
        atexit.register(self.shutdown)
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        return cls()
    
    def set_level(self, level: LogLevel) -> 'Logger':
        """Set minimum log level"""
        self.min_level = level
        return self
    
    def set_formatter(self, formatter: LogFormatter) -> 'Logger':
        """Set log formatter"""
        self.formatter = formatter
        return self
    
    def add_appender(self, appender: LogAppender) -> 'Logger':
        """Add log appender (Observer pattern)"""
        self.appenders.append(appender)
        return self
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if message should be logged based on level"""
        return level.value >= self.min_level.value
    
    def _log(self, level: LogLevel, message: str, metadata: Dict = None):
        """Internal logging method"""
        if not self._should_log(level):
            return
        
        log_message = LogMessage(level, message, metadata=metadata)
        
        try:
            # Non-blocking put with timeout
            self.log_queue.put(log_message, timeout=0.1)
        except queue.Full:
            # Handle backpressure: could drop, block, or use circuit breaker
            # For now, we'll drop the message (fail-fast)
            self._handle_queue_full(log_message)
    
    def _handle_queue_full(self, log_message: LogMessage):
        """Handle queue full scenario - this is a key design decision"""
        # Strategy 1: Drop the message (current implementation)
        print(f"WARNING: Log queue full, dropping message: {log_message.message}", file=sys.stderr)
        
        # Strategy 2: Block and wait (could use log_queue.put(log_message) without timeout)
        # Strategy 3: Implement circuit breaker pattern
    
    def _consume_logs(self):
        """Consumer thread that processes logs in batches"""
        batch = []
        last_flush_time = time.time()
        
        while not self.shutdown_event.is_set():
            try:
                # Try to get a message with timeout
                try:
                    log_message = self.log_queue.get(timeout=1.0)
                    batch.append(log_message)
                except queue.Empty:
                    # Timeout occurred, check if we should flush
                    pass
                
                # Check flush conditions
                should_flush = (
                    len(batch) >= self.batch_size or  # Size-based flush
                    (batch and time.time() - last_flush_time >= self.batch_timeout)  # Time-based flush
                )
                
                if should_flush:
                    self._flush_batch(batch)
                    batch = []
                    last_flush_time = time.time()
                    
            except Exception as e:
                print(f"Error in log consumer: {e}", file=sys.stderr)
        
        # Flush remaining logs on shutdown
        if batch:
            self._flush_batch(batch)
    
    def _flush_batch(self, batch: List[LogMessage]):
        """Flush a batch of log messages to all appenders"""
        if not batch:
            return
        
        for log_message in batch:
            formatted_message = self.formatter.format(log_message)
            
            # Send to all appenders (Observer pattern)
            for appender in self.appenders:
                try:
                    appender.append(formatted_message)
                except Exception as e:
                    print(f"Error in appender: {e}", file=sys.stderr)
    
    # Public logging methods
    def trace(self, message: str, metadata: Dict = None):
        self._log(LogLevel.TRACE, message, metadata)
    
    def debug(self, message: str, metadata: Dict = None):
        self._log(LogLevel.DEBUG, message, metadata)
    
    def info(self, message: str, metadata: Dict = None):
        self._log(LogLevel.INFO, message, metadata)
    
    def warn(self, message: str, metadata: Dict = None):
        self._log(LogLevel.WARN, message, metadata)
    
    def error(self, message: str, metadata: Dict = None):
        self._log(LogLevel.ERROR, message, metadata)
    
    def fatal(self, message: str, metadata: Dict = None):
        self._log(LogLevel.FATAL, message, metadata)
    
    def shutdown(self):
        """Graceful shutdown - flush all pending logs"""
        print("Shutting down logger...")
        self.shutdown_event.set()
        
        # Wait for consumer thread to finish
        if self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=10.0)


# Demo usage and testing
if __name__ == "__main__":
    # Create loggers using factory pattern
    logger = LoggerFactory.create_console_logger(JSONFormatter())
    logger.add_appender(FileAppender("app.log"))
    logger.set_level(LogLevel.DEBUG)
    
    # Test single-threaded logging
    logger.info("Application started")
    logger.debug("Debug information", {"user_id": 123})
    logger.error("Something went wrong!")
    
    # Test multi-threaded logging
    def worker_thread(thread_id: int):
        for i in range(10):
            logger.info(f"Worker {thread_id} - Message {i}")
            time.sleep(0.01)
    
    # Start multiple threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker_thread, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Simulate high-load scenario
    print("\nTesting high-load scenario...")
    start_time = time.time()
    for i in range(1000):
        logger.info(f"High load message {i}")
    
    # Give time for processing
    time.sleep(2)
    end_time = time.time()
    print(f"Processed 1000 messages in {end_time - start_time:.2f} seconds")
    
    # Test graceful shutdown
    print("\nTesting graceful shutdown...")
    logger.shutdown()
    print("Logger shutdown complete")
