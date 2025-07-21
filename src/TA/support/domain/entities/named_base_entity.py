from dataclasses import dataclass, field
from TA.support.domain.entities.base_entity import BaseEntity
from TA.support.domain.entities.base_config_atributtes import NAME_FIELD

@dataclass
class NamedBaseEntity(BaseEntity):
    name: str = field(default='', 
                      metadata={'required': True, 'display': 'Name', 'field_config': NAME_FIELD, 'unique': True})
