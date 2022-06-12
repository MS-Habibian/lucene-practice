import functools
import time


def record_time(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        function_name = '.'.join([func.__module__, func.__qualname__])
        res = func(self, *args, **kwargs)
        exec_time = time.time() - start_time
        print(f'execution time for {function_name}: ', exec_time)
        return res, exec_time
    return wrapper