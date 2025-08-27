import time
from threading import Thread, Lock 

x = 0

def add_one():
    global x 
    for _ in range(1000000):
        x += 1

def subtract_one():
    global x
    for _ in range(10000000):
        x -= 1

thread1 = Thread(target=add_one)
thread2 = Thread(target=subtract_one)

thread1.start()
thread2.start()
thread1.join()
thread2.join()

print(x)  # 0 is right value
# but we got  -9639804 --> race condition occurred
import sys
print = lambda x: sys.stdout.write("%s\n" % x)  # avoid new line problems
lock = Lock()

def func1():
    print("Thread 1 is waiting to acquire the lock")
    lock.acquire()   # timeout -> how long i should wait, if the lock is not free at that time, just continue
    print("Thread 1 acquired the lock")
    time.sleep(10)  # critical section
    lock.release()
    print("Thread 1 is released the lock")

def func2():
    print("Thread 2 is waiting to acquire the lock")
    lock.acquire(timeout=3)
    # we can check if its acquired first and then do the work
    print("Thread 2 acquired the lock")
    time.sleep(2)  # critical section
    lock.release()
    print("Thread 2 is released the lock")

thread1 = Thread(target=func1)
thread2 = Thread(target=func2)

thread1.start()
thread2.start()
thread1.join()
thread2.join()