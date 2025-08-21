import time
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:

    def __init__(self):
        self.track_dict = defaultdict(datetime)
        self.limit_per_10_sec = 5
        self.timer = None
        self.counter = 0
        # track_dict = {time: count}

    def allow_request(self, user_id: str) -> bool:
        if not self.timer:
            self.timer = datetime.now()
            if self.counter < self.limit_per_10_sec:
                self.counter += 1
            print("First time, Allowed!")
        else:
            print(self.timer, datetime.now())
            diff = datetime.now() - self.timer 
            print(diff.total_seconds())
            if diff.total_seconds() <= 10:
                if self.counter >= self.limit_per_10_sec:
                    print("Limit exceeded, please wait for few seconds and retry")
                else:
                    self.counter += 1
                    print("Allowed!")
            else:
                self.timer = datetime.now()
                self.counter = 1
                print("Reset to next 10 seconds, Allowed!")


if __name__=="__main__":
    rl = RateLimiter()
    for i in range(30):
        print("Asking request")
        time.sleep(1)
        rl.allow_request(str(i))
