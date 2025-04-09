import psycopg2
from database.database_handler import DatabaseHandler
from utils.log import Log

class DatabasePostgreSQLPgRoutingSample(DatabaseHandler):
    """
    Classe per gestire la connessione al database specifico 'pg_routing_sample'.
    Estende la classe generica DatabaseHandler.
    """

    def __init__(self):
        # Configurazione specifica per il database 'pg_routing_sample'
        config = {
            "host": "192.168.1.10",
            "database": "pg_routing_sample",
            "user": "postgres",
            "password": "postgreSQLpwd",
            "port": 5432
        }
        super().__init__(config)  # Inizializza la classe base
        self.log = Log(self.__class__.__name__)  # Logger specifico per questa classe

    def connect(self):
        """
        Stabilisce la connessione al database 'pg_routing_sample'.
        """
        try:
            self.log.info("Connecting to the 'pg_routing_sample' database...")
            self.connection = psycopg2.connect(**self.config)
            self.log.info("Connection to 'pg_routing_sample' established successfully.")
        except Exception as e:
            self.log.error(f"Failed to connect to 'pg_routing_sample': {e}")
            raise

    def close(self):
        """
        Chiude la connessione al database.
        """
        if self.connection:
            self.connection.close()
            self.log.info("Connection to 'pg_routing_sample' closed.")

    def execute_query(self, query, params=None):
        """
        Esegue una query sul database 'pg_routing_sample'.

        Args:
            query (str): La query SQL da eseguire.
            params (tuple, optional): Parametri da passare alla query.

        Returns:
            list: Risultati della query come lista di tuple.
        """
        try:
            with self.connection.cursor() as cursor:
                self.log.info(f"Executing query on 'pg_routing_sample': {query}")
                cursor.execute(query, params)
                if cursor.description:  # Controlla se la query restituisce dati
                    results = cursor.fetchall()
                    self.log.info(f"Query executed successfully. Rows returned: {len(results)}")
                    return results
                self.connection.commit()
                self.log.info("Query executed successfully. No rows returned.")
                return []
        except Exception as e:
            self.log.error(f"Error executing query on 'pg_routing_sample': {e}")
            raise

