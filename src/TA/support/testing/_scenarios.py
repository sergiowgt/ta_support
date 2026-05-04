"""Gera lista de cenários de teste por field, a partir de metadata.

Cada cenário vira 1 função `def test_<field>_<suffix>():` no arquivo gerado.
Cobre apenas o que está declarado em `field_config` — invariantes cross-campo
(via entity `validate()` override) ficam fora; dev adiciona manualmente no
bloco CUSTOM do arquivo gerado.
"""
from typing import Any, List, Tuple

from TA.support.infra.validators.fields import (
    BoolFieldConfig,
    DecimalFieldConfig,
    IntEnumFieldConfig,
    IntFieldConfig,
    StrEnumFieldConfig,
    StrFieldConfig,
)
from TA.support.infra.validators.field_validator import FieldValidator


# (suffix, value_expression_str)
Scenario = Tuple[str, str]


def generate_field_scenarios(field_obj) -> List[Scenario]:
    """Pra um field, retorna cenários de teste a gerar.

    Cada item é (suffix, value_expr) onde:
    - suffix: parte do nome da função, ex 'required_none_raises'
    - value_expr: expressão Python que substitui o valor do field no payload

    O valor produzido por value_expr é injetado em `_minimal_valid()` e a
    chamada `Entity(**payload).validate()` deve disparar
    `FieldValidatorException`.
    """
    metadata = field_obj.metadata
    cfg = metadata.get("field_config")
    required = metadata.get("required", False)
    scenarios: List[Scenario] = []

    if cfg is None:
        return scenarios

    # Required + None
    # BaseEntity.validate() pula `not required and not value` — então só
    # geramos required_none pra fields required.
    if required and not isinstance(cfg, BoolFieldConfig):
        # Bool com required=True é bug conhecido (validate_bool rejeita False)
        scenarios.append(("required_none_raises", "None"))

    # StrFieldConfig
    if isinstance(cfg, StrFieldConfig):
        if required:
            scenarios.append(("required_empty_string_raises", "''"))

        min_len = getattr(cfg, "min_len", 0) or 0
        max_len = getattr(cfg, "max_len", 0) or 0

        if min_len and (max_len == 0 or min_len < max_len):
            scenarios.append(
                (f"min_{min_len}_chars_violated_raises", f'"a" * {min_len - 1}')
            )
        if max_len:
            scenarios.append(
                (f"max_{max_len}_chars_exceeded_raises", f'"a" * {max_len + 1}')
            )

        validator = getattr(cfg, "validator", None)
        if validator == FieldValidator.validate_cnpj:
            scenarios.append(("cnpj_invalid_digits_raises", "'00000000000000'"))
            scenarios.append(("cnpj_non_digit_chars_raises", "'aa222333000181'"))
        elif validator == FieldValidator.validate_cpf:
            scenarios.append(("cpf_invalid_digits_raises", "'00000000000'"))
        elif validator == FieldValidator.validate_email:
            scenarios.append(("email_no_at_sign_raises", "'invalid_email'"))
        elif validator == FieldValidator.validate_state_code:
            scenarios.append(("state_code_invalid_raises", "'XX'"))
        elif validator == FieldValidator.validate_cell_phone:
            scenarios.append(("cellphone_invalid_format_raises", "'12345'"))
        elif validator == FieldValidator.validate_phone:
            scenarios.append(("phone_invalid_format_raises", "'12345'"))
        elif validator == FieldValidator.validate_uuid:
            # validate_uuid checa isinstance(UUID); string crua deve falhar
            scenarios.append(("uuid_invalid_type_raises", "'not-a-uuid-string'"))

    # IntFieldConfig
    elif isinstance(cfg, IntFieldConfig):
        min_value = getattr(cfg, "min_value", None)
        max_value = getattr(cfg, "max_value", None)
        if min_value is not None:
            scenarios.append(
                (f"below_min_{min_value}_raises", str(min_value - 1))
            )
        if max_value is not None:
            scenarios.append(
                (f"above_max_{max_value}_raises", str(max_value + 1))
            )

    # DecimalFieldConfig
    elif isinstance(cfg, DecimalFieldConfig):
        min_value = getattr(cfg, "min_value", None)
        max_value = getattr(cfg, "max_value", None)
        if min_value is not None:
            scenarios.append(
                (
                    f"below_min_{min_value}_raises",
                    f"Decimal('{min_value - 1}')",
                )
            )
        if max_value is not None:
            scenarios.append(
                (
                    f"above_max_{max_value}_raises",
                    f"Decimal('{max_value + 1}')",
                )
            )

    # IntEnumFieldConfig / StrEnumFieldConfig: valor fora do enum
    elif isinstance(cfg, (IntEnumFieldConfig, StrEnumFieldConfig)):
        if isinstance(cfg, IntEnumFieldConfig):
            scenarios.append(("enum_invalid_value_raises", "9999"))
        else:
            scenarios.append(("enum_invalid_value_raises", "'__not_in_enum__'"))

    # BoolFieldConfig: skip cenários de falha (bug validate_bool com required)
    # DateFieldConfig/DateTimeFieldConfig/TimeFieldConfig: required+None acima
    # já cobre. Casos de tipo errado ficam pra cenários custom.

    return scenarios


# Fields herdados de BaseEntity que NÃO devemos manipular no payload
# (são gerenciados pelo CRUDRepository.add() — id, status, timestamps).
# Exceção: created_by é setado manualmente pra que validate() passe (é required).
BASE_ENTITY_MANAGED_FIELDS = {
    "id",
    "status",
    "created_at",
    "updated_at",
    "updated_by",
}
