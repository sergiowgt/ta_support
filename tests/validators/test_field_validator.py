
from decimal import Decimal
from pathlib import Path

import pytest
from TA.support.exceptions.field_validator_exception import FieldValidatorException
from TA.support.i18n.message_provider import MessageProvider
from TA.support.infra.validators.field_validator import FieldValidator
from TA.support.infra.validators.fields.decimal_field_config import DecimalFieldConfig
from TA.support.infra.validators.fields.int_field_config import IntFieldConfig
from TA.support.infra.validators.fields.str_field_config import StrFieldConfig


class TestFieldValidator:
    @classmethod
    def setup_class(cls): 
        MessageProvider._load_locales(Path('/Users/sergiosousa/work/Lab/DentalInclusiva/src/locales'))

    def setup_method(self): 
        MessageProvider.set_language("pt_BR")
    
    def test_invalid_decimal_error(self):
        # arrange
        field_config = DecimalFieldConfig()
        field_description = "Test Field"
        value = "x"
        
        #act
        with pytest.raises(FieldValidatorException) as exc: 
            FieldValidator.validate_decimal(value, field_description, field_config)

        assert MessageProvider.get_message("validation.error.invalid_type", {"field": field_description, "type": "Decimal"}) in str(exc.value)
        
    def test_less_min_decimal_error(self):
        # arrange
        min_value=Decimal('0')
        field_config = DecimalFieldConfig(min_value=min_value)
        field_description = "Test Field"
        value = -1
        
        #act
        with pytest.raises(FieldValidatorException) as exc: 
            FieldValidator.validate_decimal(value, field_description, field_config)

        assert MessageProvider.get_message("validation.error.decimal.min_value", 
                                            {"field": field_description, 
                                            "type": "Decimal",
                                            "min": min_value, 
                                            "actual": value
                                            }
                                            ) in str(exc.value)
        
    def test_great_max_decimal_error(self):
        # arrange
        max_value=Decimal('10')
        field_config = DecimalFieldConfig(max_value=max_value)
        field_description = "Test Field"
        value = 11
        
        #act
        with pytest.raises(FieldValidatorException) as exc: 
            FieldValidator.validate_decimal(value, field_description, field_config)

        assert MessageProvider.get_message("validation.error.decimal.max_value", 
                                            {"field": field_description, 
                                            "type": "Decimal",
                                            "max": max_value, 
                                            "actual": value
                                            }
                                            ) in str(exc.value)
            
    def test_valid_decimal_success(self):
        # arrange
        min_value=Decimal('1')
        max_value=Decimal('10')
        field_config = DecimalFieldConfig(min_value=min_value,max_value=max_value)
        field_description = "Test Field"
        value = 9
        
        #act
        FieldValidator.validate_decimal(value, field_description, field_config)

        assert True
        
    def test_invalid_int_error(self):
        # arrange
        field_config = IntFieldConfig()
        field_description = "Test Field"
        value = "x"
        
        #act
        with pytest.raises(FieldValidatorException) as exc: 
            FieldValidator.validate_integer(value, field_description, field_config)

        assert MessageProvider.get_message("validation.error.invalid_type", {"field": field_description, "type": "in"}) in str(exc.value)
        
    def test_less_min_int_error(self):
        # arrange
        min_value=0
        field_config = IntFieldConfig(min_value=min_value)
        field_description = "Test Field"
        value = -1
        
        #act
        with pytest.raises(FieldValidatorException) as exc: 
            FieldValidator.validate_integer(value, field_description, field_config)

        assert MessageProvider.get_message("validation.error.decimal.min_value", 
                                            {"field": field_description, 
                                            "type": "Decimal",
                                            "min": min_value, 
                                            "actual": value
                                            }
                                            ) in str(exc.value)
        
    def test_great_max_int_error(self):
        # arrange
        max_value=10
        field_config = IntFieldConfig(max_value=max_value)
        field_description = "Test Field"
        value = 11
        
        #act
        with pytest.raises(FieldValidatorException) as exc: 
            FieldValidator.validate_integer(value, field_description, field_config)

        assert MessageProvider.get_message("validation.error.decimal.max_value", 
                                            {"field": field_description, 
                                            "type": "Decimal",
                                            "max": max_value, 
                                            "actual": value
                                            }
                                            ) in str(exc.value)
            
    def test_valid_int_success(self):
        # arrange
        min_value=1
        max_value=10
        field_config = IntFieldConfig(min_value=min_value,max_value=max_value)
        field_description = "Test Field"
        value = 9
        
        #act
        FieldValidator.validate_integer(value, field_description, field_config)

        assert True
        
    def test_invalid_str_error(self):
        # arrange
        field_config = StrFieldConfig()
        field_description = "Test Field"
        value = 10
        
        #act
        with pytest.raises(FieldValidatorException) as exc: 
            FieldValidator.validate_string(value, field_description, field_config)

        assert MessageProvider.get_message("validation.error.invalid_type", {"field": field_description, "type": "str"}) in str(exc.value)
    
    def test_empty_str_error(self):
        # arrange
        field_config = StrFieldConfig()
        field_description = "Test Field"
        value = "  "
        
        #act
        with pytest.raises(FieldValidatorException) as exc: 
            FieldValidator.validate_string(value, field_description, field_config)

        assert MessageProvider.get_message("validation.error.empty_field", {"field": field_description}) in str(exc.value)
        
    def test_less_min_len_str_error(self):
        # arrange
        min_len=5
        field_config = StrFieldConfig(min_len=min_len)
        field_description = "Test Field"
        value = "x"*(min_len-1)
        
        #act
        with pytest.raises(FieldValidatorException) as exc: 
            FieldValidator.validate_string(value, field_description, field_config)

        assert MessageProvider.get_message("validation.error.min_length", 
                                            {"field": field_description, 
                                            "min": min_len, 
                                            "actual": value
                                            }
                                            ) in str(exc.value)
    def test_great_max_len_str_error(self):
        # arrange
        max_len=20
        field_config = StrFieldConfig(max_len=max_len)
        field_description = "Test Field"
        value = "x"*(max_len+1)
        
        #act
        with pytest.raises(FieldValidatorException) as exc: 
            FieldValidator.validate_string(value, field_description, field_config)

        assert MessageProvider.get_message("validation.error.max_length", 
                                            {"field": field_description, 
                                            "max": max_len, 
                                            "actual": value
                                            }
                                            ) in str(exc.value)
        
    def test_diff_exact_len_str_error(self):
        # arrange
        min_len=5
        max_len=min_len
        field_config = StrFieldConfig(min_len=min_len, max_len=max_len)
        field_description = "Test Field"
        value = "x"*(min_len+1)
        
        #act
        with pytest.raises(FieldValidatorException) as exc: 
            FieldValidator.validate_string(value, field_description, field_config)

        assert MessageProvider.get_message("validation.error.exact_length", 
                                            {"field": field_description, 
                                            "exact": max_len, 
                                            "actual": value
                                            }
                                            ) in str(exc.value)
        
    def test_valid_len_str_error(self):
        # arrange
        min_len=0
        max_len=20
        field_config = StrFieldConfig(min_len=min_len, max_len=max_len)
        field_description = "Test Field"
        value = "x"*(max_len-1)
        
        #act
        FieldValidator.validate_string(value, field_description, field_config)

        assert True
        
        
        
        
        """     if min_value is not None and decimal_value < Decimal(str(min_value)):
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.decimal.min_value",
                    {"field": display_name, "min": min_value, "actual": decimal_value}
                )
            )
        
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
        min_value = getattr(field_config, "min_value", Decimal('0'))
        max_value = getattr(field_config, "max_value", Decimal('0'))

        # Validação mínima, quando min_value não é um valor padrão (0, 0.0, '', None)
        if min_value is not None and decimal_value < Decimal(str(min_value)):
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.decimal.min_value",
                    {"field": display_name, "min": min_value, "actual": decimal_value}
                )
            )

        # Validação máxima, quando max_value não é um valor padrão (0, 0.0, '', None)
        if max_value is not None and decimal_value > Decimal(str(max_value)):
            raise FieldValidatorException(
                MessageProvider.get_message(
                    "validation.error.decimal.max_value",
                    {"field": display_name, "max": max_value, "actual": decimal_value}
                )
            )
 """