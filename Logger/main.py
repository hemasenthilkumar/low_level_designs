import os
from enum import Enum
from abc import ABC
from datetime import datetime
from threading import Lock


class LogConfiguration(ABC):

    def setup_config(self):
        raise NotImplementedError("Need to implement by subclasses")


class AppenderFactory:

    @staticmethod
    def get_appender(type: str, config_obj: LogConfiguration):
        if 'console' in type:
            aobj = ConsoleAppender(config_obj)
        elif 'file' in type:
            aobj = FileAppender(config_obj)
        elif 'db' in type:
            aobj = DBAppender(config_obj)
        else:
            print("ERROR: Unknown object only console | file | db are supported.")
            return None
        return aobj

class Appender(ABC):

    def log(self, msg: str, log_level: str):
        raise NotImplementedError("Must be implemented by subclasses.")

class FileAppender(Appender):

    def __init__(self, config_obj: LogConfiguration):
        self.config = config_obj

    def log(self, msg: str, log_level: str):
        self.msg = LogMessage(msg, log_level).get_msg()
        with open(self.config.filename, 'a') as fp:
            fp.write(self.msg)

class ConsoleAppender(Appender):

    def __init__(self, config_obj: LogConfiguration):
        self.config = config_obj

    def log(self, msg: str, log_level: str):
        self.msg = LogMessage(msg, log_level).get_msg()
        print(f"[{self.config.prefix}] {self.msg}")

class DBAppender(Appender):

    def __init__(self, config_obj: LogConfiguration):
        self.config = config_obj

    def log(self, msg: str, log_level: str):
        self.msg = LogMessage(msg, log_level).get_msg()
        print(f"INSERT into msg table: {self.msg}")

class LogLevels(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    FATAL = 4
    TRACE = 5

class LogMessage:

    def __init__(self, msg: str, log_level: LogLevels):
        self.msg = msg
        self.log_level = log_level

    def get_msg(self):
        now = datetime.now().strftime("%d%m%y_%H%M%S")
        msg = f"[{now}][{self.log_level.name}]: {self.msg}"
        return msg

class ConsoleConfig(LogConfiguration):

    def __init__(self, prefix: str = 'CONSOLE'):
        self.prefix = prefix

    def setup_config(self):
        print("Log configuration set to Console")

class FileConfig(LogConfiguration):

    def __init__(self,filename: str):
        self.filename = filename

    def setup_config(self):
        print("Setting up file appender configuration...")
        print(f"Checking and creating file {self.filename}")
        if os.path.exists(self.filename) == False:
            with open(self.filename, 'w') as fp:
                fp.write('Log Configuration Set to File')
        else:
            with open(self.filename, 'a') as fp:
                fp.write('Log Configuration Set to File')

class DBConfig(LogConfiguration):

    ## assume only SQL is supported now
    def __init__(self, db_conn_str: str, table: str):
        self.conn = DBObject(db_conn)
        self.table = self.conn[table]

    def setup_config(self):
        # create table if not present
        pass

class Logger:

    def __init__(self, output_type: str, config_obj: LogConfiguration):
        self.output_type = output_type
        self.aobj = AppenderFactory.get_appender(output_type, config_obj)
        self.lock = Lock()

    def log(self, msg: str, log_level: str):
        if log_level.lower() not in ['info', 'debug', 'warning', 'fatal', 'trace']:
            raise Exception("Only these values are allowed \
                for log level: info | debug | warning | fatal | trace ")
        self.msg = msg
        self.log_level = LogLevels[log_level.upper()]
        with self.lock:
            self.aobj.log(self.msg, self.log_level)


if __name__ == "__main__":
    cs_config = ConsoleConfig()
    cs_config.setup_config()
    logger = Logger('console', cs_config)
    logger.log("Hello world!", "info")
