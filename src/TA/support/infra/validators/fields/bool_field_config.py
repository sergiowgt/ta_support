from dataclasses import dataclass
from .field_config import FieldConfig

@dataclass
class BoolFieldConfig(FieldConfig):
    def __init__(self):
        super().__init__(type=bool, validator=None)