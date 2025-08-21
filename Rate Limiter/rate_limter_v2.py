import time
import threading
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:

    def __init__(self, max_requests: int = 5, window_time: int = 10):
        self.track_dict = defaultdict(dict)
        self.max_requests = max_requests
        self.window_time = window_time
        self.user_locks = defaultdict(threading.Lock)

    def allow_request(self, user_id: str) -> bool:
        with self.user_locks[user_id]:
            if not self.track_dict[user_id]:
                self.track_dict[user_id] = { 'requested_time': datetime.now(), 'count': 0 }
                self.track_dict[user_id]['count'] += 1
                print("First time, Allowed!")
                return True
            else:
                #print(self.track_dict[user_id]['requested_time'], datetime.now())
                diff = datetime.now() - self.track_dict[user_id]['requested_time']
                #print(diff.total_seconds())
                if diff.total_seconds() <= self.window_time:
                    if self.track_dict[user_id]['count'] >= self.max_requests:
                        print("Limit exceeded, please wait for few seconds and retry")
                        return False
                    else:
                        self.track_dict[user_id]['count'] += 1
                        print("Allowed!")
                        return True
                else:
                    self.track_dict[user_id]['requested_time'] = datetime.now()
                    self.track_dict[user_id]['count'] = 1
                    print("Reset to next 10 seconds, Allowed!")
                    return True


import threading
import time

def make_requests(rate_limiter, user_id):
    for _ in range(3):
        allowed = rate_limiter.allow_request(user_id)
        print(f"Thread {threading.current_thread().name}: Allowed = {allowed}")
        time.sleep(1)

if __name__ == "__main__":
    rl = RateLimiter(max_requests=5, window_time=10)
    threads = []

    for i in range(10):
        t = threading.Thread(target=make_requests, args=(rl, "user123"), name=f"T{i}")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
