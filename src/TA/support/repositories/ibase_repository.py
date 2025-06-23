from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from TA.support.domain.entities.base_entity import BaseEntity

@dataclass
class IBaseRepository (ABC):

    @abstractmethod
    def get(self, id: int) -> BaseEntity:
        raise NotImplementedError()

    @abstractmethod
    def get_all(self) -> List[BaseEntity]:
        raise NotImplementedError()

    @abstractmethod
    def exists(self, id: int, only_active: bool = False) -> bool:
        raise NotImplementedError()