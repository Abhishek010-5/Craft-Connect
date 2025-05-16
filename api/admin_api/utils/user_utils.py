# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from api.database import execute_query
from api.admin_api.queries import*
from typing import List, Dict, Optional, Any
from psycopg2 import DatabaseError

def get_user_from_pending_signups() -> Optional[List[Dict[str, Any]] | None]:
    """
    Fetch all users from the pending signups table and return their details.

    This function executes a query to retrieve user information from the pending_signups table
    and formats the results into a list of dictionaries.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of dictionaries containing user details, or None if no users are found.
            Each dictionary contains:
            - user_id (int): Unique identifier for the user
            - name (str): User's name
            - email (str): User's email address
            - email_status (str): Status of email verification
            - user_status (str): Current status of the user account

    Raises:
        RuntimeError: If there's an error executing the database query or formatting results
    """
    try:
        query = get_user_from_pending_signups_query()
        response = execute_query(query, fetch_results=True)
        
        if not response:
            return None
        
        return [{
            "user_id": details[0],
            "name": details[1],
            "email": details[2],
            "email_status": details[3],
            "user_status": details[4]
        } for details in response]
    
    except Exception as e:
        raise RuntimeError(f"Failed to fetch pending signups: {str(e)}")


def update_pending_signups_status(email: str, status: str) -> bool:
    """
    Update the status of a user in the pending signups table.

    This function updates the status of a specific user in the pending_signups table
    based on their email address. The status should be a valid value such as "approved",
    "pending", or "rejected".

    Args:
        email (str): The email address of the user to update. Must be a non-empty string
                     containing a valid email format (e.g., "user@example.com").
        status (str): The new status to set for the user. Must be a non-empty string and
                      one of the expected values ("approved", "pending", "rejected").

    Returns:
        bool: True if the update was successful (at least one row affected),
              False otherwise.

    Raises:
        ValueError: If the email is not a valid email address, status is empty, or status
                    is not one of the expected values ("approved", "pending", "rejected").
        DatabaseError: If there's an error executing the database update (e.g., connection
                       issues, syntax errors).

    Example:
        >>> update_pending_signups_status("user@example.com", "approved")
        True
    """
    try:
        # Validate email
        if not email or not isinstance(email, str) or '@' not in email:
            raise ValueError("Invalid email address provided")

        # Validate status
        valid_statuses = {"approved", "pending", "rejected"}
        if not status or not isinstance(status, str) or status.lower() not in valid_statuses:
            raise ValueError("Invalid status. Must be 'approved', 'pending', or 'rejected'")

        # Prepare and execute update query
        query = update_user_status_query()
        params = {"email": email, "status": status.lower()}  # Normalize status to lowercase
        response = execute_query(query, params)

        # Check if update was successful
        if response is None or not isinstance(response, (int, float)):
            return False
        
        return response > 0

    except ValueError as ve:
        raise ValueError(f"Validation Error: {ve}")
    except Exception as e:
        raise RuntimeError(f"Unexpected Error: {e}")

def insert_user_to_users(email: str) -> bool:
    """
    Transfer an approved user from pending signups to users table and remove from pending.

    This function fetches an approved user from the pending_signups table using the provided email,
    inserts their information into the users table, and then deletes the entry from pending_signups.

    Args:
        email (str): The email address of the user to be transferred.

    Returns:
        bool: True if both insertion and deletion were successful, False otherwise.

    Raises:
        ValueError: If email is empty or invalid.
        DatabaseError: If there are issues executing any of the database queries.
        IndexError: If the query results are unexpectedly formatted.

    Example:
        >>> insert_user_to_users("user@example.com")
        True
    """
    try:
        # Validate email
        if not email or not isinstance(email, str) or '@' not in email:
            raise ValueError("Invalid email address provided")

        # Fetch approved user
        query_1 = get_approved_users_query()
        params_1 = {"email": email}
        get_user = execute_query(query_1, params=params_1, fetch_results=True)

        # Check if user was found and data is sufficient
        if not get_user or len(get_user) == 0 or len(get_user[0]) < 3:
            return False

        # Prepare data for insertion
        params_2 = {
            "name": get_user[0][0], 
            "email": get_user[0][1], 
            "password": get_user[0][2]
        }
        
        # Insert into users table
        query_2 = insert_user_to_users_query()
        insert_response = execute_query(query_2, params_2)

        # Delete from pending_signups
        delete_response = execute_query(delete_approved_user(), {"email": email})

        # Both operations should be successful
        return insert_response > 0 and delete_response > 0

    except ValueError as ve:
        raise (f"Validation Error: {ve}")
        
    except IndexError as ie:
        raise IndexError(f"Data Formatting Error: {ie}")
    
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")

def delete_user(email: str) -> bool:
    """
    Delete a user from the users table based on their email address.

    This function is intended for admin use to remove a user from the system.
    It executes a delete query using the provided email and returns whether
    the deletion was successful.

    Args:
        email (str): The email address of the user to be deleted.

    Returns:
        bool: True if user was successfully deleted (1 or more rows affected),
              False if no user was deleted or an error occurred.

    Raises:
        ValueError: If the email parameter is empty or not a string.
        DatabaseError: If there is an error executing the database query.
    """
    try:
        # Validate email parameter
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email must be a non-empty string")

        # Prepare query and parameters
        query = delete_user_query()
        params = {"email": email.strip()}

        # Execute query and get response
        response = execute_query(query, params)

        # Return True if at least one row was affected
        return response > 0

    except ValueError as ve:
        # Log the error (in a real application, use proper logging)
        print(f"Validation error: {str(ve)}")
        return False
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {str(e)}")
        return False

def insert_user_to_user_point(email: str) -> bool:
    """
    Insert a user into the user points table based on their email.

    Args:
        email (str): The email address of the user to be inserted.

    Returns:
        bool: True if insertion was successful (affected rows > 0), False otherwise.

    Raises:
        ValueError: If email is empty or None.
        TypeError: If email is not a string.
        DatabaseError: If there is an error executing the database query.
    """
    try:
        # Validate input
        if not isinstance(email, str):
            raise TypeError("Email must be a string")
        if not email:
            raise ValueError("Email cannot be empty")

        # Prepare and execute query
        query = insert_user_to_user_points_query()
        params = {"email": email}
        response = execute_query(query, params)

        # Check if insertion was successful
        return response > 0

    except ValueError as ve:
        raise ValueError(f"Validation error: {str(ve)}")
    except TypeError as te:
        raise TypeError(f"Type error: {str(te)}")
    except Exception as e:
        raise RuntimeError(f"Database error occurred: {str(e)}")
        
def update_user_details_(email: str, points: int, name: str) -> bool:
    """
    Updates user details in the database using the admin API.

    Args:
        email (str): The current email of the user.
        new_email (str): The new email to set for the user.
        points (int): The new points value to set for the user.
        id (int): The unique identifier of the user.

    Returns:
        bool: True if the update was successful (at least one row affected), False otherwise.

    Raises:
        DatabaseError: If a database-related error occurs during query execution.
        RuntimeError: If any other unexpected error occurs.
    """
    try:
        query = update_user_details_query()
        params = {"email": email, "points": points, "name": name}
        response = execute_query(query, params)
        
        return response > 0
    except DatabaseError as dber:
        raise DatabaseError(f"Database error {str(dber)}")
    except Exception as e:
        raise RuntimeError(str(e))