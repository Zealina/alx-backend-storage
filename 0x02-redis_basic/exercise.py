#!/usr/bin/env python3
"""Redis module and practice"""

import asyncio
from typing import Callable, Optional, Union, List
from functools import wraps
from uuid import uuid4
import redis


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of times a method is called.
    Args:
        method (Callable): The method to be decorated.
    Returns:
        Callable: The decorated method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to count method calls.
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a function.
    Args:
        method (Callable): The method to be decorated.
    Returns:
        Callable: The decorated method.
    """
    key = method.__qualname__
    inputs = key + ":inputs"
    outputs = key + ":outputs"

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to store method call history.
        """
        self._redis.rpush(inputs, str(args))
        data = method(self, *args, **kwargs)
        self._redis.rpush(outputs, str(data))
        return data
    return wrapper


def replay(method: Callable) -> None:
    """
    Replays the history of a function.
    Args:
        method (Callable): The function to be replayed.
    Returns:
        None
    """
    name = method.__qualname__
    cache = redis.Redis()
    calls = cache.get(name)
    if calls is not None:
        calls_str = calls.decode('utf-8')
        print(f"{name} was called {calls_str} times:")
        inputs = cache.lrange(name + ":inputs", 0, -1)
        outputs = cache.lrange(name + ":outputs", 0, -1)
        for i, o in zip(inputs, outputs):
            print(f"{name}(*{i.decode('utf-8')}) -> {o.decode('utf-8')}")


class Cache:
    """
    Cache class to store data and manage caching operations.
    """
    def __init__(self):
        """
        Initializes the cache.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Stores data in the cache.
        Args:
            data (Union[str, bytes, int, float]): The data to be stored.
        Returns:
            str: The randomly generated key used to store the data.
        """
        randomKey = str(uuid4())
        self._redis.set(randomKey, data)
        return randomKey

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """
        Retrieves data from the cache.
        Args:
            key (str): The key used to retrieve the data.
            fn : Apply to the retrieved data. Defaults to None.
        Returns:
            Union[str, bytes, int, float]: The retrieved data.
        """
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        """
        Retrieves a string from the cache.
        Args:
            key (str): The key used to retrieve the string.
        Returns:
            str: The retrieved string.
        """
        value = self._redis.get(key)
        return value.decode('utf-8')

    def get_int(self, key: str) -> int:
        """
        Retrieves an integer from the cache.
        Args:
            key (str): The key used to retrieve the integer.
        Returns:
            int: The retrieved integer.
        """
        value = self._redis.get(key)
        try:
            value = int(value.decode('utf-8'))
        except Exception:
            value = 0
        return value
