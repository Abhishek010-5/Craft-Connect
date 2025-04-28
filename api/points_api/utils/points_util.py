# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from api.points_api.queris import get_points_query, update_user_point_query, insert_points_data_query, get_pin_validate_query
from api.database import execute_query, execute_query_for_points
from psycopg2 import DatabaseError


def get_user_points(email: str) -> int:
    """
    Retrieves the points for a given user email.
    
    Args:
        email (str): The user's email address.
        
    Returns:
        int: The user's points, or 0 if user not found or an error occurs.
        
    Raises:
        ValueError: If email is empty or invalid.
        Exception: For unexpected database errors.
    """
    try:
        if not email or not isinstance(email, str):
            raise ValueError("Invalid or empty email provided")
            
        query = get_points_query()
        params = {"email": email}
        response = execute_query(query=query, params=params, fetch_results=True)
        
        if not response or response == []:
            return 0
            
        points = response[0][0]
        return int(points) if points is not None else 0
        
    except ValueError as ve:
        raise ValueError(f"error {ve}")
    except DatabaseError as de:
        raise DatabaseError(f"Database error {str(de)}")
    except Exception as e:
        raise RuntimeError(f"Error retrieving user points: {e}")

def add_user_points(email: str, point: int) -> bool:
    """
    Adds points to a user's existing points.
    
    Args:
        email (str): The user's email address.
        point (int): The number of points to add.
        
    Returns:
        bool: True if points were added successfully, False otherwise.
        
    Raises:
        ValueError: If email is empty/invalid or points is negative.
        Exception: For unexpected database errors.
    """
    try:
        if not email or not isinstance(email, str):
            raise ValueError("Invalid or empty email provided")
        if not isinstance(point, int) or point < 0:
            raise ValueError("Points must be a non-negative integer")
            
        query = update_user_point_query()
        old_points = get_user_points(email)
        updated_points = old_points + point
        params = {"email": email, "points": updated_points}
        response = execute_query(query=query, params=params)
        
        return response > 0
        
    except DatabaseError as de:
        raise DatabaseError(f"Database error {str(e)}")
    except ValueError as ve:
        raise ValueError(f"Value error {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error adding user points: {e}")

def redeem_user_points(email: str, points: int) -> bool:
    """
    Redeems points from a user's account if sufficient points are available.
    
    Args:
        email (str): The user's email address.
        points (int): The number of points to redeem.
        
    Returns:
        bool: True if points were redeemed successfully, False otherwise.
        
    Raises:
        ValueError: If email is empty/invalid or points is negative.
        Exception: For unexpected database errors.
    """
    try:
        if not email or not isinstance(email, str):
            return False
        if not isinstance(points, int) or points < 0:
            return False
        
        total_points = get_user_points(email)
        if points > total_points:
            return False
            
        query = update_user_point_query()
        params = {"email": email, "points": total_points - points}
        response = execute_query(query=query, params=params)
        
        return response > 0
    except DatabaseError as de:
        raise DatabaseError(f"Database error: {str(de)}")
        
    except ValueError as ve:
        raise ValueError(f"Validation error: {ve}")
    
    except Exception as e:
        raise RuntimeError(f"Error redeeming user points: {e}")

def execute_pin_validation(pin_data:list) -> dict:
    try:
        result = {
            "success_pins": [],
            "already_scanned": [],
            "not_in_system": [],
            "expired": [],
            "invalid": [],
            "total_value": 0
        }
        
        points_codes = []
        if not isinstance(pin_data, list):
            raise ValueError("pin_data must be a list")
            
        for points_code in pin_data:
            if not isinstance(points_code, str):
                raise ValueError("Each element in pin_data must be a string")
            if not points_code:
                raise ValueError("Points code cannot be empty")
            points_codes.append(points_code)
        
        if not points_codes:
            return {
                "success_pins": 0,
                "already_scanned": 0,
                "not_in_system": 0,
                "expired": 0,
                "total_points": 0
            }
        
        PIN_VALIDATION_QUERY = get_pin_validate_query()
        
        query_results = execute_query_for_points(
            PIN_VALIDATION_QUERY,
            params=(points_codes,),
            fetch_results=True
        )
        
        for points_code, status, points_value in query_results:
            pin_info = {
                "points_code": points_code,
                "points_value": points_value
            }
            
            if status == "success":
                result["success_pins"].append(pin_info)
            elif status == "already_scanned":
                result["already_scanned"].append(pin_info)
            elif status == "not_in_system":
                result["not_in_system"].append(pin_info)
            elif status == "expired":
                result["expired"].append(pin_info)
            elif status == "invalid":
                result["invalid"].append(pin_info)
        
        result["total_value"] = sum(pin["points_value"] for pin in result["success_pins"])
        
        final_result = {
            "success_pins": len(result["success_pins"]),
            "already_scanned": len(result["already_scanned"]),
            "not_in_system": len(result["not_in_system"]),
            "expired": len(result["expired"]),
            "total_points": int(result["total_value"])
        }
        
        return final_result
    except DatabaseError as de:
        raise DatabaseError(f"error {str(e)}")
    except Exception as e:
        raise RuntimeError(f"error {str(e)}")



    # Example usage:
# pin_data = [
#          "90123456EFGH", 
#          "72940183XYZW", 
#          "48390215ABCD", 
#          "48390215ABCK", 
#         "45678901IJKL" ,
#         "78901234WXYZ"
#     ]
# print(execute_pin_validation(pin_data))
# print(execute_query(query="UPDATE points SET status = 'not_scanned' WHERE status = 'scanned';"))



