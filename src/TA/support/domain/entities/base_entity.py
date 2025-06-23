from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Callable, Optional
from uuid import UUID, uuid4

from TA.support.domain.enums.status_enum import StatusEnum
from TA.support.validators_exceptions.domain_exception import DomainException
from TA.support.i18n.message_provider import MessageProvider
from TA.support.domain.entities.base_config_atributtes import NAME_FIELD  # Nova importação

@dataclass
class BaseEntity:
    id: UUID = field(default_factory=uuid4, metadata={'display': 'UUID'})
    status: StatusEnum = field(default=StatusEnum.ACTIVE, metadata={'display': 'Status'})
    created_at: datetime = field(default_factory=datetime.now, metadata={'display': 'CreatedAt'})
    created_by: str = field(default='', metadata={'display': 'CreatedBy', 'max_length': NAME_FIELD.max})
    updated_at: Optional[datetime] = field(default=None, metadata={'display': 'UpdatedAt'})
    updated_by: Optional[str] = field(default=None, metadata={'display': 'UpdatedBy', 'max_length': NAME_FIELD.max})

    def _get_display_name(self, property_name: str) -> str:
        for f in fields(self):
            if f.name == property_name:
                return f.metadata.get('display', property_name)
        return property_name

    def _get_max_length(self, property_name: str) -> Optional[int]:
        for f in fields(self):
            if f.name == property_name:
                return f.metadata.get('max_length')
        return None

    def get_length(self, property_name: str) -> Optional[int]:
        for f in fields(self):
            if f.name == property_name:
                return f.metadata.get('length')
        return None
    
    def validate_datetime(self, property_name: str, allow_future: bool = False, custom_message_key: Optional[str] = None):
        value = getattr(self, property_name)
        display_name = self._get_display_name(property_name)
        
        if not isinstance(value, datetime):
            msg_key = custom_message_key or "validation.error.invalid_datetime"
            raise DomainException(
                MessageProvider.get_message(msg_key, {"field": display_name})
            )
        
        if not allow_future and value > datetime.now():
            msg_key = custom_message_key or "validation.error.future_date"
            raise DomainException(
                MessageProvider.get_message(msg_key, {"field": display_name})
            )

    def validate_string_empty_and_len(self, property_name: str, additional_validator: Optional[Callable[[str], bool]] = None):
        value = getattr(self, property_name)
        display_name = self._get_display_name(property_name)
        exact_length = self.get_length(property_name)

        if not value or not value.strip():
            raise DomainException(
                MessageProvider.get_message("validation.error.empty_field", {"field": display_name})
            )

        if exact_length and len(value) != exact_length:
            raise DomainException(MessageProvider.get_message("validation.error.exact_length", {"field": display_name, "exact": exact_length}))
        else:
            max_length = self._get_max_length(property_name)            
            if max_length is not None and len(value) > max_length:
                raise DomainException(
                    MessageProvider.get_message("validation.error.max_length", {"field": display_name, "max": max_length}))
        
        if additional_validator and not additional_validator(value):
            raise DomainException(
                MessageProvider.get_message("validation.error.invalid_value", {
                    "field": display_name,
                    "value": value
                })
            )

    def validate(self):
        self.validate_string_empty_and_len('created_by')
        self.validate_datetime('created_at')
        
        if self.updated_at:
            self.validate_datetime('updated_at')
            self.validate_string_empty_and_len('updated_by')

        if self.updated_by:
            self.validate_string_empty_and_len('updated_by')
            self.validate_datetime('updated_at')
