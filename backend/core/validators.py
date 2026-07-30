import re

from django.core.exceptions import ValidationError

PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)]{7,20}$")


def validate_phone_number(value):
    """
    Reusable phone validator shared by Customer and Lead serializers.
    Accepts optional leading '+', digits, spaces, hyphens and parentheses,
    7-20 characters total -- permissive enough for international formats
    without being a no-op.
    """
    if not PHONE_REGEX.match(value):
        raise ValidationError(
            "Enter a valid phone number (digits, spaces, +, -, and parentheses only, 7-20 characters)."
        )
