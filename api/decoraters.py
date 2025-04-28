from flask import request, abort
import jwt
from typing import Callable, Any
from functools import wraps
from config import JWT_ALGORITHM, JWT_EXPIRY_MINUTES, JWT_SECRET_KEY, ADMIN_KEY

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            abort(401, description="Token is missing")

        try:
            # Expect token in format "Bearer <token>"
            if not token.startswith('Bearer '):
                abort(401, description="Invalid token format")
            token = token.split(' ')[1]

            # Decode and verify JWT
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            request.user = payload['sub']  # Store user data in request for use in endpoint
        except jwt.ExpiredSignatureError:
            abort(401, description="Token has expired")
        except jwt.InvalidTokenError:
            abort(401, description="Invalid token")

        return f(*args, **kwargs)
    return decorated_function




def admin_key_required(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        expected_key = ADMIN_KEY
        if not expected_key:
            raise ValueError("Admin key not configured. Please set ADMIN_KEY environment variable.")
        
        provided_key = kwargs.get('admin_key')
        if not provided_key:
            raise PermissionError("Admin key is required to access this function.")
        
        if provided_key != expected_key:
            raise PermissionError("Invalid admin key.")
        
        return func(*args, **kwargs)
    
    return wrapper