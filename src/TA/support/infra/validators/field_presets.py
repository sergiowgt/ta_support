from datetime import datetime
from TA.support.infra.validators.field_validator import FieldValidator
from TA.support.infra.validators.fields import StrFieldConfig, DateFieldConfig, IntFieldConfig

UUID_FIELD = StrFieldConfig(str, min_len=36, max_len=36, validator=FieldValidator.validate_uuid)
CPF_FIELD = StrFieldConfig(str, min_len=11, max_len=11, validator=FieldValidator.validate_cpf)
CNPJ_FIELD = StrFieldConfig(str, min_len=14, max_len=14, validator=FieldValidator.validate_cnpj)
STATECODE_FIELD = StrFieldConfig(str, max_len=2, min_len=2, validator=FieldValidator.validate_state_code)
CELLPHONE_FIELD = StrFieldConfig(str, min_len=11, max_len=11, validator=FieldValidator.validate_cell_phone)
EMAIL_FIELD = StrFieldConfig(str, min_len=0, max_len=255, validator=FieldValidator.validate_email)
STATUS_FIELD = IntFieldConfig(str, validator=FieldValidator.validate_status)
NAME_FIELD = StrFieldConfig(str, max_len=100)
DATED_BY_FIELD = StrFieldConfig(str, max_len=50)
DATED_AT_FIELD = DateFieldConfig(datetime)