"""
lock.acquire()
# critical section
lock.release()
     |
     |
    with lock():
      # critical section
"""

import time 
from threading import Thread, Lock 

lock = Lock()

def func1():
    lock.acquire()
    print("Thread1 acquired lock")
    time.sleep(3)
    lock.release()

def func2():
    while True:
        if lock.acquire(blocking=False):
            print("Thread2 acquired lock")
            time.sleep(4)
            lock.release()
            break
        else:
            print("Doing something else")
            time.sleep(1)

thread1 = Thread(target=func1)
thread2 = Thread(target=func2)

thread1.start()
thread2.start()

thread1.join()
thread2.join()