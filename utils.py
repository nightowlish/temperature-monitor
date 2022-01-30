import time


def get_timestamp():
    return int(time.time() * 1000)

def median(values):
    if not values:
        return None
    n = len(values)
    s = sorted(values)
    return (sum(s[n//2-1:n//2+1])/2.0, s[n//2])[n % 2] 
