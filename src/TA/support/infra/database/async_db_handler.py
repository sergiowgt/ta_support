# src/infra/db_handlers/async_db_handler.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from .idb_handler import IDbHandler
from TA.support.infra.db_config.db_config import DbConfig

class AsyncDbHandler(IDbHandler):
    def __init__(self, db_config: DbConfig):
        self.db_path: str = f"{db_config.driver}://{db_config.user}:{db_config.password}@{db_config.host}/{db_config.db_name}"
        self.db_timout = db_config.timeout
        self.db_echo = db_config.echo.upper() == "TRUE"
        self.engine = None
        self.session_maker = None
        self.session = None

    async def __aenter__(self):
        await self.open()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def open(self) -> None:
        self.engine = create_async_engine(
            self.db_path, 
            echo=self.db_echo,
            pool_timeout=self.db_timout
        )
        self.session_maker = async_sessionmaker(
            self.engine, 
            expire_on_commit=False,
            class_=AsyncSession
        )
        self.session = self.session_maker()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def flush(self):
        await self.session.flush()

    async def close(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def change_schema(self, schema_name: str):
        await self.session.execute(f"SET search_path TO {schema_name}")

    def get_session(self) -> AsyncSession:
        return self.session
