# biblioteca_base/user_repository.py
from abc import ABC, abstractmethod

class ILoginRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str):
        pass
