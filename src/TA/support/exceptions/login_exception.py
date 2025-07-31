class LoginException(Exception):
    @staticmethod
    def when(condition: bool, message: str):
        if condition:
            raise LoginException(message)