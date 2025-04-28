def get_user_password_query()->str:
    """
    Returns a PostgreSQL query to retrieve the password for a user based on their email.

    The query selects the password from the 'users' table where the email matches the provided email parameter.

    :return: PostgreSQL query string
    """
    return """
        SELECT password FROM users
        WHERE email = %(email)s
"""

def get_user_exists_query()->str:
    """
    Returns a PostgreSQL query to check if a user exists based on their email.

    The query selects the email from the 'users' table where the email matches the provided email parameter.

    :return: PostgreSQL query string
    """
    return """
        SELECT email FROM users
        WHERE email = %(email)s
"""

def get_insert_user_query()->str:
    """
    Returns a PostgreSQL query to insert a new user into the 'users' table.

    The query inserts the name, email, and password into the 'users' table using the provided parameters.

    :return: PostgreSQL query string
    """
    return """
        INSERT INTO users(name, email, password)
        VALUES(%(name)s, %(email)s, %(password)s)
"""

def get_insert_user_to_pending_query()->str:
    """
    Returns a PostgreSQL query to insert a new pending signup into the 'pending_signups' table.

    The query inserts the name, email, and password into the 'pending_signups' table using the provided parameters.

    :return: PostgreSQL query string
    """
    return """
        INSERT INTO pending_signups(name, email, password)
        VALUES(%(name)s, %(email)s, %(password)s)
"""

def get_user_status_in_pending_signups_query()->str:
    """
    Returns a PostgreSQL query to retrieve the status of a user from the 'pending_signups' table.

    The query selects the status from the 'pending_signups' table where the email matches the provided email parameter.

    :return: PostgreSQL query string
    """
    return """
        SELECT status FROM pending_signups
        WHERE email = %(email)s
"""

def update_user_email_status_query()->str:
    """
    Returns a PostgreSQL query to update the email status in the 'pending_signups' table.

    The query updates the 'email_status' to 'verified' for the record in the 'pending_signups' table 
    where the email matches the provided email parameter.

    :return: PostgreSQL query string
    """
    return """
        UPDATE pending_signups 
        SET email_status = 'verified'
        WHERE email = %(email)s;
"""

def get_email_status_query()->str:
    """
    Returns a PostgreSQL query to retrieve the email status from the 'pending_signups' table.

    The query selects the 'email_status' from the 'pending_signups' table where the email matches 
    the provided email parameter.

    :return: PostgreSQL query string
    """
    return """
        SELECT email_status
        FROM pending_signups
        WHERE email = %(email)s;
"""

def get_insert_or_update_otp_query() -> str:
    """
    Returns a PostgreSQL query to either insert or update an OTP in the 'otp_verification' table.

    The query uses a DO block to check if an OTP exists for the given email. If it exists, it updates 
    the OTP, creation time, and validity period; if not, it inserts a new record with the provided 
    email, OTP, creation time, and validity period.

    :return: PostgreSQL query string
    """
    return """
        DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM otp_verification WHERE email = %(email)s) THEN
                    UPDATE otp_verification
                    SET otp = %(otp)s,
                        created = %(created)s,  
                        valid_till = %(valid_till)s
                    WHERE email = %(email)s;
                ELSE
                    INSERT INTO otp_verification (email, otp, created, valid_till)
                    VALUES (%(email)s, %(otp)s, %(created)s, %(valid_till)s);
                END IF;
            END;
        $$;
    """

def get_otp_query()->str:
    """
    Returns a PostgreSQL query to retrieve the OTP and its validity period from the 'otp_verification' table.

    The query selects the OTP and valid_till fields from the 'otp_verification' table where the email 
    matches the provided email parameter.

    :return: PostgreSQL query string
    """
    return """
        SELECT otp,valid_till
        FROM otp_verification
        WHERE email = %(email)s
"""

def get_reset_password_query()->str:
    """
    Returns a PostgreSQL query to reset a user's password in the 'users' table.

    The query updates the password for the user in the 'users' table where the email matches the 
    provided email parameter and the email is not NULL.

    :return: PostgreSQL query string
    """
    return """
        UPDATE users 
        SET password = %(password)s
        WHERE email = %(email)s 
        AND email IS NOT NULL
"""

def get_delete_otp_query()->str:
    """
    Returns a PostgreSQL query to delete an OTP entry from the 'otp_verification' table.

    The query deletes the record from the 'otp_verification' table where the email matches the 
    provided email parameter.

    :return: PostgreSQL query string
    """
    return """
        DELETE FROM otp_verification
        WHERE email = %(email)s
"""

    