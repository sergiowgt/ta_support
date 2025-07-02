# src/infra/orm/unit_of_work.py
from sqlalchemy.ext.asyncio import AsyncSession
from TA.support.domain.contracts.unit_of_work import IUnitOfWork
from TA.support.infra.database.async_db_handler import AsyncDbHandler

class AsyncSqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, db_handler: AsyncDbHandler):
        self.db_handler = db_handler
        self.session: AsyncSession = None

    async def __aenter__(self):
        await self.db_handler.open()
        self.session = self.db_handler.session
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.db_handler.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
