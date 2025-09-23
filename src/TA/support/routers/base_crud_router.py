from fastapi import APIRouter, Depends, status, Query, Response
from typing import Type, Union, Callable
from uuid import UUID
from TA.support.JWT.JWT_handler import JWTHandler, JWT_CLAIMS

class BaseCrudRouter:
    def __init__(
        self,
        prefix: str,
        tags: list,
        service_cls: type,
        create_schema: Type,
        update_schema: Type,
        response_schema: Type,
        complete_response_schema: Type,
        create_response_schema: Type,
        get_async_uow: Callable,
    ):
        self.router = APIRouter(
            prefix=prefix,
            tags=tags,
            dependencies=[Depends(JWTHandler.get_claim_dependency(JWT_CLAIMS["EMAIL"]))]
        )

        self.service_cls = service_cls
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.response_schema = response_schema
        self.complete_response_schema = complete_response_schema
        self.create_response_schema = create_response_schema
        self.get_async_uow = get_async_uow
        self.register_routes()

    def register_routes(self):
        @self.router.post("/", response_model=self.create_response_schema, status_code=status.HTTP_201_CREATED)
        async def create(
            create_data: self.create_schema, 
            uow=Depends(self.get_async_uow),
            created_by: str = Depends(JWTHandler.get_claim_dependency(JWT_CLAIMS["EMAIL"]))
        ):
            service = self.service_cls(uow)
            entity = await service.create(create_data, created_by=created_by)
            return self.create_response_schema.model_validate(entity)

        @self.router.get("/{id}", response_model=Union[self.response_schema, self.complete_response_schema])
        async def get(
            id: UUID,
            complete: bool = Query(False, description="Retornar dados completos"),
            uow=Depends(self.get_async_uow)
        ):
            service = self.service_cls(uow)
            entity = await service.get(id)
            if complete:
                return self.complete_response_schema.model_validate(entity)
            return self.response_schema.model_validate(entity)

        @self.router.patch("/{id}/activate")
        async def activate(
            id: UUID, 
            uow=Depends(self.get_async_uow),
            updated_by: str = Depends(JWTHandler.get_claim_dependency(JWT_CLAIMS["EMAIL"]))
        ):
            service = self.service_cls(uow)
            await service.activate(id, updated_by=updated_by)
            return Response(status_code=status.HTTP_200_OK)

        @self.router.patch("/{id}/inactivate")
        async def inactivate(
            id: UUID, 
            uow=Depends(self.get_async_uow),
            updated_by: str = Depends(JWTHandler.get_claim_dependency(JWT_CLAIMS["EMAIL"]))
        ):
            service = self.service_cls(uow)
            await service.inactivate(id, updated_by=updated_by)
            return Response(status_code=status.HTTP_200_OK)

        @self.router.delete("/{id}")
        async def delete(
            id: UUID, 
            uow=Depends(self.get_async_uow),
            updated_by: str = Depends(JWTHandler.get_claim_dependency(JWT_CLAIMS["EMAIL"]))):
            service = self.service_cls(uow)
            await service.delete(id, updated_by=updated_by)
            return Response(status_code=status.HTTP_200_OK)

        @self.router.patch("/{id}")
        async def update(
            id: UUID, 
            update_data: self.update_schema, 
            updated_by: str = Depends(JWTHandler.get_claim_dependency(JWT_CLAIMS["EMAIL"])),
            uow=Depends(self.get_async_uow)
        ):
            service = self.service_cls(uow)
            await service.update(id, update_data, updated_by=updated_by)
            return Response(status_code=status.HTTP_200_OK)
