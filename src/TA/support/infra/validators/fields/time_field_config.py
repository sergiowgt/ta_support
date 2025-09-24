from dataclasses import dataclass
from datetime import time
from typing import Optional

from .field_config import FieldConfig

@dataclass
class TimeFieldConfig(FieldConfig):
    min_value: Optional[str] = '' 
    max_value: Optional[str] = ''
    
    def __init__(self, min_value: Optional[str] = None, max_value: Optional[str] = None, validator = None):
        super().__init__(type=time, validator=validator)
        self.min_value = min_value
        self.max_value = max_value