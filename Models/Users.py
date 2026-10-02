from Utils.Constants import Role, Permission, DashboardType


class User:
    def __init__(self, user_id, username, role, is_active=True, customer_id=None, password_hash=""):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.is_active = is_active
        self._customer_id = customer_id
        self.password_hash = password_hash

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def is_staff(self):
        return self.role == Role.STAFF

    def get_permissions(self):
        return {Permission.VIEW_OWN_PROFILE}

    def dashboard_scope(self):
        return DashboardType.PERSONAL

    def can(self, permission):
        return permission in self.get_permissions()


class StaffUser(User):
    def __init__(self, user_id, username, is_active=True, password_hash=""):
        super().__init__(user_id, username, Role.STAFF, is_active, None, password_hash)

    def get_permissions(self):
        return {
            Permission.VIEW_OWN_PROFILE,
            Permission.VIEW_ALL_CUSTOMERS,
            Permission.MANAGE_CUSTOMERS,
            Permission.CREATE_ACCOUNTS,
            Permission.VIEW_ALL_ACCOUNTS,
            Permission.MANAGE_ACCOUNT_STATUS,
            Permission.STAFF_FINANCIAL_OPERATIONS,
            Permission.VIEW_ALL_TRANSACTIONS,
            Permission.MANAGE_USERS,
            Permission.VIEW_SYSTEM_STATISTICS,
        }

    def dashboard_scope(self):
        return DashboardType.SYSTEM


class CustomerUser(User):
    def __init__(self, user_id, username, customer_id, is_active=True, password_hash=""):
        super().__init__(user_id, username, Role.CUSTOMER, is_active, customer_id, password_hash)

    def get_permissions(self):
        return {
            Permission.VIEW_OWN_PROFILE,
            Permission.VIEW_OWN_DATA,
            Permission.CUSTOMER_SELF_SERVICE,
        }

    def dashboard_scope(self):
        return DashboardType.PERSONAL
