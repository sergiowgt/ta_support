from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager

class IUnitOfWork(AbstractAsyncContextManager):
    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass
