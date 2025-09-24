from dataclasses import dataclass
from typing import Optional
from .field_config import FieldConfig

@dataclass
class JsonFieldConfig(FieldConfig):
    schema: Optional[dict] = None
    
    def __init__(self, schema: Optional[dict] = None, validator = None):
        super().__init__(type=dict, validator=validator)
        self.schema = schema
