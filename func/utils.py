from functools import wraps
from time import time

def log(info):
    print('-' * 20 + ' ' + str(info) + ' ' + '-' * 20)

def timeit(func):
    @wraps(func)
    def timer(*args, **kwargs):
        print("Function [{name}] start ...".format(name=func.__name__))
        t0 = time()
        result = func(*args, **kwargs)
        t1 = time()
        print("Function [{name}] finished, spent time {time:.2f}s".format(name=func.__name__, time=t1 - t0))
        return result
    return timer
