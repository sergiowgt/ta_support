from dataclasses import dataclass
from typing import Optional
from .field_config import FieldConfig

@dataclass
class StrFieldConfig(FieldConfig):
    min_len: Optional[int] = 0
    max_len: Optional[int] = 0
    
    def __init__(self, min_len: Optional[int] = None, max_len: Optional[int] = None, validator = None):
        super().__init__(type=str, validator=validator)
        self.min_len = min_len
        self.max_len = max_len