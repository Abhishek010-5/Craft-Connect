# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from datetime import datetime, timedelta
from api.login_api.queries import get_insert_or_update_otp_query, get_delete_otp_query, get_otp_query
from api.database import execute_query
import smtplib
from email.mime.text import MIMEText
import secrets
from api.config import MAIL, PASSWORD
from psycopg2 import DatabaseError

def generate_otp() -> str:
    """
    Generate a secure 6-character One-Time Password (OTP) using cryptographically secure random selection.

    The OTP consists of a random combination of lowercase letters (a-z), uppercase letters (A-Z),
    digits (0-9), and special characters (~!@#$%^&*()_+?). Each character is selected randomly
    from the full set of possible characters using the secrets module, ensuring cryptographic
    security suitable for authentication or verification purposes.

    Returns:
        str: A 6-character string representing the OTP.

    Example:
        >>> generate_otp()
        'kB7@mP'
    """
    lower_case = ''.join(chr(ord("a") + i) for i in range(26))
    upper_case = ''.join(chr(ord('A') + i) for i in range(26))
    nums = "0123456789"
    special_char = "~!@#$%^&*()_+?"
    
    all_char = lower_case + upper_case + nums + special_char
    
    return ''.join(secrets.choice(all_char) for _ in range(6))

def send_otp(email: str, otp: str) -> bool:
    """
    Sends an OTP to the specified email address.

    Args:
        email (str): The recipient's email address.
        otp (str): The OTP to be sent.

    Returns:
        bool: True if the email was sent successfully, False otherwise.

    Sends the OTP via email using SMTP with Gmail's SMTP server.
    """
    sender_email = MAIL
    sender_password = PASSWORD
    subject = "Your OTP Code"
    body = f"Your OTP code is {otp}. It is valid for 10 minutes."

    # Create MIMEText object for plain text email
    message = MIMEText(body, "plain")
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
    
def send_otp_to_db(email: str, otp: str) -> bool:
    """
    Store or update OTP in database with 2 minutes validity.
    
    Args:
        email (str): User's email address
        otp (str): One-time password to store
    
    Returns:
        bool: True if operation successful, False otherwise
    """
    try:
        # Get current time
        current_time = datetime.now()
        
        # Calculate expiry time (2 minutes from now)
        expiry_time = current_time + timedelta(minutes=10)
        
        # Prepare query parameters
        params = {
            "email": email,
            "otp": otp,
            "created": current_time,
            "valid_till": expiry_time
        }
        
        # Get the UPSERT query
        query = get_insert_or_update_otp_query()
        
        # Execute the query and get result
        result = execute_query(query, params)
        
        # Check if operation was successful
        return bool(result)  
        
    except Exception as e:
        print(f"Error storing OTP: {str(e)}")
        return False

def get_otp(email: str) -> dict:
    """Retrieves OTP details for a given email from the database.

    Args:
        email (str): The email address to query OTP details for.

    Returns:
        dict: A dictionary containing OTP details with keys 'otp' and 'valid_till',
              or None if no OTP is found.
              Example: {'otp': '123456', 'valid_till': 1634567890}

    Raises:
        RuntimeError: If an error occurs during query execution or database access.
    """
    try:
        query = get_otp_query()
        params = {"email": email}
        response = execute_query(query, params, fetch_results=True)
        
        if not response or response == []:
            return None
        otp_details = {
            "otp": response[0][0],
            "valid_till": response[0][1]
        }
        
        return otp_details
    except Exception as e:
        raise RuntimeError(str(e))

def delete_otp(email: str) -> bool:
    """Deletes OTP details for a given email from the database.

    Args:
        email (str): The email address whose OTP details should be deleted.

    Returns:
        bool: True if the OTP was successfully deleted, False otherwise.

    Raises:
        DatabaseError: If a database-specific error occurs during query execution.
        RuntimeError: If any other unexpected error occurs during execution.
    """
    try:
        query = get_delete_otp_query()
        params = {"email": email}
        response = execute_query(query, params)
        
        return response > 0
    except DatabaseError as dber:
        raise DatabaseError(str(dber))
    except Exception as e:
        raise RuntimeError(str(e))
    
