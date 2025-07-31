from pathlib import Path
import pytest
from datetime import datetime
from TA.support.domain.entities.base_entity import BaseEntity
from TA.support.domain.enums.status_enum import StatusEnum
from TA.support.exceptions.field_validator_exception import FieldValidatorException
from TA.support.i18n.message_provider import MessageProvider

class TestBaseEntity:
    @classmethod
    def setup_class(cls): 
        MessageProvider._load_locales(Path('/Users/sergiosousa/work/Lab/DentalInclusiva/src/locales'))

    def setup_method(self): MessageProvider.set_language("pt_BR")

    def test_created_by_empty(self):
        with pytest.raises(FieldValidatorException) as exc: BaseEntity( status=StatusEnum.ACTIVE, created_at=datetime.now(), created_by="").validate()
        assert MessageProvider.get_message("validation.error.empty_field", {"field": "CreatedBy"}) in str(exc.value)

    def test_created_at_empty(self):
        with pytest.raises(FieldValidatorException) as exc: BaseEntity( status=StatusEnum.ACTIVE, created_by="xxx", created_at=None).validate()
        assert MessageProvider.get_message("validation.error.empty_field", {"field": "CreatedAt"}) in str(exc.value)

    def test_created_at_invalid(self):
        with pytest.raises(FieldValidatorException) as exc: BaseEntity( status=StatusEnum.ACTIVE, created_by="xxx", created_at="1234").validate()
        assert MessageProvider.get_message("validation.error.invalid_datetime", {"field": "CreatedAt"}) in str(exc.value)

    def test_updated_by_without_updated_at(self):
        with pytest.raises(FieldValidatorException) as exc: BaseEntity(status=StatusEnum.ACTIVE, created_at=datetime.now(), created_by="admin", updated_by="user").validate()
        assert MessageProvider.get_message("validation.error.empty_field", {"field": "UpdatedAt"}) in str(exc.value)

    def test_updated_by_invalid_updated_at(self):
        with pytest.raises(FieldValidatorException) as exc: BaseEntity(status=StatusEnum.ACTIVE, created_at=datetime.now(), created_by="admin", updated_by="user", updated_at="123").validate()
        assert MessageProvider.get_message("validation.error.invalid_datetime", {"field": "UpdatedAt"}) in str(exc.value)

    def test_updated_at_without_updated_by(self):
        with pytest.raises(FieldValidatorException) as exc: BaseEntity(status=StatusEnum.ACTIVE, created_at=datetime.now(), created_by="admin", updated_at=datetime.now()).validate()
        assert MessageProvider.get_message("validation.error.empty_field", {"field": "UpdatedBy"}) in str(exc.value)

    def test_without_updated_by_and_without_updated_at(self):
        with pytest.raises(FieldValidatorException) as exc: 
            BaseEntity(status=StatusEnum.ACTIVE, created_at=datetime.now(), created_by="admin", updated_by="teste").validate()
        assert MessageProvider.get_message("validation.error.empty_field", {"field": "UpdatedAt"}) in str(exc.value)

    def test_valid(self):
        BaseEntity(status=StatusEnum.ACTIVE, created_at=datetime.now(), created_by="admin", updated_at=datetime.now(), updated_by="xxx").validate()
