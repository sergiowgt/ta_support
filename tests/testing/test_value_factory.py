"""Meta-tests do _value_factory."""
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

import pytest

from TA.support.infra.validators.field_presets import (
    CELL_PHONE_FIELD,
    CNPJ_FIELD,
    CPF_FIELD,
    DATED_AT_FIELD,
    EMAIL_FIELD,
    NAME_FIELD,
    PHONE_FIELD,
    STATECODE_FIELD,
    UUID_FIELD,
)
from TA.support.infra.validators.fields import (
    BoolFieldConfig,
    DateFieldConfig,
    DateTimeFieldConfig,
    DecimalFieldConfig,
    IntFieldConfig,
    StrFieldConfig,
    TimeFieldConfig,
)
from TA.support.infra.validators.field_validator import FieldValidator
from TA.support.testing._value_factory import repr_value, valid_value_for


def test_str_field_without_validator_returns_string_with_min_len():
    cfg = StrFieldConfig(min_len=5, max_len=100)
    value = valid_value_for(cfg)
    assert isinstance(value, str)
    assert len(value) == 5


def test_str_field_with_no_min_len_returns_single_char():
    cfg = StrFieldConfig(max_len=50)
    value = valid_value_for(cfg)
    assert isinstance(value, str)
    assert len(value) >= 1


def test_cnpj_field_returns_known_valid_cnpj():
    value = valid_value_for(CNPJ_FIELD)
    assert value == "11222333000181"
    # E o validator real aceita esse valor
    FieldValidator.validate_cnpj(value, "cnpj", CNPJ_FIELD)


def test_cpf_field_returns_known_valid_cpf():
    value = valid_value_for(CPF_FIELD)
    assert value == "11144477735"
    FieldValidator.validate_cpf(value, "cpf", CPF_FIELD)


def test_email_field_returns_valid_email():
    value = valid_value_for(EMAIL_FIELD)
    assert value == "test@example.com"
    FieldValidator.validate_email(value, "email", EMAIL_FIELD)


def test_state_code_field_returns_valid_state():
    value = valid_value_for(STATECODE_FIELD)
    assert value == "SP"
    FieldValidator.validate_state_code(value, "uf", STATECODE_FIELD)


def test_cell_phone_field_returns_valid_cell_phone():
    value = valid_value_for(CELL_PHONE_FIELD)
    FieldValidator.validate_cell_phone(value, "phone", CELL_PHONE_FIELD)


def test_phone_field_returns_valid_phone():
    value = valid_value_for(PHONE_FIELD)
    FieldValidator.validate_phone(value, "phone", PHONE_FIELD)


def test_uuid_field_returns_uuid_object():
    value = valid_value_for(UUID_FIELD)
    assert isinstance(value, UUID)
    FieldValidator.validate_uuid(value, "id", UUID_FIELD)


def test_int_field_with_min_returns_min():
    cfg = IntFieldConfig(min_value=5, max_value=100)
    assert valid_value_for(cfg) == 5


def test_int_field_without_min_returns_zero():
    cfg = IntFieldConfig(max_value=100)
    assert valid_value_for(cfg) == 0


def test_bool_field_returns_true():
    """Workaround bug TA validate_bool — usa True pra evitar 'empty' falso."""
    cfg = BoolFieldConfig()
    assert valid_value_for(cfg) is True


def test_date_field_returns_date():
    cfg = DateFieldConfig()
    value = valid_value_for(cfg)
    assert isinstance(value, date)


def test_datetime_field_returns_datetime():
    cfg = DateTimeFieldConfig()
    value = valid_value_for(cfg)
    assert isinstance(value, datetime)


def test_time_field_returns_time():
    cfg = TimeFieldConfig()
    value = valid_value_for(cfg)
    assert isinstance(value, time)


def test_decimal_field_returns_decimal():
    cfg = DecimalFieldConfig()
    value = valid_value_for(cfg)
    assert isinstance(value, Decimal)


def test_dated_at_field_returns_date():
    """DATED_AT_FIELD = DateFieldConfig() — verifica caminho de presets."""
    value = valid_value_for(DATED_AT_FIELD)
    assert isinstance(value, date)


def test_repr_value_string():
    assert repr_value("hello") == "'hello'"


def test_repr_value_bool():
    assert repr_value(True) == "True"


def test_repr_value_none():
    assert repr_value(None) == "None"


def test_repr_value_uuid():
    from uuid import uuid4

    u = uuid4()
    output = repr_value(u)
    assert output.startswith("UUID('")
    assert str(u) in output


def test_repr_value_date():
    output = repr_value(date(2026, 5, 4))
    assert output == "date(2026, 5, 4)"


def test_repr_value_decimal():
    output = repr_value(Decimal("1.5"))
    assert output == "Decimal('1.5')"
