from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Optional
from uuid import uuid4

from TA.support.validators_exceptions import DomainValidator  
from TA.support.domain.enums.status_enum import StatusEnum
from TA.support.validators_exceptions.domain_exception import DomainException
from TA.support.i18n.message_provider import MessageProvider
from TA.support.domain.entities.base_config_atributtes import CREATED_BY_FIELD, CREATED_AT_FIELD, UPDATED_BY_FIELD, UPDATED_AT_FIELD, UUID_FIELD

@dataclass
class BaseEntity:
    id: str = field(default_factory=uuid4, 
               metadata={
                   'field_config': UUID_FIELD, 
                   'display': 'UUID'}
            )
    status: StatusEnum = field(default=StatusEnum.ACTIVE, 
                               metadata={'display': 'Status', 
                                         'required': True}
                               )
    created_at: datetime = field(default_factory=datetime.now, 
                                 metadata={'field_config': CREATED_AT_FIELD,
                                           'display': 'CreatedAt', 
                                           'required': True}
                                           )
    created_by: str = field(default='', 
                            metadata={'field_config': CREATED_BY_FIELD,
                                      'display': 'CreatedBy', 
                                      'required': True}
                            )
    updated_at: datetime = field(default=None, 
                                 metadata={'field_config': UPDATED_AT_FIELD,
                                           'display': 'UpdatedAt'}
                            )
    updated_by: str = field(default=None, 
                            metadata={'field_config': UPDATED_BY_FIELD,
                                      'display': 'UpdatedBy'})

    def _get_display_name(self, property_name: str) -> str:
        for f in fields(self):
            if f.name == property_name:
                return f.metadata.get('display', property_name)
        return property_name

    def validate_datetime(self, property_name: str, allow_future: bool = False, custom_message_key: Optional[str] = None):
        value = getattr(self, property_name)
        display_name = self._get_display_name(property_name)

        if not value:
            raise DomainException(
                MessageProvider.get_message("validation.error.empty_field", {"field": display_name})
        )
        
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

    def validate(self) -> bool:
        for f in fields(self):
            metadata = f.metadata
            display_name = metadata.get("display", f.name)
            obrigatorio = metadata.get("required", False)
            valor = getattr(self, f.name)

            # Ignora campo não obrigatório e vazio
            if not obrigatorio and not valor:
                continue

            # Busca configuração do campo e o nome do validador
            field_config = metadata.get("field_config")
            if not field_config:
                continue

            
            validator_path = getattr(field_config, "validator", None) if field_config else None
            if validator_path and validator_path.startswith("DomainValidator."):
                # Divide em classe e método
                _, method_name = validator_path.split(".", 1)
                # Recupera o método estaticamente (ajuste o import conforme sua estrutura real)
                # ajuste o caminho se necessário
                validator_obj = getattr(DomainValidator, method_name, None)

                if callable(validator_obj):
                    validator_obj(valor, display_name, field_config)
                else:
                    # Se desejado, logue ou lance erro de configuração aqui
                    pass

        if self.updated_at:
            self.validate_datetime('updated_at')
            DomainValidator.string_required(self.updated_by, self._get_display_name('updated_by'), UPDATED_BY_FIELD)

        if self.updated_by:
            DomainValidator.string_required(self.updated_by, self._get_display_name('updated_by'), UPDATED_BY_FIELD)
            self.validate_datetime('updated_at')
        
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