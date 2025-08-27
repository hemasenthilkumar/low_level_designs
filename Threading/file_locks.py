from filelock import FileLock 
from threading import Thread, Lock 

file_name = 'example.txt'
lockfile = 'example.txt.lock'


lock = FileLock(lockfile)

lock.acquire()
print("Lock acquired!")
try:
    with open(file_name, 'w') as fp:
        fp.write("Add some data")
finally:
    lock.release()

