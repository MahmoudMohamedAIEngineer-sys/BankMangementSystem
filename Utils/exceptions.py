class BankError(Exception):
    """Base class for expected application errors."""


class ValidationError(BankError):
    pass


class AuthenticationError(BankError):
    pass


class PermissionDeniedError(BankError):
    pass


class NotFoundError(BankError):
    pass


class DuplicateError(BankError):
    pass


class AccountStateError(BankError):
    pass


class InsufficientFundsError(BankError):
    pass