from abc import ABC
from typing import Any

class IDbHandler(ABC):
    def __enter__(self):
        raise Exception("Not Implemented")

    def get_session(self)->Any:
        raise Exception("Not Implemented")

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise Exception("Not Implemented")

    def commit(self):
        raise Exception("Not Implemented")


    def change_schema(self, from_, to_):
        raise Exception("Not Implemented")