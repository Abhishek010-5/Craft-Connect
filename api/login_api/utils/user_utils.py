# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from werkzeug.security import generate_password_hash, check_password_hash
from api.login_api.queries import get_user_exists_query, get_user_password_query, get_insert_user_query, get_insert_user_to_pending_query, get_user_status_in_pending_signups_query, update_user_email_status_query,get_email_status_query, get_reset_password_query, get_delete_otp_query
from api.database import execute_query
from psycopg2 import DatabaseError
from flask import jsonify

def user_exists(email: str) -> bool:
    """
    Check if a user with the given email exists in the database.

    Args:
        email (str): The email address to check

    Returns:
        bool: True if user exists, False otherwise

    Raises:
        ValueError: If email is empty or invalid
        Exception: If database query fails
    """
    try:
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string")

        query = get_user_exists_query()
        params = {"email": email.strip()}
        response = execute_query(query, params, fetch_results=True)
        
        if response is None or response == []:
            return False
        return True

    except ValueError as ve:
        raise (f"Validation error: {str(ve)}")
    except Exception as e:
        raise RuntimeError(f"Database error checking user existence: {str(e)}")
        
def get_password_from_db(email: str) -> str:
    """
    Retrieve the stored password hash for a user from the database.

    Args:
        email (str): The email address of the user

    Returns:
        str: The hashed password from the database

    Raises:
        ValueError: If email is empty or invalid
        Exception: If database query fails
    """
    try:
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string")

        query = get_user_password_query()
        params = {"email": email.strip()}
        response = execute_query(query, params, fetch_results=True)
        
        if not response or response == []:
            raise ValueError("No password found for this email")
        
        return response[0] if response else ""  # Assuming response is a list with one password

    except ValueError as ve:
        raise ValueError(f"Validation error: {str(ve)}")
    except Exception as e:
        raise DatabaseError(f"Database error retrieving password: {str(e)}")

def verify_user_password(email: str, entered_password: str) -> bool:
    """
    Verify if the entered password matches the password stored in the database.

    Args:
        email (str): The user's email address
        entered_password (str): The password provided by the user

    Returns:
        bool: True if passwords match, False otherwise

    Raises:
        ValueError: If email or password is empty/invalid
        Exception: If database operations fail
    """
    try:
        if not email or not entered_password or not isinstance(email, str) or not isinstance(entered_password, str):
            raise ValueError("Email and password must be non-empty strings")

        # Get the stored password hash
        db_password = get_password_from_db(email)[0]
        
        if not db_password:
            return False

        # Verify the password
        return check_password_hash(db_password, entered_password)

    except ValueError as ve:
        raise ValueError(f"Validation error: {str(ve)}")
    except Exception as e:
        raise RuntimeError(f"Error verifying password: {str(e)}")

def insert_user(name: str, email: str, password: str)->None:
    """
    Insert a new user into the users table with hashed password.

    Args:
        name (str): The name of the user
        email (str): The email address of the user
        password (str): The plain text password to be hashed and stored

    Returns:
        None

    Raises:
        ValueError: If any of the input parameters are empty or invalid
        DatabaseError: If there’s an error executing the database query
        Exception: For other unexpected errors during execution
    """
    try:
        # Validate inputs
        if not all([name, email, password]):
            return jsonify({"error":"Name, email, and password cannot be empty"})

        # Get the insert query
        query = get_insert_user_query()

        # Hash the password
        hash_password = generate_password_hash(password, salt_length=15)

        # Prepare parameters
        params = {"name": name, "email": email, "password": hash_password}

        # Execute the query
        execute_query(query, params)

    except ValueError as ve:
        # Handle validation errors
        raise ValueError(f"Validation error: {str(ve)}")

    except DatabaseError as dbe:
        # Handle database specific errors
        raise DatabaseError(f"Database error occurred: {str(dbe)}")

    except Exception as e:
        # Handle any other unexpected errors
        raise Exception(f"An unexpected error occurred: {str(e)}")
    
def insert_user_to_pending(name: str, email: str, password: str) -> None:
    """Insert a new user into the pending_signups table.

    Args:
        name (str): The name of the user to be registered.
        email (str): The email address of the user (must be unique).
        password (str): The password for the user account.

    Returns:
        None: This function does not return any value.

    Raises:
        ValueError: If input validation fails (e.g., empty inputs).
        DatabaseError: If there are database-related errors during insertion.
        Exception: For any other unexpected errors during execution.

    The function validates the inputs, hashes the password, and attempts to insert the user
    data into the pending_signups table. It handles various exceptions that might occur
    during the process.
    """
    try:
        # Validate inputs
        if not all([name, email, password]):
            return jsonify({"error": "Name, email, and password cannot be empty"})
        query = get_insert_user_to_pending_query()
        hash_password = generate_password_hash(password)
        params = {"name": name, "email": email, "password": hash_password}
        
        response = execute_query(query, params)
    except ValueError as ve:
        # Handle validation errors
        raise ValueError(f"Validation error: {str(ve)}")

    except DatabaseError as dbe:
        # Handle database specific errors
        raise DatabaseError(f"Database error occurred: {str(dbe)}")

    except Exception as e:
        # Handle any other unexpected errors
        raise Exception(f"An unexpected error occurred: {str(e)}")
    
