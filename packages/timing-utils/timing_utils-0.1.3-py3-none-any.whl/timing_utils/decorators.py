import time
from functools import wraps

from loguru import logger


def async_timeit(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logger.debug(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds.")
        return result

    return wrapper


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logger.debug(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds.")
        return result

    return wrapper
