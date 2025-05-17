import psycopg2
from database.database_handler import DatabaseHandler
from utils.log import Log

class DatabasePostgreSQLPolitoPaths(DatabaseHandler):
    """
    Classe per gestire la connessione al database specifico 'polito_paths_db'.
    Estende la classe generica DatabaseHandler.
    """

    def __init__(self):
        config = {
            "host": "192.168.1.10",
            "database": "polito_paths_db",
            "user": "postgres",
            "password": "postgreSQLpwd",
            "port": 5432
        }
        super().__init__(config)  
        self.log = Log(self.__class__.__name__)  

    def connect(self):
        """
        Stabilisce la connessione al database 'polito_paths_db'.
        """
        try:
            self.connection = psycopg2.connect(**self.config)
        except Exception as e:
            self.log.error(f"Failed to connect to 'polito_paths_db': {e}")
            raise

    def close(self):
        """
        Chiude la connessione al database.
        """
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        """
        Esegue una query sul database 'polito_paths_db'.

        Args:
            query (str): La query SQL da eseguire.
            params (tuple, optional): Parametri da passare alla query.

        Returns:
            list: Risultati della query come lista di tuple.
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description: 
                    results = cursor.fetchall()
                    return results
                self.connection.commit()
                return []
        except Exception as e:
            self.log.error(f"Error executing query on 'polito_paths_db': {e}")
            raise

