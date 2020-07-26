import time

timeout_time=10

def make_request():
    print("making a request")

unlock_time=0

while True:
    current_time=int(time.time())
    if current_time>=unlock_time:
        make_request()
        unlock_time=int(time.time())+timeout_time
    else:
        print(f"waiting for {unlock_time-current_time} more seconds")
    time.sleep(1)