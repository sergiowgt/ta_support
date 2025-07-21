
import uuid
from TA.support.domain.entities.base_config_atributtes import (
    CNPJ_FIELD, NAME_FIELD, UUID_FIELD, CREATED_BY_FIELD, UPDATED_BY_FIELD,
    STATECODE_FIELD, CPF_FIELD
)
from sqlalchemy import VARCHAR, TypeDecorator

class UUIDType(TypeDecorator):
    impl = VARCHAR(UUID_FIELD.maxlen)

    def process_bind_param(self, value, dialect):
            if value is None:
                return value
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value

class NameType(TypeDecorator):
    impl = VARCHAR(NAME_FIELD.maxlen)

class CreatedByType(TypeDecorator):
    impl = VARCHAR(CREATED_BY_FIELD.maxlen)

class UpdatedByType(TypeDecorator):
    impl = VARCHAR(UPDATED_BY_FIELD.maxlen)

class StateCodeType(TypeDecorator):
    impl = VARCHAR(STATECODE_FIELD.maxlen)

class CPFType(TypeDecorator):
    impl = VARCHAR(CPF_FIELD.maxlen)

class CNPJType(TypeDecorator):
    impl = VARCHAR(CNPJ_FIELD.maxlen)

