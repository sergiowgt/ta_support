from typing import Any
from .domain_validator import DomainException

class EnumValidator:
    @staticmethod
    def validate(value: int, field_name: str, enum_class: Any):
        DomainException.when(value not in list(enum_class), f"{field_name} must be in {enum_class}. [value={value}]")