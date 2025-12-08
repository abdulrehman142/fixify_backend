import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    Accepts formats like: +92 300 1234567, 03001234567, etc.
    """
    # Remove spaces and common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it starts with + and has digits, or just has digits
    pattern = r'^(\+\d{1,3})?\d{7,15}$'
    return bool(re.match(pattern, cleaned))


def sanitize_phone(phone: str) -> Optional[str]:
    """
    Sanitize phone number by removing spaces and formatting.
    Returns None if invalid.
    """
    if not validate_phone(phone):
        return None
    # Remove spaces and common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    return cleaned

