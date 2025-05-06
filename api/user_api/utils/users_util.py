# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from api.user_api.queries import*
from api.database import execute_query
from typing import Optional
from psycopg2 import DatabaseError
from datetime import datetime

def get_user_details(email: str) -> Optional[dict | None]:
    """
    Retrieve user details from the database using their email address.

    Args:
        email (str): The email address of the user to look up.

    Returns:
        dict: A dictionary containing user details (id, name, point, email) 
              or an error message if the user is not found or an error occurs.

    Raises:
        ValueError: If the email parameter is empty or invalid.
        Exception: For unexpected database or query execution errors.
    """
    try:
        # Validate email input
        query = get_users_detail_query()
        params = {"email": email.strip()}
        
        # Execute query
        response = execute_query(query, params, fetch_results=True)
        
        # Check for empty or null response
        if not response or response == []:
            return None
        
        # Process the first row of results
        row = response[0]
        user_details = {
            "id": row[0] if row[0] is not None else 'NA',
            "name": row[1] if row[1] is not None else 'NA',
            "point": row[2] if row[2] is not None else 0,
            "email": row[3] if row[3] is not None else 'NA'
        }
        
        return user_details
    except DatabaseError as de:
        raise DatabaseError(str(de))
    except ValueError as ve:
        raise (f"error: str(ve)")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

