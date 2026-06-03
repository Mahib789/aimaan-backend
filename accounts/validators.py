import re
from django.core.exceptions import ValidationError


def strong_password_validator(password):

    # Minimum length
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    # At least 1 uppercase
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least 1 uppercase letter.")

    # At least 1 lowercase (optional but good practice)
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least 1 lowercase letter.")

    # At least 1 digit
    if not re.search(r"[0-9]", password):
        raise ValidationError("Password must contain at least 1 number.")

    # At least 1 special character
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\]~`]", password):
        raise ValidationError("Password must contain at least 1 special character.")

    return True