from dataclasses import dataclass, field, fields
from datetime import datetime
from uuid import uuid4

from TA.support.infra.validators.field_validator import FieldValidator
from TA.support.infra.validators.fields.date_field_config import DateFieldConfig
from TA.support.infra.validators.fields.decimal_field_config import DecimalFieldConfig
from TA.support.infra.validators.fields.int_field_config import IntFieldConfig
from TA.support.infra.validators.fields.json_field_config import JsonFieldConfig
from TA.support.infra.validators.fields.str_field_config import StrFieldConfig
from TA.support.domain.enums.status_enum import StatusEnum
from TA.support.infra.validators.field_presets import DATED_BY_FIELD, DATED_AT_FIELD, STATUS_FIELD, UUID_FIELD

@dataclass
class BaseEntity:
    id: str = field(default_factory=uuid4, 
               metadata={
                   'field_config': UUID_FIELD, 
                   'display': 'UUID'}
            )
    status: StatusEnum = field(default=StatusEnum.ACTIVE, 
                               metadata={'field_config': STATUS_FIELD,
                                         'display': 'Status', 
                                         'required': True}
                               )
    created_at: datetime = field(default_factory=datetime.now, 
                                 metadata={'field_config': DATED_AT_FIELD,
                                           'display': 'CreatedAt', 
                                           'required': True}
                                           )
    created_by: str = field(default='', 
                            metadata={'field_config': DATED_BY_FIELD,
                                      'display': 'CreatedBy', 
                                      'required': True}
                            )
    updated_at: datetime = field(default=None, 
                                 metadata={'field_config': DATED_AT_FIELD,
                                           'display': 'UpdatedAt'}
                            )
    updated_by: str = field(default=None, 
                            metadata={'field_config': DATED_BY_FIELD,
                                      'display': 'UpdatedBy'})

    def _get_display_name(self, property_name: str) -> str:
        for f in fields(self):
            if f.name == property_name:
                return f.metadata.get('display', property_name)
        return property_name
    
    def _get_metadata_info(self, metadata, field_name):
        display_name = metadata.get("display", field_name)
        required = metadata.get("required", False)
        value = getattr(self, field_name)

        return display_name, required, value

    def call_default_validators(self, field_config, display_name, value):
        #print(f"{display_name} => {type(field_config)}, {type(value)} {value}")
        if isinstance(field_config, StrFieldConfig):
            FieldValidator.validate_string(value, display_name, field_config)
        elif isinstance(field_config, IntFieldConfig):
            FieldValidator.validate_integer(value, display_name, field_config)
        elif isinstance(field_config, DecimalFieldConfig):
            FieldValidator.validate_decimal(value, display_name, field_config)
        elif isinstance(field_config, DateFieldConfig):
            FieldValidator.validate_datetime(value, display_name, field_config)
        elif isinstance(field_config, JsonFieldConfig):
            FieldValidator.validate_json(value, display_name, field_config)

    def validate(self) -> bool:
        for f in fields(self):
            display_name, required, value = self._get_metadata_info(f.metadata, f.name)
            if not required and not value:
                continue

            field_config = f.metadata.get("field_config")
            validator_fn = getattr(field_config, "validator", None) if field_config else None
            if callable(validator_fn):
                validator_fn(value, display_name, field_config)
                continue
 
            if required:
                self.call_default_validators(field_config, display_name, value)
              
        if self.updated_at:
            FieldValidator.validate_datetime(self.updated_at, self._get_display_name('updated_at'), DATED_AT_FIELD)
            FieldValidator.validate_string(self.updated_by, self._get_display_name('updated_by'), DATED_BY_FIELD)

        if self.updated_by:
            FieldValidator.validate_string(self.updated_by, self._get_display_name('updated_by'), DATED_BY_FIELD)
            FieldValidator.validate_datetime(self.updated_at, self._get_display_name('updated_at'), DATED_AT_FIELD)
        
        return True


"""     def validate(self):
        self.validate_string_empty_and_len('created_by')
        self.validate_datetime('created_at')
        
        if self.updated_at:
            self.validate_datetime('updated_at')
            self.validate_string_empty_and_len('updated_by')

        if self.updated_by:
            self.validate_string_empty_and_len('updated_by')
            self.validate_datetime('updated_at')
 """