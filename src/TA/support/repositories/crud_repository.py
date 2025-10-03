from dataclasses import dataclass
from datetime import datetime
from typing import Any
from TA.support.domain.contracts.CRUD_repository import ICRUDRepository
from TA.support.infra.database.idb_handler import IDbHandler
from .base_repository import BaseRepository
from ..domain.entities.base_entity import BaseEntity
from ..domain.enums.status_enum import StatusEnum

@dataclass
class CRUDRepository(BaseRepository, ICRUDRepository):
    def __init__(self, db: IDbHandler, entity: Any):
        super().__init__(db, entity)

    async def add(self, obj: BaseEntity, created_by: str) -> None:
        obj.id = None
        obj.created_at = datetime.now()
        obj.created_by = created_by
        obj.status = StatusEnum.ACTIVE.value
        obj.validate()
        self._session.add(obj)
        await self._session.flush()  

    async def update(self, obj: BaseEntity, updated_by: str) -> None:
        obj.updated_at = datetime.now()
        obj.updated_by = updated_by
        obj.validate()

    async def delete(self, obj: BaseEntity, updated_by: str) -> None:
        obj.updated_at = datetime.now()
        obj.updated_by = updated_by
        obj.status = StatusEnum.LOGICALLY_DELETED.value
