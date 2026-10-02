import logging
from PySide6.QtCore import Property, QObject, Signal, Slot

from Models.Users import User
from Services.authentication_services import AuthenticationService
from Services.authorization import AuthorizationService
from Services.bank_services import BankService
from Services.Transaction_service import TransactionService
from Utils.exceptions import BankError, PermissionDeniedError
from Utils.money import format_money

logger = logging.getLogger(__name__)


class AppController(QObject):
    loggedInChanged = Signal()
    loggedOut = Signal()
    currentPageChanged = Signal()
    messageChanged = Signal()
    dataChanged = Signal()
    loginSucceeded = Signal()
    errorOccurred = Signal(str)
    successOccurred = Signal(str)

    def __init__(self, authentication_service, authorization_service, bank_service, transaction_service):
        super().__init__()
        self.authentication_service = authentication_service
        self.authorization_service = authorization_service
        self.bank_service = bank_service
        self.transaction_service = transaction_service
        self._user = None
        self._current_page = "dashboard"
        self._last_error = ""
        self._last_success = ""

    def _require_user(self):
        if self._user is None:
            raise PermissionDeniedError("Please log in first.")
        return self._user

    def _set_error(self, message):
        self._last_error = message
        self._last_success = ""
        self.messageChanged.emit()
        self.errorOccurred.emit(message)

    def _set_success(self, message):
        self._last_success = message
        self._last_error = ""
        self.messageChanged.emit()
        self.successOccurred.emit(message)

    def _run(self, action, success_message=None):
        try:
            result = action()
            if success_message:
                self._set_success(success_message)
            return result
        except BankError as exc:
            self._set_error(str(exc))
            return None
        except Exception:
            logger.exception("Unexpected application error")
            self._set_error("An unexpected error occurred. Please try again.")
            return None

    def _run_success(self, action, success_message):
        try:
            action()
            self._set_success(success_message)
            return True
        except BankError as exc:
            self._set_error(str(exc))
            return False
        except Exception:
            logger.exception("Unexpected application error")
            self._set_error("An unexpected error occurred. Please try again.")
            return False

    @staticmethod
    def _customer_dict(customer):
        return {
            "id": customer.customer_id,
            "name": customer.name,
            "phone": customer.phone,
            "email": customer.email,
            "address": customer.address,
            "isActive": customer.is_active,
            "status": "ACTIVE" if customer.is_active else "INACTIVE",
            "createdAt": customer.created_at,
        }

    @staticmethod
    def _account_dict(account):
        return {
            "id": account.account_id,
            "accountNumber": account.account_number,
            "customerId": account.customer_id,
            "accountType": account.account_type,
            "balance": format_money(account.balance),
            "balanceValue": float(account.balance),
            "status": account.status,
            "createdAt": account.created_at,
            "closedAt": account.closed_at or "",
        }

    @staticmethod
    def _transaction_dict(transaction):
        return {
            "id": transaction.transaction_id,
            "type": transaction.transaction_type,
            "amount": format_money(transaction.amount),
            "source": transaction.source_account_number or "—",
            "destination": transaction.destination_account_number or "—",
            "performedBy": transaction.performed_by_username or "—",
            "description": transaction.description,
            "createdAt": transaction.created_at,
        }

    @staticmethod
    def _user_dict(user):
        return {
            "id": user.user_id,
            "username": user.username,
            "role": user.role,
            "customerId": str(user.customer_id) if user.customer_id else "",
            "isActive": user.is_active,
            "status": "ACTIVE" if user.is_active else "INACTIVE",
        }

    @Property(bool, notify=loggedInChanged)
    def loggedIn(self):
        return self._user is not None

    @Property(str, notify=loggedInChanged)
    def username(self):
        return self._user.username if self._user else ""

    @Property(str, notify=loggedInChanged)
    def role(self):
        return self._user.role if self._user else ""

    @Property(bool, notify=loggedInChanged)
    def isStaff(self):
        return bool(self._user and self._user.is_staff)

    @Property(str, notify=currentPageChanged)
    def currentPage(self):
        return self._current_page

    @Property(str, notify=messageChanged)
    def lastError(self):
        return self._last_error

    @Property(str, notify=messageChanged)
    def lastSuccess(self):
        return self._last_success

    @Property("QVariantList", notify=loggedInChanged)
    def availablePages(self):
        if not self._user:
            return []
        if self._user.is_staff:
            return ["dashboard", "customers", "accounts", "transactions", "users"]
        return ["dashboard", "accounts", "transactions"]

    @Slot(str, str, result=bool)
    def login(self, username, password):
        self.clearMessage()
        user = self._run(
            lambda: self.authentication_service.authenticate(username, password)
        )
        if user is None:
            return False
        self._user = user
        self._current_page = "dashboard"
        self.loggedInChanged.emit()
        self.currentPageChanged.emit()
        self.loginSucceeded.emit()
        self.dataChanged.emit()
        return True

    @Slot(result=bool)
    def logout(self):
        self._user = None
        self._current_page = "dashboard"
        self.clearMessage()
        self.loggedOut.emit()
        self.loggedInChanged.emit()
        self.currentPageChanged.emit()
        self.dataChanged.emit()
        return True

    @Slot(str, result=bool)
    def navigate(self, page):
        if page not in self.availablePages:
            self._set_error("You are not authorized to open that page.")
            return False
        self._current_page = page
        self.currentPageChanged.emit()
        self.clearMessage()
        return True

    @Slot(result="QVariant")
    def dashboardData(self):
        user = self._require_user()
        if user.is_staff:
            statistics = self.bank_service.system_statistics(user)
            recent = self.transaction_service.history(user)[:8]
            return {
                "scope": "SYSTEM",
                "username": user.username,
                "role": user.role,
                "totalCustomers": statistics["total_customers"],
                "activeCustomers": statistics["active_customers"],
                "totalAccounts": statistics["total_accounts"],
                "activeAccounts": statistics["active_accounts"],
                "totalTransactions": statistics["total_transactions"],
                "totalBalance": format_money(statistics["total_balance"]),
                "totalDeposits": format_money(statistics["total_deposits"]),
                "totalWithdrawals": format_money(statistics["total_withdrawals"]),
                "totalTransfers": format_money(statistics["total_transfers"]),
                "recentTransactions": [self._transaction_dict(item) for item in recent],
            }

        statistics = self.bank_service.customer_statistics(user)
        recent = self.transaction_service.history(user)[:8]
        customer = statistics["customer"]
        accounts = statistics["accounts"]
        return {
            "scope": "PERSONAL",
            "username": user.username,
            "role": user.role,
            "customerName": customer.name,
            "totalBalance": format_money(statistics["total_balance"]),
            "totalAccounts": len(accounts),
            "activeAccounts": sum(1 for account in accounts if account.can_transact),
            "accounts": [self._account_dict(account) for account in accounts],
            "recentTransactions": [self._transaction_dict(item) for item in recent],
        }

    @Slot(str, result="QVariant")
    def customers(self, query=""):
        user = self._require_user()
        result = self._run(lambda: self.bank_service.search_customers(user, query))
        if result is None:
            return []
        return [self._customer_dict(item) for item in result]

    @Slot(str, str, str, str, result=bool)
    def createCustomer(self, name, phone, email, address):
        user = self._require_user()
        result = self._run(
            lambda: self.bank_service.create_customer(user, name, phone, email, address),
            "Customer created successfully.",
        )
        if result is not None:
            self.dataChanged.emit()
            return True
        return False

    @Slot(int, str, str, str, str, result=bool)
    def updateCustomer(self, customer_id, name, phone, email, address):
        user = self._require_user()
        result = self._run(
            lambda: self.bank_service.update_customer(user, customer_id, name, phone, email, address),
            "Customer updated successfully.",
        )
        if result is not None:
            self.dataChanged.emit()
            return True
        return False

    @Slot(int, result=bool)
    def deactivateCustomer(self, customer_id):
        user = self._require_user()
        success = self._run_success(
            lambda: self.bank_service.deactivate_customer(user, customer_id),
            "Customer deactivated successfully.",
        )
        if success:
            self.dataChanged.emit()
        return success

    @Slot(int, result=bool)
    def activateCustomer(self, customer_id):
        user = self._require_user()
        success = self._run_success(
            lambda: self.bank_service.activate_customer(user, customer_id),
            "Customer activated successfully.",
        )
        if success:
            self.dataChanged.emit()
        return success

    @Slot(str, str, result="QVariant")
    def accounts(self, query="", status=""):
        user = self._require_user()
        result = self._run(
            lambda: self.bank_service.search_accounts(user, query, status or None)
        )
        if result is None:
            return []
        return [self._account_dict(item) for item in result]

    @Slot(int, str, result=bool)
    def createAccount(self, customer_id, account_type):
        user = self._require_user()
        result = self._run(
            lambda: self.bank_service.create_account(user, customer_id, account_type),
            "Account created successfully.",
        )
        if result is not None:
            self.dataChanged.emit()
            return True
        return False

    @Slot(str, result=bool)
    def freezeAccount(self, account_number):
        user = self._require_user()
        success = self._run_success(
            lambda: self.bank_service.freeze_account(user, account_number),
            "Account frozen successfully.",
        )
        if success:
            self.dataChanged.emit()
        return success

    @Slot(str, result=bool)
    def activateAccount(self, account_number):
        user = self._require_user()
        success = self._run_success(
            lambda: self.bank_service.activate_account(user, account_number),
            "Account activated successfully.",
        )
        if success:
            self.dataChanged.emit()
        return success

    @Slot(str, result=bool)
    def closeAccount(self, account_number):
        user = self._require_user()
        success = self._run_success(
            lambda: self.bank_service.close_account(user, account_number),
            "Account closed successfully.",
        )
        if success:
            self.dataChanged.emit()
        return success

    @Slot(str, str, str, str, result="QVariant")
    def transactions(self, transaction_type="", account_number="", search="", date_text=""):
        user = self._require_user()
        result = self._run(
            lambda: self.transaction_service.history(
                user,
                transaction_type or None,
                account_number.strip() or None,
                search.strip() or None,
                date_text.strip() or None,
            )
        )
        if result is None:
            return []
        return [self._transaction_dict(item) for item in result]

    @Slot(str, str, str, result=bool)
    def deposit(self, account_number, amount, description):
        user = self._require_user()
        result = self._run(
            lambda: self.transaction_service.deposit(user, account_number, amount, description),
            "Deposit completed successfully.",
        )
        if result is not None:
            self.dataChanged.emit()
            return True
        return False

    @Slot(str, str, str, result=bool)
    def withdraw(self, account_number, amount, description):
        user = self._require_user()
        result = self._run(
            lambda: self.transaction_service.withdraw(user, account_number, amount, description),
            "Withdrawal completed successfully.",
        )
        if result is not None:
            self.dataChanged.emit()
            return True
        return False

    @Slot(str, str, str, str, result=bool)
    def transfer(self, source_account, destination_account, amount, description):
        user = self._require_user()
        result = self._run(
            lambda: self.transaction_service.transfer(user, source_account, destination_account, amount, description),
            "Transfer completed successfully.",
        )
        if result is not None:
            self.dataChanged.emit()
            return True
        return False

    @Slot(result="QVariant")
    def users(self):
        user = self._require_user()
        result = self._run(lambda: self.bank_service.list_users(user))
        if result is None:
            return []
        return [self._user_dict(item) for item in result]

    @Slot(str, str, result=bool)
    def createStaff(self, username, password):
        actor = self._require_user()
        result = self._run(
            lambda: self.bank_service.create_staff_user(actor, username, password),
            "Staff user created successfully.",
        )
        if result is not None:
            self.dataChanged.emit()
            return True
        return False

    @Slot(str, str, int, result=bool)
    def createCustomerLogin(self, username, password, customer_id):
        actor = self._require_user()
        result = self._run(
            lambda: self.bank_service.create_customer_login(actor, username, password, customer_id),
            "Customer login created successfully.",
        )
        if result is not None:
            self.dataChanged.emit()
            return True
        return False

    @Slot(int, result=bool)
    def deactivateUser(self, user_id):
        actor = self._require_user()
        success = self._run_success(
            lambda: self.bank_service.deactivate_user(actor, user_id),
            "User deactivated successfully.",
        )
        if success:
            self.dataChanged.emit()
        return success

    @Slot(int, result=bool)
    def activateUser(self, user_id):
        actor = self._require_user()
        success = self._run_success(
            lambda: self.bank_service.activate_user(actor, user_id),
            "User activated successfully.",
        )
        if success:
            self.dataChanged.emit()
        return success

    @Slot()
    def clearMessage(self):
        if self._last_error or self._last_success:
            self._last_error = ""
            self._last_success = ""
            self.messageChanged.emit()
