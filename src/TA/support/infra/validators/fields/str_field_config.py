from dataclasses import dataclass
from typing import Optional
from .field_config import FieldConfig

@dataclass
class StrFieldConfig(FieldConfig):
    min_len: Optional[int] = None
    max_len: Optional[int] = None