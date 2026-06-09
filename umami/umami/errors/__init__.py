class ValidationError(Exception):
    """
    Base exception raised when an input or argument fails validation.

    The SDK raises this (or its subclass OperationNotAllowedError) for invalid
    or malformed inputs before any network request is made. Examples include an
    empty or non-HTTP url_base, an invalid distinct_id, a negative or
    non-numeric revenue amount, an empty currency, empty login credentials, and
    an invalid Cloud API key or region.

    Because OperationNotAllowedError subclasses this type, catching
    ValidationError also catches missing-state errors.
    """

    pass


class OperationNotAllowedError(ValidationError):
    """
    Raised when the SDK is missing required state for an operation.

    A subclass of ValidationError. It signals that prerequisite configuration
    has not been completed, for example calling an operation before
    set_url_base() in self-hosted mode, querying data before login(), or
    calling login() while a Cloud API key is configured (login() is not used in
    Cloud mode).

    Resolve it by calling the appropriate setup function first: set_url_base()
    and login() for self-hosted mode, or set_cloud_api_key() for Umami Cloud.
    """

    pass
