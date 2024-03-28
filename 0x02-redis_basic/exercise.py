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

    @property
    def redis(self) -> redis.Redis:
        """Getter"""
        return self._redis

    @redis.setter
    def redis(self, value) -> None:
        """Setter"""
        self._redis = value

    def store(self, data: Union[str, float, int, bytes]) -> str:
        """Create a key to store data"""
        key = str(uuid4())
        self.redis.set(key, data)
        return key
