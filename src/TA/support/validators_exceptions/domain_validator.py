from datetime import date
from decimal import Decimal, InvalidOperation
import re
from typing import Any, Optional
from uuid import UUID

from TA.support.domain.entities.base_config_atributtes import CNPJ_FIELD, CPF_FIELD
from TA.support.domain.enums.state_code_enum import StateCodeEnum
from TA.support.i18n.message_provider import MessageProvider
from .domain_exception import DomainException
from .password_validation_error import PasswordValidationError
from dateutil.relativedelta import relativedelta

class DomainValidator:
    @staticmethod
    def string_required(value: str, field_name: str, exact_len: int = 0, min_len: int = 0, max_len: int = 0) -> None:
        DomainException.when(
            not isinstance(value, str),
            MessageProvider.get_message("validation.error.invalid_type", {"field": field_name, "type": "string"})
        )
        
        if value is not None:  # Permite strings vazias mas não None
            value = value.strip()

        DomainException.when(
            not value,
            MessageProvider.get_message("validation.error.empty_field", {"field": field_name})
        )

        if exact_len != 0:
            DomainException.when(
                len(value) != exact_len,
                MessageProvider.get_message("validation.error.exact_length", {
                    "field": field_name,
                    "exact": exact_len
                })
            )
        else:
            if min_len > 0:
                DomainException.when(
                    len(value) < min_len,
                    MessageProvider.get_message("validation.error.min_length", {
                        "field": field_name,
                        "min": min_len
                    })
                )
            if max_len > 0:
                DomainException.when(
                    len(value) > max_len,
                    MessageProvider.get_message("validation.error.max_length", {
                        "field": field_name,
                        "max": max_len
                    })
                )

    @classmethod
    def validate_email(cls, value: str, field_name: str, min_len: int = 0, max_len: int = 0) -> None:
        cls.string_required(value, field_name, 0, min_len, max_len)
        value = value.strip()
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        DomainException.when(
            re.fullmatch(regex, value) is None,
            MessageProvider.get_message("validation.error.invalid_email", {"field": field_name})
        )

    @classmethod
    def validate_cell_phone(cls, value: str, field_name: str, exact_len: int = 0) -> None:
        cls.string_required(value, field_name, exact_len, 0, 0)
        value = value.strip()
        regex = re.compile(r'^(\+?55)?([1-9]{2})9[0-9]{8}$')
        DomainException.when(
            re.fullmatch(regex, value) is None,
            MessageProvider.get_message("validation.error.invalid_phone", {"field": field_name})
        )

    @classmethod
    def validate_decimal(
        cls,
        value: Any,
        field_name: str,
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None
    ) -> None:
        # 1. Conversão para Decimal
        try:
            decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            raise DomainException(
                MessageProvider.get_message("validation.error.invalid_type", {
                    "field": field_name,
                    "type": "Decimal"
                })
            )
        
        # 2. Validação de valor mínimo
        if min_value is not None and decimal_value < min_value:
            raise DomainException(
                MessageProvider.get_message("validation.error.decimal.min_value", {
                    "field": field_name,
                    "min": min_value,
                    "actual": decimal_value
                })
            )
        
        # 3. Validação de valor máximo
        if max_value is not None and decimal_value > max_value:
            raise DomainException(
                MessageProvider.get_message("validation.error.decimal.max_value", {
                    "field": field_name,
                    "max": max_value,
                    "actual": decimal_value
                })
            )

    @classmethod
    def validate_integer(
        cls,
        value: Any,
        field_name: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> None:
        # 1. Conversão para inteiro
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            raise DomainException(
                MessageProvider.get_message("validation.error.invalid_type", {
                    "field": field_name,
                    "type": "integer"
                })
            )
        
        # 2. Validação de valor mínimo
        if min_value is not None and int_value < min_value:
            raise DomainException(
                MessageProvider.get_message("validation.error.integer.min_value", {
                    "field": field_name,
                    "min": min_value,
                    "actual": int_value
                })
            )
        
        # 3. Validação de valor máximo
        if max_value is not None and int_value > max_value:
            raise DomainException(
                MessageProvider.get_message("validation.error.integer.max_value", {
                    "field": field_name,
                    "max": max_value,
                    "actual": int_value
                })
            )

    @classmethod
    def validate_cpf(cls, value: str, field_name: str, exact_len: int = CPF_FIELD.exact) -> None:
            cls.string_required(value, field_name, exact_len, 0, 0)
            value = value.strip()
            regex = re.compile(r'^\d{11}$')
            DomainException.when(
                re.fullmatch(regex, value) is None or not cls._cpf_is_valid(value),
                MessageProvider.get_message("validation.error.invalid_cpf", {"field": field_name})
            )

    @classmethod
    def validate_cnpj(cls, value: str, field_name: str, exact_len: int = CNPJ_FIELD.exact) -> None:
        cls.string_required(value, field_name, exact_len, 0, 0)
        value = value.strip()
        regex = re.compile(r'^\d{14}$')
        DomainException.when(
            re.fullmatch(regex, value) is None or not cls._cnpj_is_valid(value),
            MessageProvider.get_message("validation.error.invalid_cnpj", {"field": field_name})
        )
    
    @staticmethod
    def _cpf_is_valid(cpf: str) -> bool:
        # Remove possíveis caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        for i in range(9, 11):
            sum = 0
            for j in range(0, i):
                sum += int(cpf[j]) * ((i + 1) - j)
            digit = ((sum * 10) % 11) % 10
            if int(cpf[i]) != digit:
                return False
        return True

    @staticmethod
    def _cnpj_is_valid(cnpj: str) -> bool:
        if len(cnpj) != 14 or cnpj in (c * 14 for c in "1234567890"):
            return False

        def calc_digit(cnpj, digit):
            if digit == 1:
                weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
                num = cnpj[:12]
            else:
                weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
                num = cnpj[:13]
            total = sum(int(n) * w for n, w in zip(num, weights))
            remainder = total % 11
            return '0' if remainder < 2 else str(11 - remainder)

        cnpj_numbers = re.sub(r'\D', '', cnpj)
        if len(cnpj_numbers) != 14:
            return False

        digit1 = calc_digit(cnpj_numbers, 1)
        digit2 = calc_digit(cnpj_numbers + digit1, 2)
        return cnpj_numbers[-2:] == digit1 + digit2
    
    @staticmethod
    def validate_id(value: int, field_name: str) -> None:
        DomainException.when(
            not isinstance(value, int),
            MessageProvider.get_message("validation.error.invalid_type", {
                "field": field_name,
                "type": "integer"
            })
        )
        DomainException.when(
            value <= 0,
            MessageProvider.get_message("validation.error.positive_integer", {"field": field_name})
        )

    @staticmethod
    def validate_uuid(value, field_name: str) -> None: 
        DomainException.when(
            not isinstance(value, UUID), 
            MessageProvider.get_message("validation.error.invalid_type", {"field": field_name, "type": "UUID"})); 
            
        DomainException.when(
            not value or value.int == 0, 
            MessageProvider.get_message("validation.error.invalid_uuid", {"field": field_name}))

    @staticmethod
    def validate_birth_date(birth_date: date, field_name: str, min_age: int = 0, max_age: int = 0) -> None:
        DomainException.when(
            not isinstance(birth_date, date),
            MessageProvider.get_message("validation.error.invalid_datetime", {"field": field_name})
        )

        today = date.today()
        DomainException.when(
            birth_date > today,
            MessageProvider.get_message("validation.error.future_date", {"field": field_name})
        )

        age = relativedelta(today, birth_date).years
        if min_age:
            DomainException.when(
                age < min_age,
                MessageProvider.get_message("validation.error.min_age", {
                    "field": field_name,
                    "min": min_age,
                    "actual": age
                })
            )

        if max_age:
            DomainException.when(
                age > max_age,
                MessageProvider.get_message("validation.error.max_age", {
                    "field": field_name,
                    "max": max_age,
                    "actual": age
                })
            )

    @classmethod
    def validate_password(cls, value: str, field_name: str, min_len: int = 8, max_len: int = 20) -> None:
        value = value.strip()

        # Verifica o tamanho
        PasswordValidationError.when(
            len(value) < min_len,
            MessageProvider.get_message("validation.error.password_min_length", {
                "field": field_name,
                "min": min_len
            })
        )
        
        PasswordValidationError.when(
            len(value) > max_len,
            MessageProvider.get_message("validation.error.password_max_length", {
                "field": field_name,
                "max": max_len
            })
        )

        # Verificações de complexidade
        checks = {
            "numeric": any(char.isdigit() for char in value),
            "alpha": any(char.isalpha() for char in value),
            "uppercase": any(char.isupper() for char in value),
            "special": any(not char.isalnum() for char in value)
        }

        for check_type, message_key in [
            ("numeric", "validation.error.password_numeric"),
            ("alpha", "validation.error.password_alpha"),
            ("uppercase", "validation.error.password_uppercase"),
            ("special", "validation.error.password_special")
        ]:
            PasswordValidationError.when(
                not checks[check_type],
                MessageProvider.get_message(message_key, {"field": field_name})
            )

    @staticmethod
    def validate_enum(value, enum_cls, field_name, custom_message_key=None):
        if isinstance(value, enum_cls): return
        try: 
            enum_cls(value.upper() if isinstance(value, str) else value)
        except ValueError:
            raise DomainException(
                MessageProvider.get_message(
                    custom_message_key or "validation.error.invalid_enum_value",
                    {"field": field_name, "value": value}
                )
            )
        
    @classmethod
    def validate_state_code(cls, value: str, field_name: str) -> None:
        if not value or not isinstance(value, str) or len(value) != 2:
            raise DomainException(
                MessageProvider.get_message(
                    "validation.error.invalid_state_code",
                    {"field": field_name, "value": value}
                )
            )
        # Valida se o valor está no Enum
        if value not in StateCodeEnum.__members__ and value not in StateCodeEnum._value2member_map_:
            raise DomainException(
                MessageProvider.get_message(
                    "validation.error.invalid_state_code",
                    {"field": field_name, "value": value}
                )
            )