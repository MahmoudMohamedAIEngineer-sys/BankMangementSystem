from Models.Account import Account
from Utils.Constants import Permission, TransactionType
from Models.Transaction import Transactions
from Models.Users import User
from Services.authorization import AuthorizationService
from Services.Storage import Storage
from Utils.exceptions import NotFoundError, ValidationError
from Utils.money import money_to_cents, parse_amount


class TransactionService:

    def __init__(self, store, authorization):
        self.store = store
        self.authorization = authorization

    def _account_or_raise(self, account_number):
        account = self.store.get_account_by_number(account_number.strip())
        if account is None:
            raise NotFoundError("Account was not found.")
        return account

    def _check_access(self, actor, account):
        if self.store.get_user_by_id(actor.user_id) is None:
            raise NotFoundError("Performing user was not found.")
        owner = self.store.get_customer_by_id(account.customer_id)
        self.authorization.require_account_access(actor, account, owner)

    def _check_destination(self, actor, account):
        if self.store.get_user_by_id(actor.user_id) is None:
            raise NotFoundError("Performing user was not found.")
        if actor.is_staff:
            self.authorization.require_permission(actor, Permission.STAFF_FINANCIAL_OPERATIONS)
        else:
            self.authorization.require_permission(actor, Permission.CUSTOMER_SELF_SERVICE)

    def deposit(self, actor, account_number, amount, description=""):
        parsed_amount = parse_amount(amount)
        amount_cents = money_to_cents(parsed_amount)
        account = self._account_or_raise(account_number)
        self._check_access(actor, account)
        account.validate_deposit(parsed_amount)

        account.deposit(parsed_amount)
        return self.store.add_transaction(
            TransactionType.DEPOSIT,
            amount_cents,
            None,
            account.account_id,
            actor.user_id,
            (description or "Simulated deposit").strip(),
        )

    def withdraw(self, actor, account_number, amount, description=""):
        parsed_amount = parse_amount(amount)
        amount_cents = money_to_cents(parsed_amount)
        account = self._account_or_raise(account_number)
        self._check_access(actor, account)
        account.validate_withdrawal(parsed_amount)

        account.withdraw(parsed_amount)
        return self.store.add_transaction(
            TransactionType.WITHDRAWAL,
            amount_cents,
            account.account_id,
            None,
            actor.user_id,
            (description or "Withdrawal").strip(),
        )

    def transfer(self, actor, source_account_number, destination_account_number, amount, description=""):
        parsed_amount = parse_amount(amount)
        amount_cents = money_to_cents(parsed_amount)
        source = self._account_or_raise(source_account_number)
        destination = self._account_or_raise(destination_account_number)

        if source.account_id == destination.account_id:
            raise ValidationError("Source and destination accounts must be different.")

        self._check_access(actor, source)
        self._check_destination(actor, destination)

        source.validate_withdrawal(parsed_amount)
        destination.validate_deposit(parsed_amount)

        source.withdraw(parsed_amount)
        destination.deposit(parsed_amount)
        return self.store.add_transaction(
            TransactionType.TRANSFER,
            amount_cents,
            source.account_id,
            destination.account_id,
            actor.user_id,
            (description or "Account transfer").strip(),
        )

    def history(self, actor, transaction_type=None, account_number=None, search=None, date_text=None):
        if actor.is_staff:
            self.authorization.require_permission(actor, Permission.VIEW_ALL_TRANSACTIONS)
            return self.store.list_transactions(
                transaction_type, account_number, search, date_text
            )

        if account_number:
            account = self._account_or_raise(account_number)
            self._check_access(actor, account)

        if actor.customer_id is None:
            raise NotFoundError("Customer profile was not found.")

        customer = self.store.get_customer_by_id(actor.customer_id)
        if customer is None or not customer.is_active:
            raise ValidationError("The customer profile is inactive.")

        return self.store.list_customer_transactions(
            actor.customer_id,
            transaction_type,
            account_number,
            search,
            date_text,
        )