from dataclasses import dataclass
from typing import Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from TA.support.infra.database.idb_handler import IDbHandler
from .ibase_repository import IBaseRepository
from ..domain.entities.base_entity import BaseEntity
from ..domain.enums.status_enum import StatusEnum

@dataclass
class BaseRepository(IBaseRepository):
    _session: AsyncSession = NotImplementedError
    _entity: BaseEntity = NotImplementedError

    def __init__(self, session: AsyncSession, entity: BaseEntity):
        self._session = session
        self._entity = entity

    def _make_query(self, id: int, only_active: bool = False) -> Any:
        query = select(self._entity).where(self._entity.id == id)
        if only_active:
            query = query.where(self._entity.status == StatusEnum.ACTIVE)
        else:
            query = query.where(self._entity.status != StatusEnum.LOGICALLY_DELETED)
        return query

    async def exists(self, id: int, only_active: bool = False) -> bool:
        result = await self._session.execute(
            self._make_query(id, only_active)
        )
        return result.scalars().first() is not None

    async def get(self, id: int, only_active: bool = False) -> Optional[BaseEntity]:
        result = await self._session.execute(
            self._make_query(id, only_active)
        )
        return result.scalars().first()

    async def get_all(self, only_active: bool = False, page=1, page_size=20) -> List[BaseEntity]:
        query = select(self._entity)
        if only_active:
            query = query.where(self._entity.status == StatusEnum.ACTIVE)
        else:
            query = query.where(self._entity.status != StatusEnum.LOGICALLY_DELETED)
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(query)
        return result.scalars().all()