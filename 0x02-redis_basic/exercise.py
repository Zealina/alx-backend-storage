#!/usr/bin/env python3
"""Create Redis app"""

import redis
from uuid import uuid4
from typing import Union


class Cache:
    """Class yo cache stuff"""
    def __init__(self) -> None:
        """Create an instance or Redis"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, float, int, bytes]) -> str:
        """Create a key to store data"""
        key = str(uuid4())
        self._redis.set(key, data)
        return key
