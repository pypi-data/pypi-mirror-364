import time
import asyncio
from abc import ABC, abstractmethod

class BaseCache(ABC):
    @abstractmethod
    def get(self, key):
        pass
    
    @abstractmethod
    def set(self, key, value, timeout=None):
        pass

class BaseAsyncCache(ABC):
    @abstractmethod
    async def aget(self, key):
        pass
    
    @abstractmethod
    async def aset(self, key, value, timeout=None):
        pass

class InMemoryCache(BaseCache):
    def __init__(self):
        self._cache = {}
        
    def get(self, key):
        if key not in self._cache:
            return None
            
        value, expiry = self._cache[key]
        if expiry and expiry < time.time():
            del self._cache[key]
            return None
            
        return value
        
    def set(self, key, value, timeout=None):
        expiry = time.time() + timeout if timeout else None
        self._cache[key] = (value, expiry)

class InMemoryAsyncCache(BaseAsyncCache):
    def __init__(self):
        self._cache = {}
        self._lock = asyncio.Lock()
        
    async def aget(self, key):
        async with self._lock:
            if key not in self._cache:
                return None

            value, expiry = self._cache[key]
            if expiry and expiry < asyncio.get_event_loop().time():
                del self._cache[key]
                return None

            return value
            
    async def aset(self, key, value, timeout=None):
        async with self._lock:
            expiry = asyncio.get_event_loop().time() + timeout if timeout else None
            self._cache[key] = (value, expiry)

def get_default_cache():
    return InMemoryCache()

def get_default_async_cache():
    return InMemoryAsyncCache()