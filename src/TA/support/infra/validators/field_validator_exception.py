class FieldValidatorException(Exception):
    @staticmethod
    def when(condition: bool, message: str):
        if condition:
            raise FieldValidatorException(message)