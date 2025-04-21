import time
from functools import wraps
from typing import Callable, Any

_metrics: dict[str, Any] = {}

def incr(name: str, value: int = 1):
    _metrics[name] = _metrics.get(name, 0) + value

def gauge(name: str, value: float):
    _metrics[name] = value

def timing(name: str):
    """
    Декоратор замера времени выполнения функции.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            res = func(*args, **kwargs)
            _metrics[name] = time.time() - start
            return res
        return wrapper
    return decorator

def get_metrics() -> dict[str, Any]:
    return dict(_metrics)
