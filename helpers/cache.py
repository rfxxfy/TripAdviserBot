from functools import lru_cache

def cached(maxsize: int = 128):
    """
    Декоратор‑обёртка для lru_cache.
    """
    def decorator(func):
        return lru_cache(maxsize=maxsize)(func)
    return decorator
