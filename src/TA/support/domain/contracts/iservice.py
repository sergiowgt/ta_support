from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from uuid import UUID

TEntity = TypeVar('TEntity')
TCreateSchema = TypeVar('TCreateSchema')
TUpdateSchema = TypeVar('TUpdateSchema')

class IService(Generic[TEntity, TCreateSchema, TUpdateSchema], ABC):
    @abstractmethod
    async def get(self, id: UUID) -> Optional[TEntity]:
        pass

    @abstractmethod
    async def list_all(self, only_active: bool = True) -> List[TEntity]:
        pass

    @abstractmethod
    async def create(self, data: TCreateSchema, created_by: str) -> TEntity:
        pass

    @abstractmethod
    async def update(self, id: UUID, data: TUpdateSchema, updated_by: str) -> None:
        pass

    @abstractmethod
    async def delete(self, id: UUID, updated_by: str) -> None:
        pass

    @abstractmethod
    async def activate(self, id: UUID, updated_by: str) -> None:
        pass

    @abstractmethod
    async def inactivate(self, id: UUID, updated_by: str) -> None:
        pass
