from dataclasses import dataclass
from typing import Optional

from .field_config import FieldConfig

@dataclass
class IntFieldConfig(FieldConfig):
    min_value: Optional[int] = 0
    max_value: Optional[int] = 0