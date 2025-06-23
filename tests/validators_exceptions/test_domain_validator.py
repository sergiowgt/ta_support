from pathlib import Path
import pytest
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4
from TA.support.i18n.message_provider import MessageProvider
from TA.support.validators_exceptions.domain_exception import DomainException
from TA.support.validators_exceptions.password_validation_error import PasswordValidationError
from TA.support.validators_exceptions.domain_validator import DomainValidator

class TestDomainValidator:
    @classmethod
    def setup_class(cls): MessageProvider._load_locales(Path('/Users/sergiosousa/TA.support/locales'))
    def setup_method(self): MessageProvider.set_language("pt_BR")

    @pytest.mark.parametrize("value, exact_len, min_len, max_len, should_raise", [
        (123, 0, 0, 0, True),  # Não é string
        ("", 0, 0, 0, True),    # String vazia
        ("  ", 0, 0, 0, True),  # String com espaços
        ("abc", 5, 0, 0, True), # Tamanho exato incorreto
        ("a", 0, 3, 0, True),   # Abaixo do mínimo
        ("abcd", 0, 0, 3, True),# Acima do máximo
        ("valid", 0, 0, 0, False),
    ])
    def test_string_required(self, value, exact_len, min_len, max_len, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.string_required(value, "Test Field", exact_len, min_len, max_len)
        else:
            DomainValidator.string_required(value, "Test Field", exact_len, min_len, max_len)

    @pytest.mark.parametrize("email, min_len, max_len, should_raise", [
        ("invalid", 0, 0, True),        # Formato inválido
        ("a@b.c", 10, 0, True),         # Tamanho mínimo
        ("a" * 50 + "@exemplo.com", 0, 30, True), # Tamanho máximo
        ("valido@exemplo.com", 0, 0, False),
    ])
    def test_validate_email(self, email, min_len, max_len, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_email(email, "Email", min_len, max_len)
        else:
            DomainValidator.validate_email(email, "Email", min_len, max_len)

    @pytest.mark.parametrize("phone, exact_len, should_raise", [
        ("11999999999", 11, False),     # Válido
        ("11 99999-9999", 11, True),    # Formato inválido
        ("119999999", 11, True),         # Tamanho incorreto
    ])
    def test_validate_cell_phone(self, phone, exact_len, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_cell_phone(phone, "Celular", exact_len)
        else:
            DomainValidator.validate_cell_phone(phone, "Celular", exact_len)

    @pytest.mark.parametrize("value, min_val, max_val, should_raise", [
        ("not_decimal", None, None, True),   # Não é decimal
        (Decimal('5.0'), Decimal('10.0'), None, True),   # Abaixo do mínimo
        (Decimal('15.0'), None, Decimal('10.0'), True),  # Acima do máximo
        (Decimal('7.5'), Decimal('5.0'), Decimal('10.0'), False),
    ])
    def test_validate_decimal(self, value, min_val, max_val, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_decimal(value, "Decimal Field", min_val, max_val)
        else:
            DomainValidator.validate_decimal(value, "Decimal Field", min_val, max_val)

    @pytest.mark.parametrize("value, min_val, max_val, should_raise", [
        ("not_int", None, None, True),   # Não é inteiro
        (5, 10, None, True),             # Abaixo do mínimo
        (15, None, 10, True),            # Acima do máximo
        (7, 5, 10, False),
    ])
    def test_validate_integer(self, value, min_val, max_val, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_integer(value, "Inteiro", min_val, max_val)
        else:
            DomainValidator.validate_integer(value, "Inteiro", min_val, max_val)

    @pytest.mark.parametrize("cpf, exact_len, should_raise", [
        ("12345678909", 11, False),      # Válido
        ("11111111111", 11, True),       # Inválido (dígitos repetidos)
        ("123", 11, True),               # Tamanho incorreto
    ])
    def test_validate_cpf(self, cpf, exact_len, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_cpf(cpf, "CPF", exact_len)
        else:
            DomainValidator.validate_cpf(cpf, "CPF", exact_len)

    @pytest.mark.parametrize("value, should_raise", [
        (123, True),         # Não é UUID
        (UUID(int=0), True), # UUID inválido (zero)
        (uuid4(), False),    # Válido
    ])
    def test_validate_uuid(self, value, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_uuid(value, "UUID")
        else:
            DomainValidator.validate_uuid(value, "UUID")

    @pytest.mark.parametrize("birth_date, min_age, max_age, should_raise", [
        (date.today() + timedelta(days=1), 0, 0, True),  # Data futura
        (date(2010, 1, 1), 18, 0, True),                 # Idade abaixo do mínimo
        (date(1900, 1, 1), 0, 100, True),                # Idade acima do máximo
        (date(1990, 1, 1), 18, 70, False),
    ])
    def test_validate_birth_date(self, birth_date, min_age, max_age, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_birth_date(birth_date, "Data Nasc.", min_age, max_age)
        else:
            DomainValidator.validate_birth_date(birth_date, "Data Nasc.", min_age, max_age)

    @pytest.mark.parametrize("password, min_len, max_len, should_raise", [
        ("short", 8, 20, True),          # Tamanho mínimo
        ("a" * 21, 8, 20, True),         # Tamanho máximo
        ("nouppercase1!", 8, 20, True),  # Sem maiúscula
        ("NONUMBER!", 8, 20, True),      # Sem número
        ("NoSpecial1", 8, 20, True),     # Sem caractere especial
        ("ValidPass1!", 8, 20, False),
    ])
    def test_validate_password(self, password, min_len, max_len, should_raise):
        if should_raise:
            with pytest.raises(PasswordValidationError):
                DomainValidator.validate_password(password, "Senha", min_len, max_len)
        else:
            DomainValidator.validate_password(password, "Senha", min_len, max_len)

    def test_validate_enum(self):
        from enum import Enum
        class TestEnum(Enum):
            A = 1
            B = 2
        
        # Valor válido
        DomainValidator.validate_enum(TestEnum.A, TestEnum, "Enum")
        
        # Valor inválido
        with pytest.raises(DomainException):
            DomainValidator.validate_enum(3, TestEnum, "Enum")
