"""Codegen de Camada 0 (Testes de Invariância) — DL-012.

Gera arquivo `.py` com testes pytest a partir dos metadados declarados em
fields da entity. Cobre 100% dos cenários derivados de `field_config`:
required, min/max len, min/max value, validators custom (cnpj/cpf/email/etc).

Uso programático:
    from TA.support.testing import generate_invariants_file
    content: str = generate_invariants_file(MyEntityClass)

Uso CLI:
    python -m TA.support.testing.codegen src.domain.entities.tenant:Tenant \\
        > tests/unit/domain/test_tenant_invariants.py

O arquivo gerado tem 2 blocos delimitados por marcadores:
    # === AUTO-GENERATED START ===  (cobertura derivada de metadata)
    # === AUTO-GENERATED END ===
    # === CUSTOM START ===          (invariantes cross-campo manuais)
    # === CUSTOM END ===

Regenerate (futuro): comparará só o bloco AUTO-GENERATED, preservando CUSTOM.
"""
import re
import sys
from dataclasses import fields
from importlib import import_module
from typing import Type

from TA.support.testing._scenarios import (
    BASE_ENTITY_MANAGED_FIELDS,
    generate_field_scenarios,
)
from TA.support.testing._value_factory import repr_value, valid_value_for


CODEGEN_VERSION = "1.2.0"


_HEADER = '''"""Camada 0 — Testes de Invariância pra {entity_name}.

GERADO POR TA.support.testing.codegen v{codegen_version}.
NÃO EDITAR o bloco AUTO-GENERATED diretamente — regere com:
    python -m TA.support.testing.codegen {entity_module}:{entity_name}

Customizações (invariantes cross-campo via validate() override) vão
no bloco CUSTOM no final do arquivo — preservadas em regenerações.
"""
import pytest
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID, uuid4

from {entity_module} import {entity_name}
from TA.support.exceptions import FieldValidatorException


# === AUTO-GENERATED START — TA.support.testing.codegen v{codegen_version} ===

def _minimal_valid() -> dict:
    """Payload com valores válidos pra todos campos required + created_by."""
    return {{
{minimal_kwargs}
    }}


def test_happy_path_valid_{entity_snake}_passes():
    {entity_name}(**_minimal_valid()).validate()
'''


_FAILING_CASE = '''

def test_{field_name}_{suffix}():
    payload = _minimal_valid()
    payload[{field_name_repr}] = {value_expr}
    with pytest.raises(FieldValidatorException):
        {entity_name}(**payload).validate()'''


_FOOTER = '''


# === AUTO-GENERATED END ===


# === CUSTOM START — invariantes cross-campo (validate() override) ===
#
# Adicione aqui testes que codegen não captura porque dependem de regras
# cross-field expressas no override de {entity_name}.validate(). Exemplos:
#
# def test_{entity_snake}_<regra_de_negocio>_raises():
#     payload = _minimal_valid()
#     payload['campo_a'] = 'valor1'
#     payload['campo_b'] = 'valor2'  # combinação que viola invariante
#     with pytest.raises(FieldValidatorException):
#         {entity_name}(**payload).validate()
#
# === CUSTOM END ===
'''


def _camel_to_snake(name: str) -> str:
    """`TenantConfig` -> `tenant_config`. Strip leading underscores."""
    name = name.lstrip("_")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _build_minimal_kwargs(entity_cls: Type) -> str:
    """Constroi o conteúdo do dict `_minimal_valid()` em forma de string.

    Inclui apenas fields required + `created_by` (de BaseEntity, é required).
    Outros fields herdados de BaseEntity (id, status, timestamps) são
    geridos pelo CRUDRepository — pra teste de invariância de entity, não
    precisamos setar; defaults da BaseEntity já cobrem.
    """
    lines = []
    for f in fields(entity_cls):
        if f.name in BASE_ENTITY_MANAGED_FIELDS:
            continue
        if f.name == "created_by":
            lines.append("        'created_by': 'codegen'")
            continue
        cfg = f.metadata.get("field_config")
        required = f.metadata.get("required", False)
        if not required:
            # Optional — default da entity (geralmente None) já satisfaz
            continue
        if cfg is None:
            continue
        value = valid_value_for(cfg)
        if value is None:
            continue
        lines.append(f"        '{f.name}': {repr_value(value)}")
    return ",\n".join(lines)


def generate_invariants_file(entity_cls: Type) -> str:
    """Retorna conteúdo string do arquivo de teste invariância pra entity_cls."""
    entity_name = entity_cls.__name__
    entity_module = entity_cls.__module__
    entity_snake = _camel_to_snake(entity_name)

    parts = [
        _HEADER.format(
            entity_name=entity_name,
            entity_module=entity_module,
            entity_snake=entity_snake,
            codegen_version=CODEGEN_VERSION,
            minimal_kwargs=_build_minimal_kwargs(entity_cls),
        )
    ]

    # Cenários de falha por field
    for f in fields(entity_cls):
        if f.name in BASE_ENTITY_MANAGED_FIELDS:
            continue
        if f.name == "created_by":
            # Required mas valor controlado pelo repo. Cobrir só required_none.
            scenarios = [("required_none_raises", "None")]
        else:
            scenarios = generate_field_scenarios(f)

        for suffix, value_expr in scenarios:
            parts.append(
                _FAILING_CASE.format(
                    field_name=f.name,
                    suffix=suffix,
                    field_name_repr=repr(f.name),
                    value_expr=value_expr,
                    entity_name=entity_name,
                )
            )

    parts.append(
        _FOOTER.format(entity_name=entity_name, entity_snake=entity_snake)
    )
    return "".join(parts)


def main():
    """CLI: python -m TA.support.testing.codegen <module>:<EntityCls>"""
    if len(sys.argv) != 2 or ":" not in sys.argv[1]:
        sys.stderr.write(
            "Usage: python -m TA.support.testing.codegen <module>:<EntityCls>\n"
            "  Ex:  python -m TA.support.testing.codegen "
            "src.domain.entities.tenant:Tenant\n"
        )
        sys.exit(2)

    module_path, class_name = sys.argv[1].split(":", 1)
    try:
        module = import_module(module_path)
    except ImportError as exc:
        sys.stderr.write(f"Erro ao importar '{module_path}': {exc}\n")
        sys.exit(1)

    if not hasattr(module, class_name):
        sys.stderr.write(
            f"Classe '{class_name}' nao encontrada em '{module_path}'\n"
        )
        sys.exit(1)

    entity_cls = getattr(module, class_name)
    sys.stdout.write(generate_invariants_file(entity_cls))


if __name__ == "__main__":
    main()
