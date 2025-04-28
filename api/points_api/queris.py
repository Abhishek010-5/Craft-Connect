def get_points_query() -> str:
    """
    Returns a SQL query to retrieve the points for a user based on their email.
    
    Returns:
        str: SQL query string.
    """
    return """
        SELECT points
        FROM user_points
        WHERE email = %(email)s;
    """

def update_user_point_query() -> str:
    """
    Returns a SQL query to update the points for a user based on their email.
    
    Returns:
        str: SQL query string.
    """
    return """
        UPDATE user_points
        SET points = %(points)s
        WHERE email = %(email)s;
    """

def insert_points_data_query() -> str:
    """
    Returns a SQL query to insert points data into the points table.
    
    Returns:
        str: SQL query string.
    """
    return """
        INSERT INTO points(points_code, status, points_value, expiry_date)
        VALUES(%(points)s, %(status)s, %(points_value)s, %(expiry_date)s);
    """

def get_pin_validate_query() -> str:
    """
    Returns a SQL query to validate pin codes, checking their status and updating them if valid.
    
    The query processes an array of pin codes and input dates, determines their validity based on 
    status and expiry date, updates valid pins to 'scanned', and returns their status and point values.
    
    Returns:
        str: SQL query string.
    """
    PIN_VALIDATION_QUERY = """
        WITH input AS (
            SELECT points_code
            FROM unnest(%s::text[]) AS points_code
        ),
        to_update AS (
            SELECT p.points_code
            FROM points p
            JOIN input i ON p.points_code = i.points_code
            WHERE p.status = 'not_scanned' AND p.expiry_date >= CURRENT_DATE
        ),
        updated AS (
            UPDATE points p
            SET status = 'scanned'
            FROM to_update tu
            WHERE p.points_code = tu.points_code
            RETURNING p.points_code, p.points_value
        )
        SELECT 
            i.points_code,
            CASE
                WHEN p.points_code IS NULL THEN 'not_in_system'
                WHEN u.points_code IS NOT NULL THEN 'success'
                WHEN p.status = 'scanned' THEN 'already_scanned'
                WHEN p.expiry_date < CURRENT_DATE THEN 'expired'
                ELSE 'invalid'
            END AS status,
            COALESCE(p.points_value, 0) AS points_value
        FROM input i
        LEFT JOIN points p ON p.points_code = i.points_code
        LEFT JOIN updated u ON i.points_code = u.points_code;
"""
    return PIN_VALIDATION_QUERY

params = [
    {'points': '48390215ABCD', 'status': 'not_scanned', 'points_value': 10, 'expiry_date': '2025-01-01'},  # Expired
    {'points': '72940183XYZW', 'status': 'not_scanned', 'points_value': 15, 'expiry_date': '2025-06-01'},  # Future
    {'points': '13579024PQRS', 'status': 'not_scanned', 'points_value': 5, 'expiry_date': '2024-12-31'},   # Expired
    {'points': '24680135LMNO', 'status': 'not_scanned', 'points_value': 20, 'expiry_date': '2025-09-20'},  # Future
    {'points': '98765432EFGH', 'status': 'not_scanned', 'points_value': 10, 'expiry_date': '2025-03-15'},  # Expired
    {'points': '45678901IJKL', 'status': 'not_scanned', 'points_value': 15, 'expiry_date': '2026-03-22'},  # Future
    {'points': '12345678STUV', 'status': 'not_scanned', 'points_value': 5, 'expiry_date': '2024-11-01'},   # Expired
    {'points': '78901234WXYZ', 'status': 'not_scanned', 'points_value': 20, 'expiry_date': '2025-12-25'},  # Future
    {'points': '34567890ABCD', 'status': 'not_scanned', 'points_value': 10, 'expiry_date': '2025-08-15'},  # Future
    {'points': '90123456EFGH', 'status': 'not_scanned', 'points_value': 15, 'expiry_date': '2026-02-14'}   # Future
]
