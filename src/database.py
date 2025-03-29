# database.py
import psycopg2
from logger import Logger
class Database:
    def __init__(self, logger:Logger):
        self.logger = logger
        self.config = {
            "host": "192.168.1.10",
            "database": "polito_paths_db",
            "user": "postgres",
            "password": "postgreSQLpwd",
            "port": 5432
        }
        
    def execute_query(self, query):
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall() or []
        except Exception as e:
            self.logger.log_bot_critical(f"DB ERROR: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
       