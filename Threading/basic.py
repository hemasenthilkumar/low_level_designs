"""
Threading Basics

CPU Bound: Lot of computation
 - data crunching
 - analysing loads of data
- Actual parallel work
I/O : Mostly input/output operations, third party involved
 - downloading file
 - network operations
 - reading data from disk
- Its not at the same time just an illusion
- There is overlapping but not parallel
"""

import threading
import time 

start = time.perf_counter()

def sleeping():
    print("Start sleeping")
    time.sleep(1)
    print("Done Sleeping")

#sleeping()
#sleeping()
""""
thread1 = threading.Thread(target=sleeping)
thread2 = threading.Thread(target=sleeping)

thread1.start()
thread2.start()

# wait for the thread to complete
# otherwise it will just proceed to next lines without completing
thread1.join()
thread2.join()
"""

threads = []

# Looping method for threads
for _ in range(10):
    thread = threading.Thread(target=sleeping)
    thread.start()
    # adding join here will be same as running without thread 
    threads.append(thread)

for thread in threads:
    thread.join()

end = time.perf_counter()
print(f"Time taken: {round(end-start,2)} seconds")


# Passing arguments

start = time.perf_counter()
def sleep_arg(seconds):
    print(f'Sleeping for {seconds}')
    time.sleep(seconds)
    return (f'Done sleeping for {seconds}')

threads = []

# Looping method for threads
for _ in range(10):
    thread = threading.Thread(target=sleep_arg, args=[1.5])
    thread.start()
    # adding join here will be same as running without thread 
    threads.append(thread)

for thread in threads:
    thread.join()

end = time.perf_counter()
print(f"Time taken: {round(end-start,2)} seconds")

print('*'*30)

# Using thread pool executor
import concurrent.futures

start = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor() as executor:
    f1 = executor.submit(sleep_arg, 1)
    f2 = executor.submit(sleep_arg, 1)
    print(f1.result()) # wait untill the function completes
    print(f2.result()) 
end = time.perf_counter()
print(f"Time taken: {round(end-start,2)} seconds")

print('*'*30)

start = time.perf_counter()
# with looping and list argument
with concurrent.futures.ThreadPoolExecutor() as executor:
    seconds = [5,4,3,2,1]
    result = [executor.submit(sleep_arg, sec) for sec in seconds]
    
    # we can use the iterator method of that module
    for f in concurrent.futures.as_completed(result):
        print(f.result())
end = time.perf_counter()
print(f"Time taken: {round(end-start,2)} seconds")

print('*'*30)

# using executor.map 
start = time.perf_counter()
# with looping and list argument
with concurrent.futures.ThreadPoolExecutor() as executor:
    seconds = [5,4,3,2,1]
    results = executor.map(sleep_arg, seconds)  # this will automatically wait for the threads to complete

    for result in results:
        print(result)

end = time.perf_counter()
print(f"Time taken: {round(end-start,2)} seconds")