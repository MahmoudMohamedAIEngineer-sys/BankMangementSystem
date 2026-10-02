from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from Utils.exceptions import ValidationError

_CENT = Decimal("0.01")

def parse_amount(value):
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError) as exc:
        raise ValidationError("Amount must be a valid number.") from exc

    if not amount.is_finite():
        raise ValidationError("Amount must be a finite number.")

    if amount.as_tuple().exponent < -2:
        raise ValidationError("Amount cannot contain more than two decimal places.")

    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)

def money_to_cents(value):
    amount = parse_amount(value)
    return int(amount * 100)

def cents_to_money(cents):
    if not isinstance(cents, int):
        raise ValidationError("Amount must be a whole number of cents.")
    return (Decimal(cents) / Decimal("100")).quantize(_CENT, rounding=ROUND_HALF_UP)

def format_money(value):
    amount =cents_to_money(value) if isinstance(value, int) else parse_amount(value)
    return f"${amount:,.2f}"