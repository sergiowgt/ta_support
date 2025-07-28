from dataclasses import dataclass
from typing import Optional, Callable

@dataclass
class FieldConfig:
    type: type
    validator: Optional[Callable] = None
