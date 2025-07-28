from dataclasses import dataclass
from typing import Optional

from .field_config import FieldConfig

@dataclass
class DateFieldConfig(FieldConfig):
    min_value: Optional[str] = None  # 'YYYY-MM-DD'
    max_value: Optional[str] = None