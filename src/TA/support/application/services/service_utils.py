from dataclasses import fields
from TA.support.application.exceptions.business_rule_exception import BusinessRuleException
from TA.support.domain.enums.unique_type_enum import UniqueType
from TA.support.i18n.message_provider import MessageProvider
from sqlalchemy import select

async def validate_uniqueness(data, entity_cls, repo, id=None):
    async def handle_field_only():
        get_by_method = getattr(repo, f"get_by_{f.name}", None)
        if get_by_method:
            existing = await get_by_method(value)
            if existing and (id is None or existing.id != id):
                msg = MessageProvider.get_message(
                    "validation.error.duplicated_field",
                    {
                        "entity": entity_cls.__entity_name__,
                        "field": meta.get('display', f.name),
                        "value": value
                    }
                )
                raise BusinessRuleException(msg)

    async def handle_field_and_id():
        get_by_method = getattr(repo, f"get_by_id_and_{f.name}", None)
        if get_by_method:
            existing = await get_by_method(id, value)
            if existing and (id is None or existing.id != id):
                msg = MessageProvider.get_message(
                    "validation.error.duplicated_field",
                    {
                        "entity": entity_cls.__entity_name__,
                        "field": meta.get('display', f.name),
                        "value": value
                    }
                )
                raise BusinessRuleException(msg)


    for f in fields(entity_cls):
        meta = f.metadata
        unique_type = meta.get('unique_type', UniqueType.FALSE)

        if unique_type == UniqueType.FALSE:
            continue  

        value = getattr(data, f.name)
        if unique_type == UniqueType.FIELD_ONLY:
            handle_field_only()
           
        elif unique_type == UniqueType.FIELD_PLUS_ID:
            handle_field_and_id()
            

async def validate_foreign_keys(data, entity_cls, repo_registry, session):
    for f in fields(entity_cls):
        meta = f.metadata
        if 'foreign_model' in meta:
            fk_value = getattr(data, f.name)
            if fk_value is not None:
                fk_repo = repo_registry[meta['foreign_model']](session)
                exists = await fk_repo.exists(fk_value)
                if not exists:
                    msg = MessageProvider.get_message(
                        "validation.error.entity_byid_not_found",
                        {
                            "entity": meta.get('display', meta['foreign_model']),
                            "value": fk_value
                        }
                    )
                    raise BusinessRuleException(msg)
                
async def has_children(session, entity_cls, entity_id, repo_registry):
    for child in getattr(entity_cls, "__children__", []):
        child_cls = repo_registry[child["entity"]].entity_cls
        fk_field = child["fk_field"]
        result = await session.execute(
            select(child_cls).where(getattr(child_cls, fk_field) == entity_id)
        )
        if result.scalars().first():
            msg = MessageProvider.get_message(
                "validation.error.entity_has_dependencies",
                {
                    "entity": getattr(entity_cls, "__display__", entity_cls.__name__),
                    "value": entity_id,
                    "dependent": child["display"]
                }
            )
            raise BusinessRuleException(msg)
    return False
