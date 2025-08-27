"""
Reentrant Locks

special variant of locks - allows to acquire lock more than 1 if its on a recursive level
"""

import time
from threading import Thread, Lock, RLock

#lock = Lock()  # this will create problem incase of deadlock
lock = RLock()
# its a normal lock only, it will allow only incase of special cases

def task1():
    print("Task 1 is waiting to acquire lock")
    lock.acquire()
    print("Task 1 has acquired lock")
    time.sleep(2)
    lock.release()
    print("Task 1 has released lock")

def task2():
    print("Task 2 is waiting to acquire lock")
    lock.acquire()
    print("Task 2 has acquired lock")
    task1()  # --> DEADLOCK Situation
    time.sleep(2)
    lock.release()
    print("Task 2 has released lock")

thread1 = Thread(target=task1)
thread2 = Thread(target=task2)

thread1.start()
thread2.start()

thread1.join()
thread2.join()