"""
Utility functions and helpers
"""

import re
from typing import Optional
from datetime import datetime, timedelta


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone: str) -> bool:
    """Validate phone number (basic)"""
    # Remove common formatting
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    # Check if it's digits and reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    # Remove special chars
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:240] + '.' + ext if ext else name[:255]
    return filename


def calculate_retention_date(years: int) -> datetime:
    """Calculate file retention date"""
    return datetime.utcnow() + timedelta(days=365 * years)


def parse_duration(duration_str: str) -> Optional[timedelta]:
    """
    Parse duration string (e.g., '3y', '6m', '30d') into timedelta
    
    Supported formats:
    - 3y: 3 years
    - 6m: 6 months
    - 30d: 30 days
    """
    if not duration_str:
        return None
    
    match = re.match(r'^(\d+)([ymd])$', duration_str.lower())
    if not match:
        return None
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == 'd':
        return timedelta(days=value)
    elif unit == 'm':
        return timedelta(days=value * 30)  # Approximate
    elif unit == 'y':
        return timedelta(days=value * 365)  # Approximate
    
    return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_bytes(bytes_size: int) -> str:
    """Format bytes into human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def mask_email(email: str) -> str:
    """Mask email for privacy (keep first char and domain)"""
    if not email or '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask phone number for privacy"""
    if not phone:
        return phone
    
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 4:
        return '*' * len(digits)
    
    return '*' * (len(digits) - 4) + digits[-4:]
