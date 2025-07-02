from dataclasses import dataclass
from typing import Any, Optional
from TA.support.infra.database.idb_handler import IDbHandler
from .base_repository import BaseRepository
from ..domain.entities.named_base_entity import NamedBaseEntity
from ..domain.enums.status_enum import StatusEnum
from sqlalchemy.future import select

@dataclass
class NamedRepository(BaseRepository):
    def __init__(self, db: IDbHandler, entity: Any):
        super().__init__(db, entity)

    async def get_by_name(self, name: str) -> Optional[NamedBaseEntity]:
        query = select(self._entity).where(
            self._entity.name == name,
            self._entity.status != StatusEnum.LOGICALLY_DELETED
        )
        result = await self._session.execute(query)
        return result.scalars().first()
