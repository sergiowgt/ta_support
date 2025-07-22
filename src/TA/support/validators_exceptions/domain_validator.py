from datetime import date, datetime
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
    def string_required(value, field_name, field_config):
        if not value:
            raise DomainException(
                MessageProvider.get_message("validation.error.empty_field", {"field": field_name})
        )
        
        # Checagem: tipo
        DomainException.when(
            not isinstance(value, field_config.type),
            MessageProvider.get_message(
                "validation.error.invalid_type",
                {"field": field_name, "type": field_config.type.__name__}
            )
        )
        value = value.strip() if value is not None else ""

        # Preenchimento obrigatório
        DomainException.when(
            value == "",
            MessageProvider.get_message(
                "validation.error.empty_field",
                {"field": field_name}
            )
        )

        # Tamanho (exato ou mínimo/máximo)
        min_len = getattr(field_config, "minlen", 0)
        max_len = getattr(field_config, "maxlen", 0)

        if min_len and max_len and min_len == max_len:
            DomainException.when(
                len(value) != min_len,
                MessageProvider.get_message(
                    "validation.error.exact_length",
                    {"field": field_name, "exact": min_len}
                )
            )
        else:
            if min_len:
                DomainException.when(
                    len(value) < min_len,
                    MessageProvider.get_message(
                        "validation.error.min_length",
                        {"field": field_name, "min": min_len}
                    )
                )
            if max_len:
                DomainException.when(
                    len(value) > max_len,
                    MessageProvider.get_message(
                        "validation.error.max_length",
                        {"field": field_name, "max": max_len}
                    )
                )

    @classmethod
    def validate_email(cls, value, field_name, field_config):
        cls.string_required(value, field_name, field_config)
        value = value.strip()

        # Expressão regular robusta e case-insensitive
        regex = re.compile(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
            re.IGNORECASE
        )
        DomainException.when(
            re.fullmatch(regex, value) is None,
            MessageProvider.get_message(
                "validation.error.invalid_email",
                {"field": field_name}
            )
        )

    @classmethod
    def validate_datetime(self, value, field_name, field_config):
        if not value:
            raise DomainException(
                MessageProvider.get_message("validation.error.empty_field", {"field": field_name})
        )
        
        if not isinstance(value, datetime):
            msg_key = "validation.error.invalid_datetime"
            raise DomainException(
                MessageProvider.get_message(msg_key, {"field": field_name})
            )

        
    @classmethod
    def validate_cell_phone(cls, value, field_name, field_config):
        # Valida tipo, obrigatoriedade e tamanho exato conforme field_config
        cls.string_required(value, field_name, field_config)
        value = value.strip()

        regex = re.compile(r'^(\+?55)?([1-9]{2})9[0-9]{8}$')
        DomainException.when(
            re.fullmatch(regex, value) is None,
            MessageProvider.get_message(
                "validation.error.invalid_phone",
                {"field": field_name}
            )
        )

    @classmethod
    def validate_decimal(cls, value, field_name, field_config):
        # Conversão para decimal (tipo correto é responsabilidade desse método)
        try:
            decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            raise DomainException(
                MessageProvider.get_message(
                    "validation.error.invalid_type",
                    {"field": field_name, "type": "Decimal"}
                )
            )
        
        # Limites a partir do config
        min_value = getattr(field_config, "minlen", None)
        max_value = getattr(field_config, "maxlen", None)

        # Validação mínima
        if min_value is not None and min_value != 0 and decimal_value < Decimal(str(min_value)):
            raise DomainException(
                MessageProvider.get_message(
                    "validation.error.decimal.min_value",
                    {"field": field_name, "min": min_value, "actual": decimal_value}
                )
            )

        # Validação máxima
        if max_value is not None and max_value != 0 and decimal_value > Decimal(str(max_value)):
            raise DomainException(
                MessageProvider.get_message(
                    "validation.error.decimal.max_value",
                    {"field": field_name, "max": max_value, "actual": decimal_value}
                )
            )

    @classmethod
    def validate_integer(value, field_name, field_config):
        # Tenta converter para inteiro
        try:
            int_value = value if isinstance(value, int) else int(value)
        except (TypeError, ValueError):
            raise DomainException(
                MessageProvider.get_message(
                    "validation.error.invalid_type",
                    {"field": field_name, "type": "integer"}
                )
            )
        
        # Limites extraídos do config
        min_value = getattr(field_config, "minlen", None)
        max_value = getattr(field_config, "maxlen", None)

        # Observa: ignore limites quando None ou 0 (sem restrição)
        if min_value is not None and min_value != 0 and int_value < min_value:
            raise DomainException(
                MessageProvider.get_message(
                    "validation.error.integer.min_value",
                    {"field": field_name, "min": min_value, "actual": int_value}
                )
            )
        if max_value is not None and max_value != 0 and int_value > max_value:
            raise DomainException(
                MessageProvider.get_message(
                    "validation.error.integer.max_value",
                    {"field": field_name, "max": max_value, "actual": int_value}
            )
        )
    @classmethod
    def validate_cpf(cls, value: str, field_name: str, field_config) -> None:
            cls.string_required(value, field_name, field_config)
            value = value.strip()
            regex = re.compile(r'^\d{11}$')
            DomainException.when(
                re.fullmatch(regex, value) is None or not cls._cpf_is_valid(value),
                MessageProvider.get_message("validation.error.invalid_cpf", {"field": field_name})
            )

    @classmethod
    def validate_cnpj(cls, value, field_name, field_config):
        # Validação de tipo, obrigatoriedade e tamanho exato conforme config
        cls.string_required(value, field_name, field_config)
        value = value.strip()

        # Regex: apenas dígitos, exatamente 14 caracteres
        regex = re.compile(r'^\d{14}$')
        DomainException.when(
            re.fullmatch(regex, value) is None or not cls._cnpj_is_valid(value),
            MessageProvider.get_message(
                "validation.error.invalid_cnpj",
                {"field": field_name}
            )
        )
    
    @staticmethod
    def validate_uuid(value, field_name, field_config=None):
        DomainException.when(
            not isinstance(value, UUID),
            MessageProvider.get_message(
                "validation.error.invalid_type",
                {"field": field_name, "type": "UUID"}
            )
        )

        # Verifica se o UUID é vazio/nulo (UUID all zero)
        DomainException.when(
            value is None or value.int == 0,
            MessageProvider.get_message(
                "validation.error.invalid_uuid",
                {"field": field_name}
            )
        )
   
    @staticmethod
    def validate_birth_date(value, field_name, field_config):
        # Checagem de tipo
        DomainException.when(
            not isinstance(value, date),
            MessageProvider.get_message(
                "validation.error.invalid_datetime",
                {"field": field_name}
            )
        )

        today = date.today()
        # Não aceita data futura
        DomainException.when(
            value > today,
            MessageProvider.get_message(
                "validation.error.future_date",
                {"field": field_name}
            )
        )

        # Calcula idade
        age = relativedelta(today, value).years

        min_age = getattr(field_config, "minlen", 0)
        max_age = getattr(field_config, "maxlen", 0)

        # Checa idade mínima se definida (>0)
        if min_age:
            DomainException.when(
                age < min_age,
                MessageProvider.get_message(
                    "validation.error.min_age",
                    {"field": field_name, "min": min_age, "actual": age}
                )
            )
        # Checa idade máxima se definida (>0)
        if max_age:
            DomainException.when(
                age > max_age,
                MessageProvider.get_message(
                    "validation.error.max_age",
                    {"field": field_name, "max": max_age, "actual": age}
                )
            )

    @classmethod
    def validate_password(cls, value, field_name, field_config):
        value = value.strip() if value else ""

        min_len = getattr(field_config, "minlen", 8)
        max_len = getattr(field_config, "maxlen", 20)

        # Verifica comprimento mínimo
        PasswordValidationError.when(
            len(value) < min_len,
            MessageProvider.get_message("validation.error.password_min_length", {
                "field": field_name,
                "min": min_len
            })
        )
        # Verifica comprimento máximo
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

        # Mensagens para cada requisito de complexidade
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
    def validate_state_code(cls, value: str, field_name: str, field_config=None) -> None:
        max_len = getattr(field_config, "maxlen", 2)
        if not value or not isinstance(value, str) or len(value) != max_len:
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