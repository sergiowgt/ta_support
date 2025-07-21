from collections import namedtuple
from datetime import datetime
FieldConfig = namedtuple('FieldConfig', 'type minlen maxlen validator')

NAME_FIELD = FieldConfig(str, 5, 100, "DomainValidator.string_required")
UUID_FIELD = FieldConfig(str, 36, 36, "DomainValidator.validate_uuid")
CPF_FIELD = FieldConfig(str, 11, 11, "DomainValidator.validate_cpf")
CNPJ_FIELD = FieldConfig(str, 14, 14, "DomainValidator.validate_cnpj")
CREATED_BY_FIELD = FieldConfig(str, 0, 50, "DomainValidator.string_required")
UPDATED_BY_FIELD = FieldConfig(str, 0, 50, "DomainValidator.string_required")
STATECODE_FIELD = FieldConfig(str, 2, 2, "DomainValidator.validate_state_code")
CREATED_AT_FIELD = FieldConfig(datetime, None, None, "DomainValidator.validate_datetime")
UPDATED_AT_FIELD = FieldConfig(datetime, None, None, "DomainValidator.validate_datetime")
