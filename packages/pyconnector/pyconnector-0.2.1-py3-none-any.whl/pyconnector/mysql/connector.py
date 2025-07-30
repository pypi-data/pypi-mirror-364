from mysql import connector
from core.base_connector import BaseConnector

class MySqlConnector(BaseConnector):
    def __init__(self, user: str, password: str, host: str = 'localhost', port: int = 3306, database: str=None):
        if not user or not password or not host:
            raise ValueError("user, password, host are required.")
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database if database else "test"
        self.connection = self.connect()
        self.cursor = self.connection.cursor() if self.connection else None
        super().__init__(user, password, host, port, database)

    def connect(self):
        """Establish a connection to the MySQL database."""
        if self.database is None:
            self.database = "test"
        return connector.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            database=self.database
        )
        


   

  