def user_exists_in_pending_signups(email: str) -> str:
    """
    Check if a user with the given email exists in pending signups.

    Args:
        email (str): The email address to check in pending signups.

    Returns:
        str: The result from the database query indicating user status.

    Raises:
        ValueError: If the email parameter is empty or not a string.
        DatabaseError: If there is an error executing the database query.
        TypeError: If the input parameters are of incorrect type.
    """
    try:
        # Input validation
        if not isinstance(email, str):
            raise TypeError("Email must be a string")
        if not email.strip():
            raise ValueError("Email cannot be empty")

        query = get_user_status_in_pending_signups_query()
        params = {"email": email}
        res = execute_query(query, params, fetch_results=True)
        
        return res

    except TypeError as e:
        raise TypeError(f"Invalid input type: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Invalid input value: {str(e)}")
    except Exception as e:
        raise Exception(f"Database error occurred: {str(e)}")

def update_user_email_status(email: str)->bool:
    """
    Updates the email status to 'verified' for a user in the pending_signups table.

    Args:
        email (str): The email address of the user whose status needs to be updated.
                     Must exist in the pending_signups table and be non-empty.

    Returns:
        bool: True if the update was successful, False otherwise.

    Raises:
        ValueError: If the email parameter is empty or invalid.
        DatabaseError: If there is an error executing the database query (e.g., connection issue, syntax error).
        KeyError: If the query parameters are incorrectly formatted.

    Example:
        >>> update_user_email_status("user@example.com")
        True
    """
    try:
        # Input validation
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string.")

        # Prepare the query and parameters
        query = update_user_email_status_query()
        params = {"email": email.strip()}  # Strip any whitespace

        # Execute the query
        res = execute_query(query, params)
        return res > 0

    except ValueError as ve:
        raise(f"Validation error: {str(ve)}")
    except KeyError as ke:
        raise KeyError(f"Parameter error: {str(ke)}")
    except Exception as e:
        raise DatabaseError(f"Database error occurred: {str(e)}")
        
def user_mail_verified(email: str) -> bool:
    """
    Check the verification status of a given email address.

    Args:
        email (str): The email address to check. Must be a non-empty string.

    Returns:
        bool: True if the email is verified, False otherwise.

    Raises:
        ValueError: If the email parameter is empty or not a string.
        TypeError: If the email parameter is not a string.
        Exception: For other unexpected errors during query execution.

    Example:
        >>> get_email_status("user@example.com")
        True
        >>> get_email_status("unverified@example.com")
        False
    """
    try:
        # Input validation
        if not isinstance(email, str):
            raise TypeError("Email must be a string")
        if not email:
            raise ValueError("Email cannot be empty")

        query = get_email_status_query()
        params = {"email": email}
        response = execute_query(query, params, fetch_results=True)

        # Handle empty response
        if response is None or response == []:
            return False

        # Check verification status
        if response[0][0] == "unverified":
            return True
        return False

    except TypeError as e:
        raise TypeError(f"Invalid email type: {str(e)}")
        
    except ValueError as e:
        raise ValueError(f"Invalid email value: {str(e)}")
    except DatabaseError as de:
        raise DatabaseError(f"Database error {str(de)}")
    except Exception as e:
        raise RuntimeError(f"Error checking email status: {str(e)}")
    
def reset_user_password(email: str, password: str) -> bool:
    """
    Reset the password for a user with the given email.

    Args:
        email (str): The email address of the user whose password needs to be reset.
        password (str): The new password to be set for the user.

    Returns:
        bool: True if the password was successfully reset (i.e., at least one row was updated),
              False otherwise.

    Raises:
        ValueError: If email or password is empty or invalid.
        DatabaseError: If there's an error executing the database query.
        Exception: For other unexpected errors during password reset.
    """
    try:
        # Input validation
        if not email or not password:
            raise ValueError("Email and password cannot be empty")

        # Get the reset password query
        query = get_reset_password_query()
        
        # Hash the password
        hash_password = generate_password_hash(password)
        
        # Prepare parameters
        params = {"email": email, "password": hash_password}
        
        # Execute the query
        response = execute_query(query, params)
        
        # Return True if at least one row was updated
        return response > 0

    except ValueError as ve:
        raise ValueError(f"error: {str(e)}")
    except DatabaseError as de:
        raise DatabaseError(f"Database error occurred: {str(de)}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")
        
