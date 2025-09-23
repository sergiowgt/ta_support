from dataclasses import dataclass
from typing import Optional

from .field_config import FieldConfig

@dataclass
class IntFieldConfig(FieldConfig):
    min_value: Optional[int] = None
    max_value: Optional[int] = None