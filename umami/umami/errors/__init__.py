class ValidationError(Exception):
    pass


class OperationNotAllowedError(ValidationError):
    pass
