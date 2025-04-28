from config import DB_URI
import psycopg2
from psycopg2 import Error



def get_connection():
    try:
        if 'DB_URI' not in globals():
            raise NameError("DB_URI is not defined as a global variable")

        connection = psycopg2.connect(DB_URI)
        # connection.timeout = 30
        
        if connection.closed:
            raise Exception("Failed to establish database connection")
            
        return connection
    
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise Exception(f"Database connection failed: {str(e)}")
    except NameError as e:
        print(f"Configuration error: {e}")
        raise

def execute_query(query, params=None, fetch_results=False):
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if not fetch_results:
            connection.commit()
            return cursor.rowcount
        else:
            results = cursor.fetchall()
            return results
    
    except Error as e:
        if connection:
            connection.rollback()
        print(f"Error executing query: {e}")
        raise Exception(f"Query execution failed: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
def execute_query_for_points(query, params=None, fetch_results=False):
    """
    Execute a SQL query with optional parameters, committing changes and optionally fetching results.
    
    Args:
        query (str): The SQL query to execute.
        params (tuple, optional): Parameters to pass to the query (e.g., a tuple of lists).
        fetch_results (bool): If True, fetch and return the query results; otherwise, return row count.
    
    Returns:
        list or int: Fetched results if fetch_results=True, otherwise the number of affected rows.
    
    Raises:
        Exception: If query execution fails, with the error message.
    """
    connection = None
    cursor = None
    
    try:
        # Establish database connection
        connection = get_connection()
        cursor = connection.cursor()
        
        # Execute the query with parameters if provided
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Handle queries that return results
        if fetch_results:
            results = cursor.fetchall()
            connection.commit()  # Commit to save updates
            return results
        else:
            connection.commit()  # Commit to save updates
            return cursor.rowcount  # Return number of affected rows
    
    except Error as e:
        # Roll back transaction on error
        if connection:
            connection.rollback()
        print(f"Error executing query: {e}")
        raise Exception(f"Query execution failed: {str(e)}")
    
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection:
            connection.close()



