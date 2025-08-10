from dataclasses import dataclass
from typing import Optional
from .field_config import FieldConfig

@dataclass
class StrFieldConfig(FieldConfig):
    min_len: Optional[int] = 0
    max_len: Optional[int] = 0