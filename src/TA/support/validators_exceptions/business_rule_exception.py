class BusinessRuleException(Exception):
    @staticmethod
    def when(condition: bool, message: str):
        if condition:
            raise BusinessRuleException(message)