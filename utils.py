from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import request

# Smallest coin value so we can round money the same way everywhere.
CURRENCY_QUANT = Decimal('0.01')


def _extract_payload():
    """Pulls info from the request whether it came from a form or JSON."""
    if request.is_json:
        return request.get_json(silent=True)
    if request.form:
        return request.form.to_dict()
    return None


def _to_decimal(value):
    """Turns number-like input into a Decimal so we can work with money safely."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _normalize_amount(value):
    """Rounds money to the nearest cent so values stay tidy."""
    decimal_value = _to_decimal(value)
    if decimal_value is None:
        return None
    return decimal_value.quantize(CURRENCY_QUANT)


def _clean_text(value):
    """Trims extra spaces so we keep the neat version of any text."""
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _to_int(value):
    """Gently converts id values into whole numbers when possible."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_datetime(raw_value):
    """Turns date strings into datetime objects, or uses right now if missing."""
    if not raw_value:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(raw_value)
    except ValueError:
        return datetime.utcnow()


def _serialize_user(user):
    """Builds a simple dictionary of a user so it is easy to send around."""
    return {
        'id': user.id,
        'firstname': user.firstname,
        'lastname': user.lastname,
        'email': user.email,
        'created_at': user.created_at.isoformat() if user.created_at else None,
    }


def _serialize_expense(record):
    """Builds an easy-to-read dictionary that describes an expense."""
    return {
        'id': record.id,
        'name': record.name,
        'type': record.type,
        'amount': float(record.amount),
        'currency': record.currency,
        'date': record.date.isoformat() if record.date else None,
        'user_id': record.user_id,
    }


def _serialize_income(record):
    """Builds an easy-to-read dictionary that explains an income entry."""
    return {
        'id': record.id,
        'name': record.name,
        'type': record.type,
        'amount': float(record.amount),
        'currency': record.currency,
        'frequency': record.frequency,
        'gross_net': record.gross_net,
        'date': record.date.isoformat() if record.date else None,
        'user_id': record.user_id,
    }


# Helper function to normalize all income to a monthly value
def calculate_monthly_income(income):
    """Turns any pay schedule into a monthly amount so we can compare stuff."""
    amount = income.amount
    freq = income.frequency.lower()
    if freq == 'hourly':
        return amount * 40 * 52 / 12  # Approximation: 40hr work week
    elif freq == 'weekly':
        return amount * 52 / 12
    elif freq == 'monthly':
        return amount
    elif freq == 'annually':
        return amount / 12
    return 0
