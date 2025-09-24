from dataclasses import dataclass
from typing import Optional

from .field_config import FieldConfig

@dataclass
class IntFieldConfig(FieldConfig):
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    
    def __init__(self, min_value: Optional[int] = None, max_value: Optional[int] = None, validator = None):
        super().__init__(type=int, validator=validator)
        self.min_value = min_value
        self.max_value = max_value