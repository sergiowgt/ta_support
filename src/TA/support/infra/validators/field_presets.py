from TA.support.infra.validators.field_validator import FieldValidator
from TA.support.infra.validators.fields import StrFieldConfig, DateFieldConfig, IntFieldConfig


# StrEnum — max_len explícito, independente dos valores do enum
#SPECIALTY_TYPE_FIELD = EnumFieldConfig(enum_cls=SpecialtyTypeEnum, max_len=30)
#GENDER_FIELD = EnumFieldConfig(enum_cls=GenderEnum)

UUID_FIELD = StrFieldConfig(min_len=36, max_len=36, validator=FieldValidator.validate_uuid)
CPF_FIELD = StrFieldConfig(min_len=11, max_len=11, validator=FieldValidator.validate_cpf)
CNPJ_FIELD = StrFieldConfig(min_len=14, max_len=14, validator=FieldValidator.validate_cnpj)
STATECODE_FIELD = StrFieldConfig(max_len=2, min_len=2, validator=FieldValidator.validate_state_code)
CELL_PHONE_FIELD = StrFieldConfig(min_len=11, max_len=11, validator=FieldValidator.validate_cell_phone)
PHONE_FIELD = StrFieldConfig(min_len=10, max_len=10, validator=FieldValidator.validate_phone)
EMAIL_FIELD = StrFieldConfig(min_len=0, max_len=255, validator=FieldValidator.validate_email)
STATUS_FIELD = IntFieldConfig(validator=FieldValidator.validate_status)
NAME_FIELD = StrFieldConfig(max_len=100)
DATED_BY_FIELD = StrFieldConfig(max_len=50)
DATED_AT_FIELD = DateFieldConfig() 