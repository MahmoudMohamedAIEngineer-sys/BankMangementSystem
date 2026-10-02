from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from Models.Users import User
from Services.Storage import Storage
from Utils.exceptions import AuthenticationError
from Utils.Validators import validate_username

password_hasher = PasswordHasher()

def hash_password(password):
    return password_hasher.hash(password)

def verify_password(password, hashed_password):
    try:
        return password_hasher.verify(hashed_password, password)
    except VerifyMismatchError:
        return False

class AuthenticationService:
    def __init__(self, store):
        self.store = store

    def authenticate(self, username, password):
        username = validate_username(username)
        credentials = self.store.get_credentials(username)
        if credentials is None or not verify_password(password, credentials["password_hash"]):
            raise AuthenticationError("Username or password is incorrect.")

        user = self.store.get_user_by_id(credentials["user_id"])
        
        if user is None or not user.is_active:
            raise AuthenticationError("This user account is inactive.")

        if user.customer_id is not None:
            customer = self.store.get_customer_by_id(user.customer_id)
            if customer is None or not customer.is_active:
                raise AuthenticationError("The linked customer profile is inactive.")

        return user