import psycopg2
from psycopg2 import OperationalError
import logging

# Logging configuration for the database module
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Creates and returns a PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(
            host="192.168.1.10",
            database="polito_paths_db",
            user="postgres",
            password="postgreSQLpwd",
            port="5432"
        )
        logger.warning("Database connection established successfully")
        return conn
    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        return None

def execute_query(query):
    """
    Executes an SQL query and returns:
    - Results as list of tuples on success
    - Error string on failure
    """
    conn = get_db_connection()
    if not conn:
        return "❌ Database connection error"

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            return results if results else []
            
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return f"❌ Error executing query: {e}"
    finally:
        conn.close()