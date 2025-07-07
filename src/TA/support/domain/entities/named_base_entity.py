from dataclasses import dataclass, field
from TA.support.domain.entities.base_entity import BaseEntity
from TA.support.domain.entities.base_config_atributtes import NAME_FIELD

@dataclass
class NamedBaseEntity(BaseEntity):
    name: str = field(default='', metadata={'display': 'Name', 'max_length': NAME_FIELD.max, 'unique': True})

    def validate(self):
        super().validate()
        self.validate_string_empty_and_len('name')
