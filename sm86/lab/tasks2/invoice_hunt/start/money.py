from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

def number(text):
    try:
        value = Decimal(text)
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError('decimal') from None
    if not value.is_finite() or value < 0:
        raise ValueError('amount')
    return value

def cents(value):
    return value.quantize(Decimal('.01'), rounding='ROUND_HALF_EVEN')

def display(value):
    return format(value, '.2f')
