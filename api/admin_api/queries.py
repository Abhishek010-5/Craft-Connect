def get_user_from_pending_signups_query() -> str:
    """Retrieve verified users from pending_signups table."""
    return """
    SELECT id, name, email, email_status, status
    FROM pending_signups
    WHERE email_status = 'verified'
""".strip()

def update_user_status_query() -> str:
    """Update status of a user in pending_signups table based on email."""
    return """
        UPDATE pending_signups
        SET status = %(status)s
        WHERE email = %(email)s;
"""

def insert_user_to_users_query():
    """Insert a new user into the users table."""
    return """
        INSERT INTO users(name, email, password)
        VALUES( %(name)s, %(email)s, %(password)s);
    """

def delete_approved_user():
    """Delete a user from pending_signups table based on email."""
    return """
        DELETE FROM pending_signups 
        WHERE email = %(email)s;
    """
    
def get_approved_users_query() -> str:
    """Retrieve approved and verified users from pending_signups table based on email."""
    return """
        SELECT name, email, password 
        FROM pending_signups 
        WHERE email = %(email)s AND status = 'approved' AND email_status = 'verified' ;
"""

def delete_user_query() -> str:
    """Delete a user from users table based on email."""
    return """
        DELETE FROM users
        WHERE email = %(email)s
"""

def insert_user_to_user_points_query() -> str:
    """Insert a user's email into user_points table."""
    return """
        INSERT INTO user_points (email)
        VALUES (%(email)s);
    """

def insert_scheme_query() -> str:
    """Insert a new scheme into the scheme table."""
    return """
        INSERT INTO scheme (scheme_title, scheme_valid_from, scheme_valid_to, scheme_perks, points)
        VALUES(%(scheme_title)s, %(scheme_valid_from)s, %(scheme_valid_to)s, %(scheme_perks)s, %(points)s);
"""

def delete_scheme_query() -> str:
    """Delete a scheme from scheme table based on scheme title."""
    return """
        DELETE FROM scheme
        WHERE scheme_title = %(scheme_title)s;
    """

def update_scheme_query() -> str:
    """Update scheme details in scheme table based on scheme title, with optional fields."""
    return """
        UPDATE scheme 
        SET 
            scheme_valid_from = COALESCE(%(scheme_valid_from)s, scheme_valid_from),
            scheme_valid_to = COALESCE(%(scheme_valid_to)s, scheme_valid_to),
            scheme_perks = COALESCE(%(scheme_perks)s, scheme_perks),
            points = COALESCE(%(points)s, points)
        WHERE scheme_title = %(scheme_title)s;
"""

def get_scheme_query() -> str:
    """Retrieve all schemes from the scheme table."""
    return """
        SELECT * FROM scheme;
"""

def get_insert_admin_query() -> str:
    """
    Returns the SQL query to insert a new admin user into the database.

    Returns:
        str: The SQL query string for inserting an admin with email and password.
    """
    return """
        INSERT INTO admin (email, password) 
        VALUES (%(email)s, %(password)s);
"""

def get_admin_password_query() -> str:
    """
    Returns the SQL query to retrieve the password of an admin user by email.

    Returns:
        str: The SQL query string for selecting the password of an admin by email.
    """
    return """
        SELECT password FROM admin
        WHERE email = %(email)s;
"""

def get_admin_exists_query() -> str:
    """
    Returns the SQL query to check if an admin user exists by email.

    Returns:
        str: The SQL query string for checking the existence of an admin by email.
    """
    return """
        SELECT 1 FROM admin
        WHERE email = %(email)s;
"""

def delete_admin_query() -> str:
    """
    Returns the SQL query to delete an admin user by email.

    Returns:
        str: The SQL query string for deleting an admin by email.
    """
    return """
        DELETE FROM admin 
        WHERE email = %(email)s;
"""

def update_user_details_query() -> str:
    return """
        UPDATE users u
        JOIN user_points up ON u.email = up.email
        SET u.email = %(new_email)s, u.name = %(name)s, up.points = %(points)s
        WHERE u.email = %(email)s;
    """