# TA/support/domain/entities/base_entity.py
#
# MUDANÇAS:
#   - Adicionado DeclarativeBase e MappedAsDataclass na herança
#   - Campos trocados de dataclass.field() para mapped_column()
#   - metadata= preservado em cada campo (SQLAlchemy 2.0 suporta)
#   - validate(), _get_display_name(), call_default_validators() — inalterados
#   - dataclasses.fields() continua funcionando (MappedAsDataclass é compatível)
#
# O QUE ISSO ELIMINA nos projetos que usam a TA.support:
#   - Arquivos _database_schema.py separados
#   - orm_mapper.py com map_imperatively manual
#   - start_mappers() espalhado pelo projeto
#
# COMO USAR nas entidades filhas:
#   @dataclass
#   class Dentist(NamedBaseEntity):
#       __tablename__ = "dentist"
#
#       cpf: Mapped[str] = mapped_column(CHAR(11), nullable=False,
#           metadata={'display': 'CPF', 'required': True, 'field_config': CPF_FIELD})

from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, VARCHAR, func
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column, Mapped

from TA.support.infra.orm.type_decorators import UUIDType
from TA.support.infra.validators.field_presets import (
    DATED_BY_FIELD, DATED_AT_FIELD, STATUS_FIELD, UUID_FIELD,
)
from TA.support.infra.validators.field_validator import FieldValidator
from TA.support.infra.validators.fields import (
    DateFieldConfig, DateTimeFieldConfig, DecimalFieldConfig,
    IntFieldConfig, JsonFieldConfig, StrFieldConfig, BoolFieldConfig,
)
from TA.support.domain.enums.status_enum import StatusEnum
from TA.support.infra.validators.fields.time_field_config import TimeFieldConfig


class _DeclarativeBase(DeclarativeBase):
    """Registry declarativo interno — não usar diretamente."""
    pass


class BaseEntity(MappedAsDataclass, _DeclarativeBase, init=False):
    """
    Base para todas as entidades do domínio.

    Combina:
      - MappedAsDataclass: campos são lidos como @dataclass pelo SQLAlchemy
      - DeclarativeBase: registra automaticamente no metadata ao definir __tablename__
      - validate(), _get_display_name(): lógica de domínio preservada

    As entidades filhas só precisam declarar __tablename__ e seus próprios campos.
    Nenhum mapper externo, nenhum arquivo de schema separado.
    """
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        UUIDType(), primary_key=True, default_factory=uuid4, init=False,
        metadata={'field_config': UUID_FIELD, 'display': 'UUID'}
    )
    status: Mapped[int] = mapped_column(
        Integer, nullable=False, init=False, default=StatusEnum.ACTIVE.value,
        metadata={'field_config': STATUS_FIELD, 'display': 'Status', 'required': True}
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, init=False,
        default_factory=datetime.now,
        metadata={'field_config': DATED_AT_FIELD, 'display': 'CreatedAt', 'required': True}
    )
    created_by: Mapped[str] = mapped_column(
        VARCHAR(DATED_BY_FIELD.max_len), nullable=False, init=False, default='',
        metadata={'field_config': DATED_BY_FIELD, 'display': 'CreatedBy', 'required': True}
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, init=False, default=None,
        metadata={'field_config': DATED_AT_FIELD, 'display': 'UpdatedAt'}
    )
    updated_by: Mapped[Optional[str]] = mapped_column(
        VARCHAR(DATED_BY_FIELD.max_len), nullable=True, init=False, default=None,
        metadata={'field_config': DATED_BY_FIELD, 'display': 'UpdatedBy'}
    )

    # ── Lógica de domínio — inalterada ───────────────────────────────────────

    def _get_display_name(self, property_name: str) -> str:
        for f in fields(self):
            if f.name == property_name:
                return f.metadata.get('display', property_name)
        return property_name

    def _get_metadata_info(self, metadata, field_name):
        display_name = metadata.get("display", field_name)
        required = metadata.get("required", False)
        value = getattr(self, field_name)
        return display_name, required, value

    def call_default_validators(self, field_config, display_name, value):
        if isinstance(field_config, StrFieldConfig):
            FieldValidator.validate_string(value, display_name, field_config)
        elif isinstance(field_config, IntFieldConfig):
            FieldValidator.validate_integer(value, display_name, field_config)
        elif isinstance(field_config, DecimalFieldConfig):
            FieldValidator.validate_decimal(value, display_name, field_config)
        elif isinstance(field_config, DateTimeFieldConfig):
            FieldValidator.validate_datetime(value, display_name, field_config)
        elif isinstance(field_config, BoolFieldConfig):
            FieldValidator.validate_bool(value, display_name, field_config)
        elif isinstance(field_config, TimeFieldConfig):
            FieldValidator.validate_time(value, display_name, field_config)
        elif isinstance(field_config, DateFieldConfig):
            FieldValidator.validate_date(value, display_name, field_config)
        elif isinstance(field_config, JsonFieldConfig):
            FieldValidator.validate_json(value, display_name, field_config)

    def validate(self):
        for f in fields(self):
            display_name, required, value = self._get_metadata_info(f.metadata, f.name)
            if not required and not value:
                continue

            field_config = f.metadata.get("field_config")
            validator_fn = getattr(field_config, "validator", None) if field_config else None
            if callable(validator_fn):
                validator_fn(value, display_name, field_config)
                continue

            if required:
                self.call_default_validators(field_config, display_name, value)

        if self.updated_at:
            FieldValidator.validate_datetime(self.updated_at, self._get_display_name('updated_at'), DATED_AT_FIELD)
            FieldValidator.validate_string(self.updated_by, self._get_display_name('updated_by'), DATED_BY_FIELD)

        if self.updated_by:
            FieldValidator.validate_string(self.updated_by, self._get_display_name('updated_by'), DATED_BY_FIELD)
            FieldValidator.validate_datetime(self.updated_at, self._get_display_name('updated_at'), DATED_AT_FIELD)