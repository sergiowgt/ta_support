from pathlib import Path
import pytest
from datetime import datetime
from TA.support.domain.entities.base_config_atributtes import NAME_FIELD
from TA.support.domain.entities.named_base_entity import NamedBaseEntity
from TA.support.validators_exceptions.domain_exception import DomainException
from TA.support.i18n.message_provider import MessageProvider

class TestNamedBaseEntity:
    @classmethod
    def setup_class(cls): 
        MessageProvider._load_locales(Path('/Users/sergiosousa/TA.support/locales'))
        
    def setup_method(self): MessageProvider.set_language("pt_BR")

    def test_valid_name(self):
        NamedBaseEntity(name="Paciente X", created_by="admin", created_at=datetime.now()).validate()

    def test_empty_name(self):
        with pytest.raises(DomainException) as exc:
            NamedBaseEntity(name="", created_by="admin", created_at=datetime.now()).validate()
        assert MessageProvider.get_message("validation.error.empty_field", {"field": "Name"}) in str(exc.value)

    def test_name_too_long(self):
        with pytest.raises(DomainException) as exc:
            NamedBaseEntity(name="A"*101, created_by="admin", created_at=datetime.now()).validate()
        assert MessageProvider.get_message("validation.error.max_length", {"field": "Name", "max": NAME_FIELD.max}) in str(exc.value)
