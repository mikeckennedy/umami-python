## errors.ValidationError


Base exception raised when an input or argument fails validation.


Usage

``` python
errors.ValidationError()
```


The SDK raises this (or its subclass OperationNotAllowedError) for invalid or malformed inputs before any network request is made. Examples include an empty or non-HTTP url_base, an invalid distinct_id, a negative or non-numeric revenue amount, an empty currency, empty login credentials, and an invalid Cloud API key or region.

Because OperationNotAllowedError subclasses this type, catching ValidationError also catches missing-state errors.
