from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from TA.support.domain.entities.base_entity import BaseEntity

@dataclass
class IBaseRepository(ABC):

    @abstractmethod
    async def get(self, id: int, only_active: bool = False) -> Optional[BaseEntity]:
        raise NotImplementedError()

    @abstractmethod
    async def get_all(self, only_active: bool = False) -> List[BaseEntity]:
        raise NotImplementedError()

    @abstractmethod
    async def exists(self, id: int, only_active: bool = False) -> bool:
        raise NotImplementedError()
