import re
from Utils.exceptions import ValidationError

EMAIL_PATTERN    = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_PATTERN    = re.compile(r"^\d{10,15}$")
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,20}$")


def required(value, field_name):
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValidationError(f"{field_name} cannot be empty.")
    return cleaned


def validate_email(email):
    email = required(email, "Email").lower()
    if not EMAIL_PATTERN.match(email):
        raise ValidationError("Invalid email address.")
    return email


def Validate_Phone(phone):
    phone = required(phone, "Phone").strip()
    if not PHONE_PATTERN.match(phone):
        raise ValidationError("Invalid phone number.")
    return phone


def validate_username(username):
    username = required(username, "Username").lower()
    if not USERNAME_PATTERN.match(username):
        raise ValidationError("Invalid username.")
    return username


def validate_password(password):
    if not password:
        raise ValidationError("Password cannot be empty.")
    if len(password) < 6:
        raise ValidationError("Password must contain at least six characters.")
    return password


def validate_account_type(account_type):
    if account_type not in ["SAVINGS", "CURRENT", "BUSINESS"]:
        raise ValidationError("Account type must be 'SAVINGS', 'CURRENT', or 'BUSINESS'.")
    return account_type
