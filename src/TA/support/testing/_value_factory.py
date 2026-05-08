"""Sintetiza valores válidos pra cada FieldConfig type.

Usado pelo codegen pra montar `_minimal_valid()` no arquivo de teste gerado:
um payload onde cada field tem valor que satisfaz seu validator declarado
em metadata.
"""
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from TA.support.infra.validators.fields import (
    BoolFieldConfig,
    DateFieldConfig,
    DateTimeFieldConfig,
    DecimalFieldConfig,
    IntEnumFieldConfig,
    IntFieldConfig,
    JsonFieldConfig,
    StrEnumFieldConfig,
    StrFieldConfig,
    TimeFieldConfig,
)
from TA.support.infra.validators.field_validator import FieldValidator


# Exemplos canônicos por validator. Cada um deve passar no validator real
# (DV calculados pra CNPJ/CPF, regex pra cell_phone/phone, etc).
_VALIDATOR_VALID_EXAMPLES = {
    FieldValidator.validate_cnpj: "11222333000181",  # CNPJ válido (DVs corretos)
    FieldValidator.validate_cpf: "11144477735",  # CPF válido
    FieldValidator.validate_email: "test@example.com",
    FieldValidator.validate_state_code: "SP",
    FieldValidator.validate_cell_phone: "11987654321",
    FieldValidator.validate_phone: "1133334444",
}


def valid_value_for(field_config: Any) -> Any:
    """Retorna valor Python válido pra o field_config dado.

    Cobre todos FieldConfig types da TA.support v1.1.b. Pra StrFieldConfig
    com validator custom, usa exemplo canônico de _VALIDATOR_VALID_EXAMPLES.
    """
    if field_config is None:
        return None

    if isinstance(field_config, StrFieldConfig):
        validator = getattr(field_config, "validator", None)
        if validator and validator in _VALIDATOR_VALID_EXAMPLES:
            return _VALIDATOR_VALID_EXAMPLES[validator]
        if validator == FieldValidator.validate_uuid:
            # UUID fixo determinístico — codegen precisa de output estável entre runs
            return UUID("00000000-0000-0000-0000-000000000001")
        # Sem validator: gera string com tamanho mínimo
        min_len = getattr(field_config, "min_len", 0) or 1
        return "a" * min_len

    if isinstance(field_config, IntFieldConfig):
        validator = getattr(field_config, "validator", None)
        if validator == FieldValidator.validate_status:
            return 1  # ACTIVE
        min_value = getattr(field_config, "min_value", None)
        return min_value if min_value is not None else 0

    if isinstance(field_config, BoolFieldConfig):
        return True  # Bug TA validate_bool rejeita False — usar True por seg.

    if isinstance(field_config, DateFieldConfig):
        return date(2026, 1, 1)

    if isinstance(field_config, DateTimeFieldConfig):
        return datetime(2026, 1, 1, 12, 0, 0)

    if isinstance(field_config, TimeFieldConfig):
        return time(12, 0, 0)

    if isinstance(field_config, DecimalFieldConfig):
        min_value = getattr(field_config, "min_value", None)
        return Decimal(str(min_value)) if min_value is not None else Decimal("1.0")

    if isinstance(field_config, IntEnumFieldConfig):
        enum_cls = field_config.enum_cls
        return list(enum_cls)[0].value

    if isinstance(field_config, StrEnumFieldConfig):
        enum_cls = field_config.enum_cls
        return list(enum_cls)[0].value

    if isinstance(field_config, JsonFieldConfig):
        return {"key": "value"}

    return None  # tipo desconhecido — codegen pode pular


def repr_value(value: Any) -> str:
    """Retorna expressão Python que reproduz o valor em código gerado.

    Output deve ser eval-safe assumindo imports padrão do arquivo gerado:
        from datetime import date, datetime, time
        from decimal import Decimal
        from uuid import UUID, uuid4
    """
    if value is None:
        return "None"
    if isinstance(value, bool):
        return repr(value)
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, int):
        return repr(value)
    if isinstance(value, datetime):
        return f"datetime({value.year}, {value.month}, {value.day}, {value.hour}, {value.minute}, {value.second})"
    if isinstance(value, date):
        return f"date({value.year}, {value.month}, {value.day})"
    if isinstance(value, time):
        return f"time({value.hour}, {value.minute}, {value.second})"
    if isinstance(value, Decimal):
        return f"Decimal('{value}')"
    if isinstance(value, UUID):
        return f"UUID('{value}')"
    if isinstance(value, dict):
        return repr(value)
    return repr(value)
