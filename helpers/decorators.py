import functools
import time
import logging

logger = logging.getLogger(__name__)

def retry(times: int = 3, delay: float = 1.0, exceptions: tuple[type, ...] = (Exception,)):
    """
    Декоратор повтора при ошибках.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    logger.warning(f"Retry {attempt}/{times} for {func.__name__}: {e}")
                    time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator
