from datetime import datetime, timezone
from decimal import Decimal
from Utils.Constants import AccountStatus
from Utils.exceptions import AccountStateError, InsufficientFundsError, ValidationError


class Account:
    def __init__(self, account_id, account_number, customer_id, account_type, balance=Decimal("0.00"), status=AccountStatus.ACTIVE, created_at=None, closed_at=None):
        self.account_id = account_id
        self.account_number = account_number
        self.customer_id = customer_id
        self.account_type = account_type
        self.__balance = balance
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.closed_at = closed_at

        if self.__balance < Decimal("0.00"):
            raise ValidationError("Account balance cannot be negative.")

    @property
    def balance(self):
        return self.__balance

    @property
    def can_transact(self):
        return self.status == AccountStatus.ACTIVE

    def _validate_amount(self, amount):
        if amount <= Decimal("0.00"):
            raise ValidationError("Amount must be greater than zero.")

    def _validate_permissions(self):
        if self.status == AccountStatus.FROZEN:
            raise AccountStateError("Account is frozen. Financial operations are not allowed.")
        if self.status == AccountStatus.CLOSED:
            raise AccountStateError("Account is closed. Financial operations are not allowed.")

    def validate_deposit(self, amount):
        self._validate_amount(amount)
        self._validate_permissions()

    def validate_withdrawal(self, amount):
        self._validate_amount(amount)
        self._validate_permissions()
        if self.__balance < amount:
            raise InsufficientFundsError("Insufficient funds.")

    def deposit(self, amount):
        self._validate_amount(amount)
        self._validate_permissions()
        self.__balance += amount

    def withdraw(self, amount):
        self._validate_amount(amount)
        self._validate_permissions()
        if self.__balance < amount:
            raise InsufficientFundsError("Insufficient funds.")
        self.__balance -= amount

    def freeze(self):
        if self.status == AccountStatus.CLOSED:
            raise AccountStateError("A closed account cannot be frozen.")
        if self.status == AccountStatus.FROZEN:
            raise AccountStateError("Account is already frozen.")
        self.status = AccountStatus.FROZEN

    def close(self):
        if self.status == AccountStatus.CLOSED:
            raise AccountStateError("Account is already closed.")
        if self.__balance != Decimal("0.00"):
            raise AccountStateError("Account can only be closed when its balance is zero.")
        self.status = AccountStatus.CLOSED
        self.closed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def activate(self):
        if self.status == AccountStatus.CLOSED:
            raise AccountStateError("A closed account cannot be activated.")
        if self.status == AccountStatus.ACTIVE:
            raise AccountStateError("Account is already active.")
        self.status = AccountStatus.ACTIVE
