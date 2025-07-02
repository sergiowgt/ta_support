from dataclasses import dataclass
from typing import Any
from TA.support.infra.database.idb_handler import IDbHandler
from .base_repository import BaseRepository
from ..domain.entities.base_entity import BaseEntity
from ..domain.enums.status_enum import StatusEnum

@dataclass
class CRUDRepository(BaseRepository):
    def __init__(self, db: IDbHandler, entity: Any):
        super().__init__(db, entity)

    async def add(self, obj: BaseEntity) -> None:
        obj.id = None
        obj.status = StatusEnum.ACTIVE
        self._session.add(obj)
        await self._session.flush()  # Alterado para async

    async def delete(self, obj: BaseEntity) -> None:
        obj.status = StatusEnum.LOGICALLY_DELETED
        # Persistência imediata opcional:
        # await self._session.flush()
