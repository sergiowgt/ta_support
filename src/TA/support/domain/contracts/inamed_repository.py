from abc import ABC, abstractmethod
from typing import Any, Optional

from TA.support.domain.contracts.ibase_repository import IBaseRepository

class INamedRepository(IBaseRepository, ABC):
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def get_all(self, only_active=True, name_like=None, page=1, page_size=20):
        pass
