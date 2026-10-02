import secrets
from Utils.Constants import Permission, Role
from Services.authentication_services import hash_password
from Utils.exceptions import DuplicateError, NotFoundError, ValidationError
from Utils.money import cents_to_money
from Utils.Validators import (
    required,
    validate_account_type,
    validate_email,
    validate_password,
    Validate_Phone,
    validate_username,
)


class BankService:
    def __init__(self, storage, authorization_service):
        self.storage = storage
        self.authorization_service = authorization_service

    def _customer_or_raise(self, customer_id):
        customer = self.storage.get_customer_by_id(customer_id)
        if customer is None:
            raise NotFoundError("Customer was not found.")
        return customer

    def _account_or_raise(self, account_number):
        account = self.storage.get_account_by_number(account_number)
        if account is None:
            raise NotFoundError("Account was not found.")
        return account

    def _new_account_number(self):
        for _ in range(10):
            candidate = f"ACC-{secrets.token_hex(5).upper()}"
            if self.storage.get_account_by_number(candidate) is None:
                return candidate
        raise DuplicateError("Could not generate a unique account number.")

    def create_customer(self, actor, name, phone, email, address):
        self.authorization_service.require_staff(actor, Permission.MANAGE_CUSTOMERS)
        name = required(name, "Name")
        phone = Validate_Phone(phone)
        email = validate_email(email)
        address = (address or "").strip()
        return self.storage.add_customer(name, phone, email, address)

    def update_customer(self, actor, customer_id, name, phone, email, address):
        self.authorization_service.require_staff(actor, Permission.MANAGE_CUSTOMERS)
        self._customer_or_raise(customer_id)
        name = required(name, "Name")
        phone = Validate_Phone(phone)
        email = validate_email(email)
        address = (address or "").strip()
        return self.storage.update_customer(customer_id, name, phone, email, address)

    def deactivate_customer(self, actor, customer_id):
        self.authorization_service.require_staff(actor, Permission.MANAGE_CUSTOMERS)
        self._customer_or_raise(customer_id)
        return self.storage.set_customer_active(customer_id, False)

    def activate_customer(self, actor, customer_id):
        self.authorization_service.require_staff(actor, Permission.MANAGE_CUSTOMERS)
        self._customer_or_raise(customer_id)
        return self.storage.set_customer_active(customer_id, True)

    def search_customers(self, actor, query=""):
        self.authorization_service.require_staff(actor, Permission.MANAGE_CUSTOMERS)
        return self.storage.search_customers(query)

    def get_customer_for_actor(self, actor):
        if actor.customer_id is None:
            raise NotFoundError("This user does not have a linked customer profile.")
        customer = self._customer_or_raise(actor.customer_id)
        self.authorization_service.require_customer_profile(actor, customer)
        return customer

    def create_account(self, actor, customer_id, account_type):
        self.authorization_service.require_staff(actor, Permission.CREATE_ACCOUNTS)
        customer = self._customer_or_raise(customer_id)
        if not customer.is_active:
            raise ValidationError("An inactive customer cannot receive a new account.")
        validated_type = validate_account_type(account_type)
        return self.storage.add_account(self._new_account_number(), customer_id, validated_type)

    def search_accounts(self, actor, query="", status=None):
        if actor.is_staff:
            self.authorization_service.require_permission(actor, Permission.VIEW_ALL_ACCOUNTS)
            return self.storage.search_accounts(query, status=status)
        customer = self.get_customer_for_actor(actor)
        return self.storage.search_accounts(query, status=status, customer_id=customer.customer_id)

    def freeze_account(self, actor, account_number):
        self.authorization_service.require_staff(actor, Permission.MANAGE_ACCOUNT_STATUS)
        account = self._account_or_raise(account_number)
        account.freeze()

    def activate_account(self, actor, account_number):
        self.authorization_service.require_staff(actor, Permission.MANAGE_ACCOUNT_STATUS)
        account = self._account_or_raise(account_number)
        account.activate()

    def close_account(self, actor, account_number):
        self.authorization_service.require_staff(actor, Permission.MANAGE_ACCOUNT_STATUS)
        account = self._account_or_raise(account_number)
        account.close()

    def create_staff_user(self, actor, username, password):
        self.authorization_service.require_staff(actor, Permission.MANAGE_USERS)
        username = validate_username(username)
        password = validate_password(password)
        return self.storage.add_user(username, hash_password(password), Role.STAFF)

    def create_customer_login(self, actor, username, password, customer_id):
        self.authorization_service.require_staff(actor, Permission.MANAGE_USERS)
        customer = self._customer_or_raise(customer_id)
        if not customer.is_active:
            raise ValidationError("An inactive customer cannot receive a login.")
        username = validate_username(username)
        password = validate_password(password)
        return self.storage.add_user(username, hash_password(password), Role.CUSTOMER, customer_id)

    def deactivate_user(self, actor, user_id):
        self.authorization_service.require_staff(actor, Permission.MANAGE_USERS)
        target = self.storage.get_user_by_id(user_id)
        if target is None:
            raise NotFoundError("User was not found.")
        if target.user_id == actor.user_id:
            raise ValidationError("You cannot deactivate your own active session.")
        self.storage.set_user_active(user_id, False)

    def activate_user(self, actor, user_id):
        self.authorization_service.require_staff(actor, Permission.MANAGE_USERS)
        target = self.storage.get_user_by_id(user_id)
        if target is None:
            raise NotFoundError("User was not found.")
        self.storage.set_user_active(user_id, True)

    def list_users(self, actor):
        self.authorization_service.require_staff(actor, Permission.MANAGE_USERS)
        return self.storage.list_users()

    def system_statistics(self, actor):
        self.authorization_service.require_staff(actor, Permission.VIEW_SYSTEM_STATISTICS)
        transaction_stats = self.storage.transaction_stats()
        return {
            "total_customers": self.storage.customer_count(),
            "active_customers": self.storage.customer_count(active_only=True),
            "total_accounts": self.storage.account_count(),
            "active_accounts": self.storage.account_count(active_only=True),
            "total_transactions": self.storage.transaction_count(),
            "total_balance": self.storage.total_balance(),
            "total_deposits": cents_to_money(transaction_stats["DEPOSIT_total_cents"]),
            "total_withdrawals": cents_to_money(transaction_stats["WITHDRAWAL_total_cents"]),
            "total_transfers": cents_to_money(transaction_stats["TRANSFER_total_cents"]),
        }

    def customer_statistics(self, actor):
        customer = self.get_customer_for_actor(actor)
        accounts = self.storage.search_accounts(customer_id=customer.customer_id)
        return {
            "customer": customer,
            "accounts": accounts,
            "total_balance": self.storage.total_balance_for_customer(customer.customer_id),
        }
