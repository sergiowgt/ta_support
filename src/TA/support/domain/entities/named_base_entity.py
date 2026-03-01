# TA/support/domain/entities/named_base_entity.py

from sqlalchemy import VARCHAR
from sqlalchemy.orm import mapped_column, Mapped

from TA.support.domain.entities.base_entity import BaseEntity
from TA.support.domain.enums.unique_type_enum import UniqueTypeEnum
from TA.support.infra.validators.field_presets import NAME_FIELD


class NamedBaseEntity(BaseEntity, init=False):
    """
    Base para entidades que possuem o campo 'name'.
    Equivale ao NamedBaseEntity original, agora com mapped_column.
    """
    __abstract__ = True

    name: Mapped[str] = mapped_column(
        VARCHAR(NAME_FIELD.max_len), nullable=False,  # NAME_FIELD.max_len = 100
        metadata={
            'field_config': NAME_FIELD,
            'required': True,
            'display': 'Name',
            'unique_type': UniqueTypeEnum.FIELD_ONLY,
        }
    )