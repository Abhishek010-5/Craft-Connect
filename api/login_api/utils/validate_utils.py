import re

def validate_email(email: str) -> bool:
    """
    Validate email address using regex pattern.
    Returns True if email is valid, False otherwise.
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: Validation result
    """
    # Email regex pattern: checks for standard email format
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or not isinstance(email, str):
        return False
    
    return bool(re.match(pattern, email))

def validate_password(password: str) -> bool:
    """
    Validate password strength using regex pattern.
    Password must be 8-20 characters long and contain at least:
    - 1 uppercase letter
    - 1 lowercase letter
    - 1 number
    - 1 special character
    
    Args:
        password (str): Password to validate
    
    Returns:
        bool: Validation result
    """
    if not password or not isinstance(password, str):
        return False
    
    # Check length
    if not (8 <= len(password) <= 20):
        return False
    
    # Pattern for password requirements:
    # At least one uppercase, one lowercase, one number, one special char
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$'
    
    return bool(re.match(pattern, password))