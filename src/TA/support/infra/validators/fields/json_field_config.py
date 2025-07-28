from dataclasses import dataclass
from typing import Optional
from .field_config import FieldConfig

@dataclass
class JsonFieldConfig(FieldConfig):
    schema: Optional[dict] = None
