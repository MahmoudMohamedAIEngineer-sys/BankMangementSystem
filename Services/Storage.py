from datetime import datetime, timezone
from decimal import Decimal
from Models.Account import Account
from Models.Customer import Customer
from Utils.Constants import AccountStatus, Role
from Models.Transaction import Transactions
from Models.Users import StaffUser, CustomerUser
from Utils.exceptions import DuplicateError, NotFoundError, ValidationError
from Utils.money import cents_to_money, money_to_cents


class Storage:

    def __init__(self):
        self.users = []
        self.customers = []
        self.accounts = []
        self.transactions = []

        self._next_user_id = 1
        self._next_customer_id = 1
        self._next_account_id = 1
        self._next_transaction_id = 1

        self._seed()

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def _seed(self):
        from argon2 import PasswordHasher
        ph = PasswordHasher()

        staff = StaffUser(self._next_user_id, "staff", True, ph.hash("staff123"))
        self.users.append(staff)
        self._next_user_id += 1

        demo_customer = Customer(
            customer_id=self._next_customer_id,
            name="Demo Customer",
            phone="01000000000",
            email="customer@demo.com",
            address="123 Demo Street",
            created_at=self._now()
        )
        self.customers.append(demo_customer)
        self._next_customer_id += 1

        customer_user = CustomerUser(
            self._next_user_id,
            "customer",
            demo_customer.customer_id,
            True,
            ph.hash("customer123")
        )
        self.users.append(customer_user)
        self._next_user_id += 1

        demo_account = Account(
            account_id=self._next_account_id,
            account_number="ACC-DEMO0001",
            customer_id=demo_customer.customer_id,
            account_type="SAVINGS",
            balance=Decimal("1000.00"),
            created_at=self._now()
        )
        self.accounts.append(demo_account)
        self._next_account_id += 1

    def add_user(self, username, password_hash, role, customer_id=None):
        normalized_username = username.strip().lower()

        for user in self.users:
            if user.username.lower() == normalized_username:
                raise DuplicateError("Username already exists.")

        if role == Role.CUSTOMER:
            if customer_id is None:
                raise ValidationError("A customer login must be linked to a customer.")
            if self.get_customer_by_id(customer_id) is None:
                raise NotFoundError("Customer was not found.")
            for user in self.users:
                if user.customer_id == customer_id:
                    raise DuplicateError("This customer already has a login.")
        elif customer_id is not None:
            raise ValidationError("Staff users cannot be linked to customer accounts.")

        user_id = self._next_user_id
        self._next_user_id += 1

        if role == Role.STAFF:
            user = StaffUser(user_id, normalized_username, True, password_hash)
        else:
            user = CustomerUser(user_id, normalized_username, customer_id, True, password_hash)

        self.users.append(user)
        return user

    def get_user_by_id(self, user_id):
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None

    def get_user_by_username(self, username):
        normalized = username.strip().lower()
        for user in self.users:
            if user.username.lower() == normalized:
                return user
        return None

    def get_credentials(self, username):
        user = self.get_user_by_username(username)
        if user is None:
            return None
        return {
            "user_id": user.user_id,
            "password_hash": user.password_hash,
        }

    def set_user_active(self, user_id, is_active):
        user = self.get_user_by_id(user_id)
        if user is None:
            raise NotFoundError("User was not found.")
        user.is_active = is_active

    def list_users(self):
        return sorted(self.users, key=lambda u: u.user_id)

    def add_customer(self, name, phone, email, address):
        for customer in self.customers:
            if customer.email.lower() == email.lower() and customer.is_active:
                raise DuplicateError("A customer with this email already exists.")

        customer = Customer(
            customer_id=self._next_customer_id,
            name=name,
            phone=phone,
            email=email,
            address=address,
            created_at=self._now()
        )
        self._next_customer_id += 1
        self.customers.append(customer)
        return customer

    def get_customer_by_id(self, customer_id):
        for customer in self.customers:
            if customer.customer_id == customer_id:
                return customer
        return None

    def update_customer(self, customer_id, name, phone, email, address):
        customer = self.get_customer_by_id(customer_id)
        if customer is None:
            raise NotFoundError("Customer was not found.")

        for other in self.customers:
            if other.customer_id != customer_id and other.email.lower() == email.lower() and other.is_active:
                raise DuplicateError("A customer with this email already exists.")

        customer.name = name
        customer.phone = phone
        customer.email = email
        customer.address = address
        return customer

    def set_customer_active(self, customer_id, is_active):
        customer = self.get_customer_by_id(customer_id)
        if customer is None:
            raise NotFoundError("Customer was not found.")
        customer.is_active = is_active

    def search_customers(self, query=""):
        query = query.strip().lower()
        matches = []
        for customer in self.customers:
            if not query:
                matches.append(customer)
            elif (
                query in str(customer.customer_id)
                or query in customer.name.lower()
                or query in customer.phone.lower()
                or query in customer.email.lower()
            ):
                matches.append(customer)
        return sorted(matches, key=lambda c: c.customer_id)

    def customer_count(self, active_only=False):
        count = 0
        for customer in self.customers:
            if active_only and not customer.is_active:
                continue
            count += 1
        return count

    def add_account(self, account_number, customer_id, account_type):
        if self.get_customer_by_id(customer_id) is None:
            raise NotFoundError("Customer was not found.")
        if self.get_account_by_number(account_number) is not None:
            raise DuplicateError("Account number already exists.")

        account = Account(
            account_id=self._next_account_id,
            account_number=account_number,
            customer_id=customer_id,
            account_type=account_type,
            created_at=self._now()
        )
        self._next_account_id += 1
        self.accounts.append(account)
        return account

    def get_account_by_id(self, account_id):
        for account in self.accounts:
            if account.account_id == account_id:
                return account
        return None

    def get_account_by_number(self, account_number):
        normalized = account_number.strip().lower()
        for account in self.accounts:
            if account.account_number.lower() == normalized:
                return account
        return None

    def search_accounts(self, query="", status=None, customer_id=None):
        query = query.strip().lower()
        result = []
        for account in self.accounts:
            owner = self.get_customer_by_id(account.customer_id)
            if owner is None:
                continue
            if status and account.status != status:
                continue
            if customer_id is not None and account.customer_id != customer_id:
                continue
            if query:
                searchable = (account.account_number + " " + str(account.customer_id) + " " + owner.name).lower()
                if query not in searchable:
                    continue
            result.append(account)
        return sorted(result, key=lambda a: a.account_id)

    def account_count(self, active_only=False):
        count = 0
        for account in self.accounts:
            if active_only and account.status != AccountStatus.ACTIVE:
                continue
            count += 1
        return count

    def total_balance_for_customer(self, customer_id):
        total_cents = 0
        for account in self.accounts:
            if account.customer_id == customer_id and account.status != AccountStatus.CLOSED:
                total_cents += money_to_cents(account.balance)
        return cents_to_money(total_cents)

    def total_balance(self):
        total_cents = 0
        for account in self.accounts:
            if account.status != AccountStatus.CLOSED:
                total_cents += money_to_cents(account.balance)
        return cents_to_money(total_cents)

    def add_transaction(self, transaction_type, amount_cents, source_account_id, destination_account_id, performed_by_user_id, description):
        performer = self.get_user_by_id(performed_by_user_id)
        if performer is None:
            raise NotFoundError("Performing user was not found.")

        source = self.get_account_by_id(source_account_id) if source_account_id is not None else None
        destination = self.get_account_by_id(destination_account_id) if destination_account_id is not None else None

        if source_account_id is not None and source is None:
            raise NotFoundError("Source account was not found.")
        if destination_account_id is not None and destination is None:
            raise NotFoundError("Destination account was not found.")

        transaction = Transactions(
            transaction_id=self._next_transaction_id,
            transaction_type=transaction_type,
            amount=cents_to_money(amount_cents),
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            performed_by_user_id=performed_by_user_id,
            description=description,
            created_at=self._now(),
            source_account_number=source.account_number if source else None,
            destination_account_number=destination.account_number if destination else None,
            performed_by_username=performer.username
        )
        self._next_transaction_id += 1
        self.transactions.append(transaction)
        return transaction

    def _matches_transaction(self, transaction, transaction_type, account_number, search, date_text):
        if transaction_type and transaction.transaction_type != transaction_type:
            return False
        if account_number:
            if account_number not in {transaction.source_account_number, transaction.destination_account_number}:
                return False
        if date_text:
            if not transaction.created_at.startswith(date_text.strip()):
                return False
        if search:
            search_text = search.strip().lower()
            searchable = (
                transaction.description + " "
                + (transaction.performed_by_username or "") + " "
                + (transaction.source_account_number or "") + " "
                + (transaction.destination_account_number or "")
            ).lower()
            if search_text not in searchable:
                return False
        return True

    def list_transactions(self, transaction_type=None, account_number=None, search=None, date_text=None):
        result = [t for t in self.transactions if self._matches_transaction(t, transaction_type, account_number, search, date_text)]
        return sorted(result, key=lambda t: (t.created_at, t.transaction_id), reverse=True)

    def list_customer_transactions(self, customer_id, transaction_type=None, account_number=None, search=None, date_text=None):
        owned_account_ids = set()
        for account in self.accounts:
            if account.customer_id == customer_id:
                owned_account_ids.add(account.account_id)

        result = []
        for t in self.transactions:
            if t.source_account_id in owned_account_ids or t.destination_account_id in owned_account_ids:
                if self._matches_transaction(t, transaction_type, account_number, search, date_text):
                    result.append(t)
        return sorted(result, key=lambda t: (t.created_at, t.transaction_id), reverse=True)

    def transaction_stats(self):
        result = {
            "DEPOSIT_count": 0,
            "DEPOSIT_total_cents": 0,
            "WITHDRAWAL_count": 0,
            "WITHDRAWAL_total_cents": 0,
            "TRANSFER_count": 0,
            "TRANSFER_total_cents": 0,
        }
        for t in self.transactions:
            kind = t.transaction_type
            result[kind + "_count"] += 1
            result[kind + "_total_cents"] += money_to_cents(t.amount)
        return result

    def transaction_count(self):
        return len(self.transactions)