def get_user_with_most_points(limit: int) -> Optional[list[dict] | None]:
    """
    Retrieves a list of users with the highest points from the database.

    Args:
        limit (int): The maximum number of users to return.

    Returns:
        list[dict]: A list of dictionaries containing user details (id, name, email, points).
                    Returns None if  no users are found.

    Raises:
        ValueError: If the limit is less than or equal to 0.
        Exception: For unexpected errors during query execution or processing.
    """
    try:
        query = get_top_users_query()
        params = {"limit": limit}
        response = execute_query(query, params, fetch_results=True)

        if not response:
            return None

        top_users_details = []
        for row in response:
            try:
                details = {
                    "id": row[0] if row[0] is not None else 'NA',
                    "name": row[1] if row[1] is not None else 'NA',
                    "email": row[2] if row[2] is not None else 'NA',
                    "points": row[3] if row[3] is not None else 'NA',
                }
                top_users_details.append(details)
            except IndexError as e:
                # Handle cases where row doesn't have expected number of columns
                raise IndexError(f"Invalid data format in database response: {str(e)}")

        return top_users_details

    except ValueError as ve:
        raise ValueError(f"error: {str(ve)}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

def get_users_(limit:int)->Optional[list[dict] | None]:
    
    try:
    
        query = get_users_query()
        params = {"limit":limit}
        response = execute_query(query, params, fetch_results=True)
        
        users = []
        
        if not response:
            return None
        for row in response:
            user_details = {
                "id":row[0] if row[0] else 'NA',
                "name":row[1] if row[1] else 'NA',
                "email":row[2] if row[2] else 'NA'
            }
            users.append(user_details)
        return users
    except DatabaseError as de:
        raise DatabaseError(str(de))
    except Exception as e:
        raise RuntimeError(str(e))

def is_scheme_date_valid(id: int) -> bool:
    """
    Check if the scheme's valid-to date is greater than or equal to the current date.

    Args:
        id (int): The ID of the scheme to check.

    Returns:
        bool: True if the scheme's valid-to date is current or future, False otherwise.

    Raises:
        DatabaseError: If a database error occurs during query execution.
        ValueError: If the date string is in an invalid format.
        RuntimeError: For other unexpected errors.
    """
    try:
        query = get_scheme_valid_to_query()
        params = {"id": id}
        response = execute_query(query, params, fetch_results=True)
        
        if not response or response == []:
            return False
        
        date_str = response[0][0]
        date_object = datetime.strptime(date_str, '%d-%m-%Y').date()
        curr_date = datetime.today().date()
        
        return date_object >= curr_date
        
    except DatabaseError as dber:
        raise DatabaseError(f"Database error: {str(dber)}")
    except ValueError as ve:
        raise ValueError(f"Invalid date format: {str(ve)}")
    except Exception as e:
        raise RuntimeError(f"Error: {str(e)}")
    
def insert_scheme(name: str, email: str, scheme_id: int) -> bool:
    """
    Insert a new scheme record into the database.

    Args:
        name (str): The name associated with the scheme.
        email (str): The email associated with the scheme.
        scheme_id (int): The ID of the scheme to insert.

    Returns:
        bool: True if the insertion was successful, False otherwise.

    Raises:
        DatabaseError: If a database error occurs during query execution.
        RuntimeError: For other unexpected errors.
    """
    try:
        query = insert_scheme_query()
        params = {"name": name, "email": email, "scheme_id": scheme_id}
        response = execute_query(query, params)
    
        return response > 1
        
    except DatabaseError as dber:
        raise DatabaseError(f"Database error: {str(dber)}")
    except Exception as e:
        raise RuntimeError(f"Error: {str(e)}")

def scheme_already_applied(email:str)->bool:
    try:
        # Construct a safe query to check for the email
        query = scheme_already_applied_query()
        params = {"email": email}

        # Execute the query
        response = execute_query(query, params, fetch_results=True)

        # Check if the email exists (response should contain a boolean)
        if response and response[0][0]:
            return True
        return False

    except DatabaseError as dber:
        raise DatabaseError(f"Database error: {str(dber)}")
    except ValueError as ve:
        raise ValueError(f"Invalid input: {str(ve)}")
    except Exception as e:
        raise RuntimeError(f"Error: {str(e)}")
    
def scheme_status(email: str) -> Optional[list[dict]| None]:
    """
    Retrieves the status of schemes applied by a user based on their email.

    Args:
        email (str): The email address associated with the user applying for schemes.

    Returns:
        Optional[list[dict]]: A list of dictionaries containing scheme status details,
            or None if no schemes are found. Each dictionary contains:
            - scheme_title (str): The title of the scheme, or "NA" if not available.
            - scheme_status (str): The status of the scheme (e.g., "Pending", "Approved", "Rejected"),
              or "NA" if not available.

    Raises:
        DatabaseError: If a database error occurs during query execution.
        RuntimeError: If an unexpected error occurs during execution.

    Examples:
        >>> scheme_status_user_api("user@example.com")
        [{'scheme_title': 'Summer Bonanza', 'scheme_status': 'Pending'}]
    """
    try:
        query = scheme_status_query()
        params = {"email":email}
        response = execute_query(query, params, fetch_results=True)
        
        if not response or response == []:
            return None
        status = []
        
        for row in response:
            scheme_status = {
                "scheme_title":row[0] if row[0] else "NA",
                "scheme_status":row[1] if row[1] else "NA",
            }
            status.append(scheme_status)
        return status
    except DatabaseError as dber:
        raise DatabaseError(f"Database error {str(dber)}")
    except Exception as e:
        raise RuntimeError(str(e))
        
def get_schemes_()->Optional[ list[dict] | None]:
    """
    This function gets the schemes for the user that are active or are in the scheme table
    
    Returns:
        Optional[list[dict] | None]: A list of dictionaries containing scheme details, or None if no schemes are found.
        Each dictionary contains:
            - shceme_id (str): The ID of the scheme, or "NA" if not available.
            - scheme_title (str): The title of the scheme, or "NA" if not available.
            - scheme_valid_from (str): The start date of the scheme, or "NA" if not available.
            - scheme_valid_to (str): The end date of the scheme, or "NA" if not available.
            - perks (str): The perks associated with the scheme, or "NA" if not available.
            - points (int): The points associated with the scheme, defaults to 10000 if not available.
    
    Raises:
        DatabaseError: If a database error occurs during query execution.
        RuntimeError: If an unexpected error occurs.
    """
    try:
        query = get_scheme_query()
        response = execute_query(query, fetch_results=True)
        
        if not response or response == []:
            return None
        
        scheme = []
        for row in response:
            scheme_details = {
                "scheme_id":row[0] if row[0] else "NA",
                "scheme_title":row[1] if row[1] else "NA",
                "scheme_valid_from":row[2] if row[2] else "NA",
                "scheme_valid_to":row[3] if row[3] else "NA",
                "perks":row[4] if row[4] else "NA",
                "points":row[5] if row[5] else 10000
            }
            scheme.append(scheme_details)
        return scheme
    except DatabaseError as dber:
        raise DatabaseError(f"Database error occured {str(dber)}")
    except Exception as e:
        raise RuntimeError(str(e))
        
def get_points_required_for_scheme(scheme_id: int) -> Optional[int | None]:
    """
    Retrieves the points required for a specific scheme from the database.

    Args:
        scheme_id (int): The unique identifier of the scheme.

    Returns:
        Optional[int | None]: The number of points required for the scheme, or None if not found.
    Raises:
        DatabaseError: If a database-related error occurs during query execution.
        RuntimeError: If an unexpected error occurs during the operation.
    """
    try:
        query = get_points_required_for_scheme_query()
        params = {"scheme_id": scheme_id}
        response = execute_query(query, params, fetch_results=True)
        
        if not response or response == []:
            return None
        points = response[0][0]
        
        return int(points)
    except DatabaseError as dber:
        raise DatabaseError(f"Database error :{str(dber)}")
    except Exception as e:
        raise RuntimeError({str(e)})