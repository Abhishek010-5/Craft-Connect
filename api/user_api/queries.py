def get_users_detail_query() -> str:
    """
    Returns a SQL query to retrieve detailed information for a specific user by email.

    The query selects the user's ID, name, email, and points by joining the `users` and `user_points` tables.
    It filters results based on the provided email parameter.

    Returns:
        str: A SQL query string with a placeholder for the email parameter (%(email)s).
    """
    return """
        SELECT u.id, u.name, up.points, u.email
        FROM users u
        LEFT JOIN user_points up ON u.email = up.email
        WHERE u.email = %(email)s;
    """

def get_top_users_query() -> str:
    """
    Returns a SQL query to retrieve the top users based on their points.

    The query selects the user's ID, name, email, and points by joining the `users` and `user_points` tables.
    Results are ordered by points in descending order and limited by the provided limit parameter.

    Returns:
        str: A SQL query string with a placeholder for the limit parameter (%(limit)s).
    """
    return """
        SELECT u.id, u.name, u.email, up.points
        FROM users u
        JOIN user_points up ON u.email = up.email
        ORDER BY up.points DESC
        LIMIT %(limit)s;
    """

def get_users_query() -> str:
    """
    Returns a SQL query to retrieve a list of users with basic information.

    The query selects the user's ID, name, and email from the `users` table, with a limit on the number of results.

    Returns:
        str: A SQL query string with a placeholder for the limit parameter (%(limit)s).
    """
    return """
        SELECT u.id, u.name, u.email up.points 
        FROM users u
        JOIN user_points up ON u.email = up.email
        LIMIT %(limit)s;
    """

def get_scheme_query() -> str:
    """
    Returns a SQL query to retrieve all schemes.

    The query selects all columns from the `schemes` table.

    Returns:
        str: A SQL query string.
    """
    return """
        SELECT * FROM schemes;
    """

def get_applied_scheme() -> str:
    """
    Returns a SQL query to retrieve applied schemes with their titles and statuses.

    The query selects the scheme title and status from the `pending` table.

    Returns:
        str: A SQL query string.
    """
    return """
        SELECT scheme_title, scheme_status FROM schemes_redemption WHERE email = %(email)s;
    """

def insert_scheme_query() -> str:
    """
    Returns a SQL query to insert a new scheme redemption record.

    The query inserts a record into the `schemes_redemption` table with the provided name, email, and scheme status.

    Note: The query contains a typo ('shcemes_redemption' should be 'schemes_redemption') and incorrect syntax
    ('VALUES ... SET' is invalid). It should be corrected to use proper INSERT syntax.

    Returns:
        str: A SQL query string with placeholders for name, email, and scheme_status
             (%(name)s, %(email)s, %(scheme_status)s).
    """
    return """
        INSERT INTO schemes_redemption (name, email, scheme_id)
        VALUES (%(name)s, %(email)s, %(scheme_id)s);
    """
    
def get_scheme_valid_to_query()->str:
    return """
        SELECT scheme_valid_to FROM scheme
        WHERE scheme_id = %(id)s;
"""

def scheme_already_applied_query()->str:
    return """
        SELECT EXISTS (SELECT 1 FROM schemes_redemption WHERE email = %(email)s);
"""

def scheme_status_query()->str:
    return """
        SELECT s.scheme_title, sr.scheme_status
        FROM scheme s
        LEFT JOIN schemes_redemption sr ON s.scheme_id = sr.scheme_id
        WHERE sr.email = %(email)s;
"""

def get_points_required_for_scheme_query() -> str:
    """
    Returns the SQL query to retrieve the points required for a specific scheme.
    Returns:
        str: The SQL query string to fetch points from the scheme table based on scheme_id.
    """
    return"""
        SELECT points
        FROM scheme
        WHERE scheme_id = %(scheme_id)s;
"""