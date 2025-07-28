class DomainException(Exception):
    @staticmethod
    def when(condition: bool, message: str):
        if condition:
            raise DomainException(message)