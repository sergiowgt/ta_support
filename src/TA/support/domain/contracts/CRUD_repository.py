from abc import ABC, abstractmethod
from TA.support.domain.contracts.ibase_repository import IBaseRepository
from TA.support.domain.entities.base_entity import BaseEntity

class ICRUDRepository(IBaseRepository, ABC):
    @abstractmethod
    async def add(self, obj: BaseEntity, created_by: str) -> None:
        pass

    @abstractmethod
    async def update(self, obj: BaseEntity, updated_by: str) -> None:
        pass

    @abstractmethod
    async def delete(self, obj: BaseEntity, updated_by: str) -> None:
        pass
