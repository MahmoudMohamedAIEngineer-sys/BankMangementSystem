from Utils.Constants import Permission, Role
from Utils.exceptions import NotFoundError, PermissionDeniedError


class AuthorizationService:
    def __init__(self, storage):
        self.storage = storage

    def require_permission(self, actor, permission):
        if not actor.is_active:
            raise PermissionDeniedError("This user is inactive.")
        if not actor.can(permission):
            raise PermissionDeniedError("You are not authorized to perform this action.")

    def require_staff(self, actor, permission):
        if actor.role != Role.STAFF:
            raise PermissionDeniedError("This operation is available only to staff.")
        self.require_permission(actor, permission)

    def require_account_access(self, actor, account, owner):
        if actor.is_staff:
            self.require_permission(actor, Permission.STAFF_FINANCIAL_OPERATIONS)
            return

        self.require_permission(actor, Permission.CUSTOMER_SELF_SERVICE)
        if actor.customer_id != account.customer_id:
            raise PermissionDeniedError("You can access only your own accounts.")

        if owner is None:
            owner = self.storage.get_customer_by_id(account.customer_id)
        if owner is None:
            raise NotFoundError("Account owner was not found.")
        if not owner.is_active:
            raise PermissionDeniedError("The customer profile is inactive.")

    def require_customer_profile(self, actor, customer):
        self.require_permission(actor, Permission.VIEW_OWN_DATA)
        if actor.customer_id != customer.customer_id:
            raise PermissionDeniedError("You can view only your own profile.")
        if not customer.is_active:
            raise PermissionDeniedError("The customer profile is inactive.")
