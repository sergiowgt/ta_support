from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from .field_config import FieldConfig

@dataclass
class IntFieldConfig(FieldConfig):
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None