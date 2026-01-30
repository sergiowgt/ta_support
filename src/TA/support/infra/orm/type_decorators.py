import uuid
from sqlalchemy import VARCHAR
from sqlalchemy.types import TypeDecorator

class UUIDType(TypeDecorator):
    impl = VARCHAR(36)
    
    cache_ok = True
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