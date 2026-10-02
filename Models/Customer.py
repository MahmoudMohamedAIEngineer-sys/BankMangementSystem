from datetime import datetime, timezone
class Customer:
    def __init__(self, customer_id, name, email, phone, address, is_active = True, created_at = None):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)