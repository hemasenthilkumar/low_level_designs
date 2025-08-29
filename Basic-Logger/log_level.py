"""
Log Level using Enum
"""

from enum import Enum 

class LogLevel(Enum):
    TRACE = 0 # Low priority
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4 
    FATAL = 5  # High priority