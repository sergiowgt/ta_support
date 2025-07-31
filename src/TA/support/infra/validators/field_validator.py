from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import json
import re
from uuid import UUID
from TA.support.domain.enums.state_code_enum import StateCodeEnum
from TA.support.domain.enums.status_enum import StatusEnum
from TA.support.i18n.message_provider import MessageProvider
from dateutil.relativedelta import relativedelta
from TA.support.exceptions.field_validator_exception import FieldValidatorException

class FieldValidator:
    @staticmethod
    def _cpf_is_valid(cpf: str) -> bool:
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
    def validate_string(value, display_name, field_config):
        if not value:
            raise FieldValidatorException(
                MessageProvider.get_message("validation.error.empty_field", {"field": display_name})
        )
        
        FieldValidatorException.when(
            not isinstance(value, field_config.type),
            MessageProvider.get_message(
                "validation.error.invalid_type",
                {"field": display_name, "type": field_config.type.__name__}
            )
        )
        value = value.strip() if value is not None else ""

        # Preenchimento obrigatório
        FieldValidatorException.when(
            value == "",
            MessageProvider.get_message(
                "validation.error.empty_field",
                {"field": display_name}
            )
        )

        # Tamanho (exato ou mínimo/máximo)
        min_len = getattr(field_config, "min_len", 0)
        max_len = getattr(field_config, "max_len", 0)

        if min_len and max_len and min_len == max_len:
            FieldValidatorException.when(
                len(value) != min_len,
                MessageProvider.get_message(
                    "validation.error.exact_length",
                    {"field": display_name, "exact": min_len}
                )
            )
        else:
            if min_len:
                FieldValidatorException.when(
                    len(value) < min_len,
                    MessageProvider.get_message(
                        "validation.error.min_length",
                        {"field": display_name, "min": min_len}
                    )
                )
            if max_len:
                FieldValidatorException.when(
                    len(value) > max_len,
                    MessageProvider.get_message(
                        "validation.error.max_length",
                        {"field": display_name, "max": max_len}
                    )
                )
    @staticmethod
    def validate_json(value, display_name, field_config):
        if not value:
            raise FieldValidatorException(
                MessageProvider.get_message("validation.error.empty_field", {"field": display_name})
        )
        
        try:
            json.loads(value)
        except Exception:
            raise FieldValidatorException(
                MessageProvider.get_message("validation.error.invalid_json", {"field": display_name})
            )
                
    @classmethod
    def validate_email(cls, value, display_name, field_config):
        cls.validate_string(value, display_name, field_config)
        value = value.strip()

        # Expressão regular robusta e case-insensitive
        regex = re.compile(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
            re.IGNORECASE
        )
        FieldValidatorException.when(
            re.fullmatch(regex, value) is None,
            MessageProvider.get_message(
                "validation.error.invalid_email",
                {"field": display_name}
            )
        )

    @classmethod
    def validate_datetime(self, value, display_name, field_config):
        if not value:
            raise FieldValidatorException(
                MessageProvider.get_message("validation.error.empty_field", {"field": display_name})
        )
        
        if not isinstance(value, datetime):
            msg_key = "validation.error.invalid_datetime"
            raise FieldValidatorException(
                MessageProvider.get_message(msg_key, {"field": display_name})
            )

    @classmethod
    def validate_cell_phone(cls, value, display_name, field_config):
        cls.validate_string(value, display_name, field_config)
        value = value.strip()

        regex = re.compile(r'^(\+?55)?([1-9]{2})9[0-9]{8}$')
        FieldValidatorException.when(
            re.fullmatch(regex, value) is None,
            MessageProvider.get_message(
                "validation.error.invalid_phone",
                {"field": display_name}
            )
        )

    @classmethod
    def validate_decimal(cls, value, display_name, field_config):
        # Conversão para decimal (tipo correto é responsabilidade desse método)
        try:
            decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.invalid_type",
                    {"field": display_name, "type": "Decimal"}
                )
            )
        
        # Limites a partir do config
        min_value = getattr(field_config, "min_len", None)
        max_value = getattr(field_config, "max_len", None)

        # Validação mínima
        if min_value is not None and min_value != 0 and decimal_value < Decimal(str(min_value)):
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.decimal.min_value",
                    {"field": display_name, "min": min_value, "actual": decimal_value}
                )
            )

        # Validação máxima
        if max_value is not None and max_value != 0 and decimal_value > Decimal(str(max_value)):
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.decimal.max_value",
                    {"field": display_name, "max": max_value, "actual": decimal_value}
                )
            )

    @classmethod
    def validate_integer(cls,value, display_name, field_config):
        # Tenta converter para inteiro
        try:
            int_value = value if isinstance(value, int) else int(value)
        except (TypeError, ValueError):
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.invalid_type",
                    {"field": display_name, "type": "integer"}
                )
            )
        
        # Limites extraídos do config
        min_value = getattr(field_config, "min_len", None)
        max_value = getattr(field_config, "max_len", None)

        # Observa: ignore limites quando None ou 0 (sem restrição)
        if min_value is not None and min_value != 0 and int_value < min_value:
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.integer.min_value",
                    {"field": display_name, "min": min_value, "actual": int_value}
                )
            )
        if max_value is not None and max_value != 0 and int_value > max_value:
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.integer.max_value",
                    {"field": display_name, "max": max_value, "actual": int_value}
            )
        )

    @classmethod
    def validate_cpf(cls, value: str, display_name: str, field_config) -> None:
            cls.validate_string(value, display_name, field_config)
            value = value.strip()
            regex = re.compile(r'^\d{11}$')
            FieldValidatorException.when(
                re.fullmatch(regex, value) is None or not cls._cpf_is_valid(value),
                MessageProvider.get_message("validation.error.invalid_cpf", {"field": display_name})
            )

    @classmethod
    def validate_cnpj(cls, value, display_name, field_config):
        # Validação de tipo, obrigatoriedade e tamanho exato conforme config
        cls.validate_string(value, display_name, field_config)
        value = value.strip()

        # Regex: apenas dígitos, exatamente 14 caracteres
        regex = re.compile(r'^\d{14}$')
        FieldValidatorException.when(
            re.fullmatch(regex, value) is None or not cls._cnpj_is_valid(value),
            MessageProvider.get_message(
                "validation.error.invalid_cnpj",
                {"field": display_name}
            )
        )
   
    @staticmethod
    def validate_uuid(value, display_name, field_config=None):
        FieldValidatorException.when(
            not isinstance(value, UUID),
            MessageProvider.get_message(
                "validation.error.invalid_type",
                {"field": display_name, "type": "UUID"}
            )
        )

        # Verifica se o UUID é vazio/nulo (UUID all zero)
        FieldValidatorException.when(
            value is None or value.int == 0,
            MessageProvider.get_message(
                "validation.error.invalid_uuid",
                {"field": display_name}
            )
        )
   
    @staticmethod
    def validate_birth_date(value, display_name, field_config):
        # Checagem de tipo
        FieldValidatorException.when(
            not isinstance(value, date),
            MessageProvider.get_message(
                "validation.error.invalid_datetime",
                {"field": display_name}
            )
        )

        today = date.today()
        # Não aceita data futura
        FieldValidatorException.when(
            value > today,
            MessageProvider.get_message(
                "validation.error.future_date",
                {"field": display_name}
            )
        )

        # Calcula idade
        age = relativedelta(today, value).years

        min_age = getattr(field_config, "min_len", 0)
        max_age = getattr(field_config, "max_len", 0)

        # Checa idade mínima se definida (>0)
        if min_age:
            FieldValidatorException.when(
                age < min_age,
                MessageProvider.get_message(
                    "validation.error.min_age",
                    {"field": display_name, "min": min_age, "actual": age}
                )
            )
        # Checa idade máxima se definida (>0)
        if max_age:
            FieldValidatorException.when(
                age > max_age,
                MessageProvider.get_message(
                    "validation.error.max_age",
                    {"field": display_name, "max": max_age, "actual": age}
                )
            )

    @classmethod
    def validate_password(cls, value, display_name, field_config):
        value = value.strip() if value else ""

        min_len = getattr(field_config, "min_len", 8)
        max_len = getattr(field_config, "max_len", 20)

        # Verifica comprimento mínimo
        FieldValidatorException.when(
            len(value) < min_len,
            MessageProvider.get_message("validation.error.password_min_length", {
                "field": display_name,
                "min": min_len
            })
        )
        # Verifica comprimento máximo
        FieldValidatorException.when(
            len(value) > max_len,
            MessageProvider.get_message("validation.error.password_max_length", {
                "field": display_name,
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
            FieldValidatorException.when(
                not checks[check_type],
                MessageProvider.get_message(message_key, {"field": display_name})
            )

    @staticmethod
    def validate_enum(value, enum_cls, display_name, custom_message_key=None):
        if isinstance(value, enum_cls): return
        try: 
            enum_cls(value.upper() if isinstance(value, str) else value)
        except ValueError:
            raise FieldValidatorException(
                MessageProvider.get_message(
                    custom_message_key or "validation.error.invalid_enum_value",
                    {"field": display_name, "value": value}
                )
            )
        
    @classmethod
    def validate_state_code(cls, value: str, display_name: str, field_config=None) -> None:
        max_len = getattr(field_config, "max_len", 2)
        if not value or not isinstance(value, str) or len(value) != max_len:
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.invalid_state_code",
                    {"field": display_name, "value": value}
                )
            )

        if value not in StateCodeEnum.__members__ and value not in StateCodeEnum._value2member_map_:
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.invalid_state_code",
                    {"field": display_name, "value": value}
                )
            )
        
    @classmethod
    def validate_status(cls, value: int, display_name: str, field_config=None) -> None:
        # Verifica se é do tipo int
        if not isinstance(value, int):
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.invalid_status_type",
                    {"field": display_name, "value": value}
                )
            )
        # Verifica se o int é membro válido do StatusEnum
        try:
            StatusEnum(value)
        except ValueError:
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.invalid_status_value",
                    {"field": display_name, "value": value}
                )
            )