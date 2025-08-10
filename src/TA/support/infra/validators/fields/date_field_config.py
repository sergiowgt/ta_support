from dataclasses import dataclass
from typing import Optional

from .field_config import FieldConfig

@dataclass
class DateFieldConfig(FieldConfig):
    min_value: Optional[str] = ''
    max_value: Optional[str] = ''