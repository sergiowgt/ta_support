from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from uuid import UUID

TEntity = TypeVar('TEntity')

class IReadOnlyService(Generic[TEntity], ABC):
    @abstractmethod
    async def get(self, id: UUID) -> Optional[TEntity]:
        pass

    @abstractmethod
    async def list_all(self, only_active: bool = True) -> List[TEntity]:
        pass
