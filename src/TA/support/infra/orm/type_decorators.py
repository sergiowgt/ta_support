
import uuid
from TA.support.infra.validators.field_presets import (
    CNPJ_FIELD, NAME_FIELD, UUID_FIELD, DATED_BY_FIELD, DATED_BY_FIELD,
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
    impl = VARCHAR(NAME_FIELD.max_len)

class CreatedByType(TypeDecorator):
    impl = VARCHAR(DATED_BY_FIELD.max_len)

class UpdatedByType(TypeDecorator):
    impl = VARCHAR(DATED_BY_FIELD.max_len)

class StateCodeType(TypeDecorator):
    impl = VARCHAR(STATECODE_FIELD.max_len)

class CPFType(TypeDecorator):
    impl = VARCHAR(CPF_FIELD.max_len)

class CNPJType(TypeDecorator):
    impl = VARCHAR(CNPJ_FIELD.max_len)

