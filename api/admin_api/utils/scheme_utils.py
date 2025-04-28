# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from api.database import execute_query
from api.admin_api.queries import insert_scheme_query, delete_scheme_query, update_scheme_query, get_scheme_query 
from datetime import date, datetime
from typing import Optional

def add_scheme(scheme_title: str, valid_from: str, valid_to: str, perks: str, points: int) -> bool:
    """
    Adds a new scheme to the database with the specified details.

    Args:
        scheme_title (str): The title of the scheme.
        valid_from (date): The start date of the scheme's validity.
        valid_to (date): The end date of the scheme's validity.
        perks (str): Description of the perks associated with the scheme.
        points (int): The number of points required to complete the scheme.

    Returns:
        bool: True if the scheme was successfully added, False otherwise.

    Raises:
        ValueError: If any input parameter is invalid (e.g., empty title, invalid dates, negative points).
        DatabaseError: If there is an issue executing the database query.
    """
    try:
        # Input validation
        if not scheme_title.strip():
            raise ValueError("Scheme title cannot be empty")
        if valid_from > valid_to:
            raise ValueError("Valid from date must be before valid to date")
        if points < 0:
            raise ValueError("Points cannot be negative")

        query = insert_scheme_query()
        params = {
            "scheme_title": scheme_title,
            "scheme_valid_from": valid_from,
            "scheme_valid_to": valid_to,
            "scheme_perks": perks,
            "points": points
        }

        response = execute_query(query, params)
        return response > 0

    except ValueError as ve:
        raise ValueError(f"Validation error: {str(ve)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while adding scheme: {str(e)}")
        
def remove_scheme(scheme_title:str)->Optional[bool]:
    if not isinstance(scheme_title, str):
        return f"The scheme title should be of type str, but provided type is {type(scheme_title).__name__}"

    try:
        query = delete_scheme_query()
        params = {"scheme_title":scheme_title}
        response = execute_query(query, params)
        
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")
    

    return response > 0
    
def update_scheme(scheme_title: str, valid_from: Optional[str] = None, valid_to: Optional[str] = None, perks: Optional[str] = None, points: Optional[int] = None) -> bool:
    """
    Updates a scheme in the database with the provided parameters.

    Args:
        scheme_title (str): The title of the scheme to update.
        valid_from (str, optional): The start date of the scheme's validity period.
        valid_to (str, optional): The end date of the scheme's validity period.
        perks (str, optional): Description of the perks associated with the scheme.
        points (int, optional): The number of points associated with the scheme.

    Returns:
        bool: True if the scheme was successfully updated, False otherwise.

    Raises:
        ValueError: If scheme_title is empty or None.
        TypeError: If any parameter is of an incorrect type.
        DatabaseError: If there is an issue executing the database query.
    """
    try:
        # Validate scheme_title
        if not scheme_title or not isinstance(scheme_title, str):
            raise ValueError("scheme_title must be a non-empty string")
            

        # Type checking for optional parameters
        if valid_from is not None and not isinstance(valid_from, str):
            raise ValueError("valid_from must be a date object")
        if valid_to is not None and not isinstance(valid_to, str):
            raise ("valid_to must be a date object")
            
        if perks is not None and not isinstance(perks, str):
            raise ValueError("perks must be a string")
        
        if points is not None and not isinstance(points, int):
            raise ValueError("points must be an integer")
    
        query = update_scheme_query()
        params = {
            "scheme_title": scheme_title,
            "scheme_valid_from": valid_from,
            "scheme_valid_to": valid_to,
            "scheme_perks": perks,
            "points": points,
        }

        response = execute_query(query, params)
        return response > 0

    except ValueError as ve:
        return f"Validation error: {str(ve)}"
    except TypeError as te:
        return f"Type error: {str(te)}"

def get_scheme()->list[dict]:
    """
    Retrieves scheme details from a database query and formats them into a list of dictionaries.

    This function executes a predefined query to fetch scheme data, processes each row to extract
    relevant fields (title, valid_from, valid_till, perks), and formats date fields into 'DD/MM/YYYY'.
    It includes error handling for query execution, invalid date formats, and missing data.

    Returns:
        list: A list of dictionaries, each containing scheme details:
              - Title (str): The scheme title.
              - valid_from (str): The start date in 'DD/MM/YYYY' format or 'N/A' if not available.
              - valid_till (str): The end date in 'DD/MM/YYYY' format or 'N/A' if not available.
              - perks (str): The scheme perks.

    Raises:
        Exception: If the query execution fails or an unexpected error occurs during processing.
    """
    try:
        query = get_scheme_query()
        response = execute_query(query, fetch_results=True)

        if not response:
            return []

        schemes = []
        for row in response:
            try:
                schemes_details = {
                    "Title": row[1] if row[1] else "N/A",
                    "valid_from": row[2] if row[2]  else "N/A",
                    "valid_till": row[3] if row[3] else "N/A",
                    "perks": row[4] if row[4] else "N/A",
                    "points":row[5] if row[5] else "N/A"
                }
                schemes.append(schemes_details)
            except (AttributeError, ValueError) as e:
                # Handle cases where row[2] or row[3] are not valid datetime objects or other issues
                print(f"Error processing row {row}: {e}")
                schemes_details = {
                    "Title": row[1] if row[1] else "N/A",
                    "valid_from": "N/A",
                    "valid_till": "N/A",
                    "perks": row[4] if row[4] else "N/A",
                    "points":row[5] if row[5] else "N/A"
                }
                schemes.append(schemes_details)
        return schemes

    except Exception as e:
        raise RuntimeError(f"Error executing query or processing schemes: {e}")
        



 