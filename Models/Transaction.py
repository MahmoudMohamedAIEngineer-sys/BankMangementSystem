class Transactions:
    def __init__(self, transaction_id, transaction_type, amount,
                 source_account_id, destination_account_id,
                 performed_by_user_id, description, created_at,
                 source_account_number, destination_account_number,
                 performed_by_username):
        self.transaction_id             = transaction_id
        self.transaction_type           = transaction_type
        self.amount                     = amount
        self.source_account_id          = source_account_id
        self.destination_account_id     = destination_account_id
        self.performed_by_user_id       = performed_by_user_id
        self.description                = description
        self.created_at                 = created_at
        self.source_account_number      = source_account_number
        self.destination_account_number = destination_account_number
        self.performed_by_username      = performed_by_username
