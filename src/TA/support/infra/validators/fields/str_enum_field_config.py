from dataclasses import dataclass
from enum import Enum
from typing import Type

from TA.support.infra.validators.fields.field_config import FieldConfig

@dataclass
class StrEnumFieldConfig(FieldConfig):
    enum_cls: Type[Enum] = None

    def __init__(self, enum_cls: Type[Enum], max_len: int, validator=None):
        super().__init__(type=enum_cls, validator=validator)
        self.enum_cls = enum_cls
        self.max_len = max_len 