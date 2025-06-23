from TA.support.infra.database.db_handler import DbHandler
from TA.support.infra.db_config.db_config import DbConfig

class BaseController:
    def __init__(self, db_config: DbConfig) -> None:
        self.db = DbHandler(db_config)
        self.db.open()

    def __del__(self):
        self.db.session.invalidate()