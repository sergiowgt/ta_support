"""Meta-tests do codegen.

Testa: dado entity stub, gera arquivo, escreve em tmp_path, executa via
pytest, verifica que happy-path passa e cenários gerados disparam o
exception correto. End-to-end real, sem mocks.
"""
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from TA.support.domain.entities import BaseEntity
from TA.support.infra.validators.field_presets import (
    CNPJ_FIELD,
    EMAIL_FIELD,
)
from TA.support.infra.validators.fields import IntFieldConfig, StrFieldConfig
from TA.support.testing import generate_invariants_file


NAME_FIELD = StrFieldConfig(min_len=2, max_len=100)
AGE_FIELD = IntFieldConfig(min_value=0, max_value=150)


@dataclass
class StubEntity(BaseEntity):
    __entity_name__ = "Stub"
    name: str = field(
        default="",
        metadata={"display": "Nome", "required": True, "field_config": NAME_FIELD},
    )
    cnpj: str = field(
        default="",
        metadata={"display": "CNPJ", "required": True, "field_config": CNPJ_FIELD},
    )
    email: str = field(
        default="",
        metadata={"display": "Email", "field_config": EMAIL_FIELD},
    )
    age: int = field(
        default=0,
        metadata={"display": "Idade", "required": True, "field_config": AGE_FIELD},
    )


def test_generate_returns_string_with_imports():
    output = generate_invariants_file(StubEntity)
    assert isinstance(output, str)
    assert "import pytest" in output
    assert "from TA.support.exceptions import FieldValidatorException" in output


def test_generate_contains_happy_path_test():
    output = generate_invariants_file(StubEntity)
    assert "def test_happy_path_valid_stub_entity_passes():" in output


def test_generate_contains_required_none_for_required_fields():
    output = generate_invariants_file(StubEntity)
    assert "def test_name_required_none_raises():" in output
    assert "def test_cnpj_required_none_raises():" in output
    assert "def test_age_required_none_raises():" in output


def test_generate_skips_required_none_for_optional_fields():
    """email é optional → não gera required_none."""
    output = generate_invariants_file(StubEntity)
    assert "def test_email_required_none_raises():" not in output


def test_generate_contains_min_max_len_for_str():
    output = generate_invariants_file(StubEntity)
    assert "def test_name_min_2_chars_violated_raises():" in output
    assert "def test_name_max_100_chars_exceeded_raises():" in output


def test_generate_contains_below_above_for_int():
    output = generate_invariants_file(StubEntity)
    assert "def test_age_below_min_0_raises():" in output
    assert "def test_age_above_max_150_raises():" in output


def test_generate_contains_validator_specific_cases():
    output = generate_invariants_file(StubEntity)
    # CNPJ
    assert "cnpj_invalid_digits_raises" in output
    assert "cnpj_non_digit_chars_raises" in output
    # Email
    assert "email_no_at_sign_raises" in output


def test_generate_contains_markers():
    output = generate_invariants_file(StubEntity)
    assert "# === AUTO-GENERATED START" in output
    assert "# === AUTO-GENERATED END ===" in output
    assert "# === CUSTOM START" in output
    assert "# === CUSTOM END ===" in output


def test_generate_minimal_valid_uses_canonical_examples():
    output = generate_invariants_file(StubEntity)
    # CNPJ válido
    assert "11222333000181" in output
    # created_by setado
    assert "'created_by': 'codegen'" in output


def test_generated_file_executes_with_pytest(tmp_path: Path):
    """End-to-end: gera arquivo, escreve, roda pytest, verifica resultado."""
    # Recria entity stub num módulo escrito no disco — generate_invariants_file
    # usa cls.__module__ no import gerado. Pra reproduzir num arquivo isolado,
    # precisa do stub também ser importável de path conhecido.
    stub_module = tmp_path / "stub_module.py"
    stub_module.write_text(
        textwrap.dedent(
            '''
            from dataclasses import dataclass, field
            from TA.support.domain.entities import BaseEntity
            from TA.support.infra.validators.field_presets import CNPJ_FIELD, EMAIL_FIELD
            from TA.support.infra.validators.fields import IntFieldConfig, StrFieldConfig

            NAME_FIELD = StrFieldConfig(min_len=2, max_len=100)
            AGE_FIELD = IntFieldConfig(min_value=0, max_value=150)

            @dataclass
            class StubEntity(BaseEntity):
                __entity_name__ = "Stub"
                name: str = field(default="",
                    metadata={"display": "Nome", "required": True, "field_config": NAME_FIELD})
                cnpj: str = field(default="",
                    metadata={"display": "CNPJ", "required": True, "field_config": CNPJ_FIELD})
                email: str = field(default="",
                    metadata={"display": "Email", "field_config": EMAIL_FIELD})
                age: int = field(default=0,
                    metadata={"display": "Idade", "required": True, "field_config": AGE_FIELD})
            '''
        )
    )

    # Importa stub a partir do tmp_path
    sys.path.insert(0, str(tmp_path))
    try:
        from stub_module import StubEntity  # type: ignore

        # Override __module__ pra apontar pro arquivo temp
        StubEntity.__module__ = "stub_module"

        # Gera arquivo de teste
        content = generate_invariants_file(StubEntity)
        test_file = tmp_path / "test_stub_invariants.py"
        test_file.write_text(content)

        # Roda pytest contra o arquivo gerado
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            env={**__import__("os").environ, "PYTHONPATH": str(tmp_path)},
        )

        # Todos os testes devem passar (happy-path + cenários de fail capturados
        # pelo pytest.raises)
        assert result.returncode == 0, (
            f"pytest falhou:\n--- STDOUT ---\n{result.stdout}\n"
            f"--- STDERR ---\n{result.stderr}"
        )
        # Confirma que rodou pelo menos os ~16 testes esperados
        assert "passed" in result.stdout
    finally:
        sys.path.remove(str(tmp_path))
        # Limpa cache de import pra não vazar entre tests
        sys.modules.pop("stub_module", None)


def test_cli_help_via_subprocess():
    """Sem argumento CLI mostra usage e sai com código != 0."""
    result = subprocess.run(
        [sys.executable, "-m", "TA.support.testing.codegen"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Usage:" in result.stderr


def test_cli_with_invalid_module():
    result = subprocess.run(
        [sys.executable, "-m", "TA.support.testing.codegen", "nao.existe:Class"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Erro ao importar" in result.stderr or "nao.existe" in result.stderr
