from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .idb_handler import IDbHandler
from TA.support.infra.db_config.db_config import DbConfig

class DbHandler(IDbHandler):
    session: Session = None

    def __init__(self, db_config: DbConfig):
        self.db_path: str=f"{db_config.driver}://{db_config.user}:{db_config.password}@{db_config.host}/{db_config.db_name}"
        print(self.db_path)
        self.db_timout = db_config.timeout
        self.db_echo = db_config.echo.upper() == "TRUE"

    def get_session(self) -> Session:
        return self.session

    def commit(self):
        self.session.commit()

    def flush(self):
        self.session.flush()

    def close(self) -> None:
        #self.session.close()
        #self.engine.dispose(close=True)
        ...

    def open(self) -> None:
        self.engine = create_engine(self.db_path, echo=self.db_echo)
        self.session_maker = sessionmaker()
        self.session = self.session_maker(bind=self.engine)