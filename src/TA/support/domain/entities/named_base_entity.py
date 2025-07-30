from dataclasses import dataclass, field
from TA.support.domain.entities.base_entity import BaseEntity
from TA.support.domain.enums.unique_type_enum import UniqueTypeEnum
from TA.support.infra.validators.field_presets import NAME_FIELD

@dataclass
class NamedBaseEntity(BaseEntity):
    name: str = field(default='', 
        metadata={'field_config': NAME_FIELD, 
                  'required': True, 
                  'display': 'Name', 
                  'unique': UniqueTypeEnum.FIELD_ONLY})
