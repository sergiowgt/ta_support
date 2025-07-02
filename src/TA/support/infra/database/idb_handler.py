# src/infra/db_handlers/idb_handler.py
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

class IDbHandler(ABC):
    @abstractmethod
    def get_session(self) -> AsyncSession: ...
    
    @abstractmethod
    async def commit(self): ...
    
    @abstractmethod
    async def rollback(self): ...
    
    @abstractmethod
    async def __aenter__(self): ...
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...
