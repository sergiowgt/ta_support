import decimal
from pathlib import Path
import pytest
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4
from TA.support.i18n.message_provider import MessageProvider
from TA.support.validators_exceptions.password_validation_error import PasswordValidationError
from TA.support.validators_exceptions import DomainValidator, DomainException
from TA.support.domain.entities.base_config_atributtes import *

class TestDomainValidator:
    @classmethod
    def setup_class(cls): 
        MessageProvider._load_locales(Path('/Users/sergiosousa/work/Lab/DentalInclusiva/src/locales'))

    def setup_method(self): MessageProvider.set_language("pt_BR")

    @pytest.mark.parametrize("value, field_config, should_raise", [
        (123, FieldConfig(str, 0, 0, 'DomainValidator.string_required'), True),  # Não é string
        ("", FieldConfig(str, 0, 0, 'DomainValidator.string_required'), True),    # String vazia
        ("  ", FieldConfig(str, 0, 0, 'DomainValidator.string_required'), True),  # String com espaços
        ("abc", FieldConfig(str, 5, 5, 'DomainValidator.string_required'), True), # Tamanho exato incorreto
        ("a", FieldConfig(str, 3, 0, 'DomainValidator.string_required'), True),   # Abaixo do mínimo
        ("abcd", FieldConfig(str, 0, 3, 'DomainValidator.string_required'), True),# Acima do máximo
        ("valid", FieldConfig(str, 0, 0, 'DomainValidator.string_required'), False)
    ])
    def test_string_required(self, value, field_config, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.string_required(value, "Test Field", field_config)
        else:
            DomainValidator.string_required(value, "Test Field", field_config)

    @pytest.mark.parametrize("email, field_config, should_raise", [
        ("invalid", FieldConfig(str, 0, 0, 'DomainValidator.validate_email'), True),        # Formato inválido
        ("a@b.c", FieldConfig(str, 10, 0, 'DomainValidator.validate_email'), True),         # Tamanho mínimo
        ("a" * 50 + "@exemplo.com", FieldConfig(str, 0, 30, 'DomainValidator.validate_email'), True), # Tamanho máximo
        ("valido@exemplo.com", FieldConfig(str, 0, 0, 'DomainValidator.validate_email'), False),
    ])
    def test_validate_email(self, email, field_config, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_email(email, "Email", field_config)
        else:
            DomainValidator.validate_email(email, "Email", field_config)

    @pytest.mark.parametrize("phone, field_config, should_raise", [
        ("11999999999", FieldConfig(str, 11, 11, 'DomainValidator.validate_phone'), False),     # Válido
        ("11 99999-9999", FieldConfig(str, 11, 11, 'DomainValidator.validate_phone'), True),    # Formato inválido
        ("119999999", FieldConfig(str, 11, 11, 'DomainValidator.validate_phone'), True),         # Tamanho incorreto
    ])
    def test_validate_cell_phone(self, phone, field_config, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_cell_phone(phone, "Celular", field_config)
        else:
            DomainValidator.validate_cell_phone(phone, "Celular", field_config)

    @pytest.mark.parametrize("value, field_config, should_raise", [
        ("not_decimal", FieldConfig(decimal, None, None, 'DomainValidator.validate_decimal'), True),   # Não é decimal
        (Decimal('5.0'), FieldConfig(decimal, Decimal('10.0'), None, 'DomainValidator.validate_decimal'), True),   # Abaixo do mínimo
        (Decimal('15.0'), FieldConfig(decimal, None, Decimal('10.0'), 'DomainValidator.validate_decimal'), True),  # Acima do máximo
        (Decimal('7.5'), FieldConfig(decimal, Decimal('5.0'), Decimal('10.0'), 'DomainValidator.validate_decimal'), False),
    ])
    def test_validate_decimal(self, value, field_config, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_decimal(value, "Decimal Field", field_config)
        else:
            DomainValidator.validate_decimal(value, "Decimal Field", field_config)

    
    @pytest.mark.parametrize("cpf, field_config, should_raise", [
        ("12345678909", FieldConfig(str, 11, 11, 'DomainValidator.validate_cpf'), False),      # Válido
        ("11111111111", FieldConfig(str, 11, 11, 'DomainValidator.validate_cpf'), True),       # Inválido (dígitos repetidos)
        ("123", FieldConfig(str, 11, 11, 'DomainValidator.validate_cpf'), True),               # Tamanho incorreto
    ])
    def test_validate_cpf(self, cpf, field_config, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_cpf(cpf, "CPF", field_config)
        else:
            DomainValidator.validate_cpf(cpf, "CPF", field_config)

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

    @pytest.mark.parametrize("birth_date, field_config, should_raise", [
        (date.today() + timedelta(days=1),  FieldConfig(datetime, 0, 0, 'DomainValidator.validate_birth_date'), True),  # Data futura
        (date(2010, 1, 1),  FieldConfig(datetime, 18, 0, 'DomainValidator.validate_birth_date'), True),                 # Idade abaixo do mínimo
        (date(1900, 1, 1),  FieldConfig(datetime, 0, 100, 'DomainValidator.validate_birth_date'), True),                # Idade acima do máximo
        (date(1990, 1, 1),  FieldConfig(datetime, 18, 70, 'DomainValidator.validate_birth_date'), False),
    ])
    def test_validate_birth_date(self, birth_date, field_config, should_raise):
        if should_raise:
            with pytest.raises(DomainException):
                DomainValidator.validate_birth_date(birth_date, "Data Nasc.", field_config)
        else:
            DomainValidator.validate_birth_date(birth_date, "Data Nasc.", field_config)

    @pytest.mark.parametrize("password, field_config, should_raise", [
        ("short", FieldConfig(str, 8, 20, 'DomainValidator.validate_password'), True),          # Tamanho mínimo
        ("a" * 21, FieldConfig(str, 8, 20, 'DomainValidator.validate_password'), True),         # Tamanho máximo
        ("nouppercase1!", FieldConfig(str, 8, 20, 'DomainValidator.validate_password'), True),  # Sem maiúscula
        ("NONUMBER!", FieldConfig(str, 8, 20, 'DomainValidator.validate_password'), True),      # Sem número
        ("NoSpecial1", FieldConfig(str, 8, 20, 'DomainValidator.validate_password'), True),     # Sem caractere especial
        ("ValidPass1!", FieldConfig(str, 8, 20, 'DomainValidator.validate_password'), False),
    ])
    def test_validate_password(self, password, field_config, should_raise):
        if should_raise:
            with pytest.raises(PasswordValidationError):
                DomainValidator.validate_password(password, "Senha", field_config)
        else:
            DomainValidator.validate_password(password, "Senha", field_config)

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
