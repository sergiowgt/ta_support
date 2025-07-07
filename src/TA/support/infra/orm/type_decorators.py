
import uuid
from TA.support.domain.entities.base_config_atributtes import (
    CNPJ_FIELD, NAME_FIELD, UUID_FIELD, CREATE_BY_FIELD, UPDATE_BY_FIELD,
    STATECODE_FIELD, CPF_FIELD
)
from sqlalchemy import VARCHAR, TypeDecorator

class UUIDType(TypeDecorator):
    impl = VARCHAR(UUID_FIELD.exact)

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
    impl = VARCHAR(NAME_FIELD.max)

class CreatedByType(TypeDecorator):
    impl = VARCHAR(CREATE_BY_FIELD.max)

class UpdatedByType(TypeDecorator):
    impl = VARCHAR(UPDATE_BY_FIELD.max)

class StateCodeType(TypeDecorator):
    impl = VARCHAR(STATECODE_FIELD.exact)

class CPFType(TypeDecorator):
    impl = VARCHAR(CPF_FIELD.exact)

class CNPJType(TypeDecorator):
    impl = VARCHAR(CNPJ_FIELD.exact)

