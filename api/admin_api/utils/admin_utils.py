from api.admin_api.queries import*
from psycopg2 import DatabaseError
from api.database import execute_query
from werkzeug.security import generate_password_hash, check_password_hash

def insert_admin_admin_api(email: str, password: str) -> bool:
    """
    Inserts a new admin user into the database using the provided email and password.

    Args:
        email (str): The email address of the admin user.
        password (str): The password for the admin user.

    Returns:
        bool: True if the insertion was successful, False otherwise.

    Raises:
        DatabaseError: If a database-related error occurs during the insertion.
        RuntimeError: If a general runtime error occurs during the operation.
    """
    try:
        query = get_insert_admin_query()
        params = {"email": email, "password": password}
        response = execute_query(query, params)
        
        return response > 0
    except DatabaseError as dber:
        raise DatabaseError(f"Database error : {str(dber)}")
    except RuntimeError as e:
        raise RuntimeError(str(e))
    
def validate_admin_password(email: str, password: str) -> bool:
    """
    Validates an admin user's password by comparing it with the stored hashed password.

    Args:
        email (str): The email address of the admin user.
        password (str): The password to validate.

    Returns:
        bool: True if the password matches the stored hash, False otherwise.

    Raises:
        DatabaseError: If a database-related error occurs during the query.
        RuntimeError: If a general runtime error occurs during the operation.
    """
    try:
        query = get_admin_password_query()
        params = {"email": email}
        response = execute_query(query, params, fetch_results=True)
        if not response or response == []:
            return False
        hash_password = response[0][0]
        
        return check_password_hash(hash_password, password)
    except DatabaseError as dber:
        raise DatabaseError(f"Database error : {str(dber)}")
    except RuntimeError as e:
        raise RuntimeError(str(e))
    
def is_admin_present(email: str) -> bool:
    """
    Checks if an admin user with the specified email exists in the database.

    Args:
        email (str): The email address to check for an admin user.

    Returns:
        bool: True if an admin with the given email exists, False otherwise.

    Raises:
        DatabaseError: If a database-related error occurs during the query.
        RuntimeError: If a general runtime error occurs during the operation.
    """
    try:
        query = get_admin_exists_query()  
        params = {"email": email}
        response = execute_query(query, params, fetch_results=True)
        
        return bool(response and response != [])
    except DatabaseError as dber:
        raise DatabaseError(f"Database error: {str(dber)}")
    except RuntimeError as e:
        raise RuntimeError(str(e))
    
def delete_admin(email: str) -> bool:
    """
    Deletes an admin user from the database using the provided email.

    Args:
        email (str): The email address of the admin user to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.

    Raises:
        DatabaseError: If a database-related error occurs during the deletion.
        RuntimeError: If a general runtime error occurs during the operation.
    """
    try:
        query = delete_admin_query()
        params = {"email": email}
        response = execute_query(query, params)
        
        return response > 0
    except DatabaseError as dber:
        raise DatabaseError(f"Database error: {str(dber)}")
    except RuntimeError as e:
        raise RuntimeError(str(e))