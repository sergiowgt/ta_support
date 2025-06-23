from dataclasses import dataclass
from typing import Any
from TA.support.infra.database.idb_handler import IDbHandler
from .base_repository import BaseRepository
from ..domain.entities.named_base_entity import NamedBaseEntity
from ..domain.enums.status_enum import StatusEnum

@dataclass
class NamedRepository (BaseRepository):
    def __init__(self, db: IDbHandler, entity: Any):
        super().__init__(db, entity)

    def get_by_name(self, name: str) -> NamedBaseEntity:
        query = self._session.query(self._entity).filter_by(name = name)
        query = query.filter(self._entity.status != StatusEnum.LOGICAMENTE_DELETADO)

        return query.first()