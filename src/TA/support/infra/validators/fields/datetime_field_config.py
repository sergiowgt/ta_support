from dataclasses import dataclass
from typing import Optional

from .field_config import FieldConfig

@dataclass
class DateTimeFieldConfig(FieldConfig):
    min_value: Optional[str] = None  # Ex: '2020-01-01T00:00:00'
    max_value: Optional[str] = None