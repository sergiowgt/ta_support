from dataclasses import dataclass
from datetime import date
from typing import Optional

from .field_config import FieldConfig

@dataclass
class DateFieldConfig(FieldConfig):
    min_value: Optional[str] = ''
    max_value: Optional[str] = ''
    
    def __init__(self, min_value: Optional[str] = None, max_value: Optional[str] = None, validator = None):
        super().__init__(type=date, validator=validator)
        self.min_value = min_value
        self.max_value = max_value