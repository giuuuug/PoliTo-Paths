import logging
from abc import ABC, abstractmethod

class DatabaseHandler(ABC):
    """
    Abstract base class for database connections.
    This class defines standard methods for database operations and can be extended
    for specific database types (e.g., PostgreSQL, MySQL, SQLite).
    """

    def __init__(self, config):
        """
        Initialize the database handler with a configuration dictionary.

        Args:
            config (dict): A dictionary containing database connection parameters.
        """
        self.config = config
        self.connection = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def connect(self):
        """
        Establish a connection to the database.
        This method must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Close the database connection.
        This method must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def execute_query(self, query, params=None):
        """
        Execute a query on the database.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): Parameters to pass to the query.

        Returns:
            list: The results of the query as a list of tuples.
        """
        pass

    def __enter__(self):
        """
        Context manager entry point. Automatically connects to the database.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context manager exit point. Automatically closes the database connection.
        """
        self.close()