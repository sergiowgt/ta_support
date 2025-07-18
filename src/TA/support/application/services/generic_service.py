from datetime import datetime
from typing import Type, List, Optional
from uuid import UUID

from TA.support.application.services.service_utils import validate_uniqueness
from TA.support.domain.contracts.iservice import IService
from TA.support.validators_exceptions import BusinessRuleException
from TA.support.i18n.message_provider import MessageProvider
from TA.support.domain.enums.status_enum import StatusEnum

class GenericService(IService):
    def __init__(self, uow, repo_cls: Type, entity_cls: Type):
        self.uow = uow
        self.repo_cls = repo_cls
        self.entity_cls = entity_cls

    async def _get_entity(self, id: UUID, repo, only_active: bool):
        entity = await repo.get(id, only_active=only_active)
        if not entity:
            msg = MessageProvider.get_message("validation.error.entity_byid_not_found", {
                "entity": self.entity_cls.__entity_name__,
                "value": id
            })
            raise BusinessRuleException(msg)
        return entity

    async def get(self, id: UUID) -> Optional:
        async with self.uow:
            repo = self.repo_cls(self.uow.session)
            return await self._get_entity(id, repo, only_active=True)

    async def list_all(self, only_active: bool = True) -> List:
        async with self.uow:
            repo = self.repo_cls(self.uow.session)
            return await repo.get_all(only_active=only_active)

    async def _execute_insert(self, entity, repo):
        entity.validate()
        await repo.add(entity)
        await self.uow.commit()
        return entity
    
    async def _execute_update(self, entity):
        entity.updated_at = datetime.now()
        entity.validate()
        await self.uow.commit()
    
    async def _validate_childs(self, id: UUID):
        ...
            
    async def _validate_fk(self, id: UUID):
        ...
    
    async def create(self, data, created_by: str):
        async with self.uow:
            repo = self.repo_cls(self.uow.session)

            # valida a unicidade
            await validate_uniqueness(data, self.entity_cls, repo, id=None)

            # Validação das FKs
            await self._validate_fk(data)

            # prepara a entidade para insert
            entity = self.entity_cls(**data.model_dump(), created_by=created_by)

            # insere
            return await self._execute_insert(entity, repo)
        
    async def update(self, id: UUID, data, updated_by: str) -> None:
        async with self.uow:
            repo = self.repo_cls(self.uow.session)
            entity = await self._get_entity(id, repo, only_active=False)

            # Validação de unicidades
            await validate_uniqueness(data, self.entity_cls, repo, id=id)

            # Validação das FKs
            await self._validate_fk(data)

             # Prepara o update
            entity.updated_by = updated_by
            for field, value in data.model_dump().items():
                setattr(entity, field, value)
                 
            # atualiza
            await self._execute_update(entity)
            return 
            
    async def delete(self, id: UUID, updated_by: str) -> None:
        async with self.uow:
            repo = self.repo_cls(self.uow.session)
            entity = await self._get_entity(id, repo, only_active=False)
            if entity.status == StatusEnum.LOGICALLY_DELETED:
                msg = MessageProvider.get_message("validation.error.entity_already_deleted", {
                    "entity": self.entity_cls.__entity_name__,
                    "value": id
                })
                raise BusinessRuleException(msg)
            
            await self._validate_childs(id)
                    
            # prepara a exclusao
            entity.status = StatusEnum.LOGICALLY_DELETED
            entity.updated_by = updated_by

            # exclui
            await self._execute_update(entity)

    async def activate(self, id: UUID, updated_by: str) -> None:
        async with self.uow:
            repo = self.repo_cls(self.uow.session)
            entity = await self._get_entity(id, repo, only_active=False)
            if entity.status == StatusEnum.ACTIVE:
                msg = MessageProvider.get_message("validation.error.entity_already_activate", {
                    "entity": self.entity_cls.__entity_name__,
                    "value": id
                })
                raise BusinessRuleException(msg)
            
            # prepara o activate
            entity.updated_by = updated_by
            entity.status = StatusEnum.ACTIVE
            
            # atualiza
            await self._execute_update(entity)
            
    async def inactivate(self, id: UUID, updated_by: str) -> None:
        async with self.uow:
            repo = self.repo_cls(self.uow.session)
            entity = await self._get_entity(id, repo, only_active=False)
            if entity.status == StatusEnum.INACTIVE:
                msg = MessageProvider.get_message("validation.error.entity_already_inactivate", {
                    "entity": self.entity_cls.__entity_name__,
                    "value": id
                })
                raise BusinessRuleException(msg)
            
            # prepara o inactivate
            entity.updated_by = updated_by
            entity.status = StatusEnum.INACTIVE

            # atualiza
            await self._execute_update(entity)
