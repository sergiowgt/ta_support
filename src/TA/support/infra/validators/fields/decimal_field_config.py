from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from .field_config import FieldConfig

@dataclass
class DecimalFieldConfig(FieldConfig):
    min_value: Optional[Decimal] = Decimal('0')
    max_value: Optional[Decimal] = Decimal('0')
    
    def __init__(self, min_value: Optional[Decimal] = None, max_value: Optional[Decimal] = None, validator = None):
        super().__init__(type=Decimal, validator=validator)
        self.min_value = min_value
        self.max_value = max_value