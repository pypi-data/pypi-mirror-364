
class BaseConnector:
    """Base class for database connectors."""
    def __init__(self, host, port, user, password, database=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish a connection to the database."""
        raise NotImplementedError("Subclasses should implement this method.")
        
    def get_cursor(self):
        """Get a cursor from the connection."""
        if self.cursor is None:
            self.cursor = self.connection.cursor()
        return self.cursor

    def commit(self):
        """Commit the current transaction."""
        if self.connection:
            self.connection.commit()

    def rollback(self):
        """Rollback the current transaction."""
        if self.connection:
            self.connection.rollback()
        
    def close(self):
        """Close the cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        """Execute a query and return the results."""
        cursor = self.get_cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.fetchall()
    
    def fetch_all(self, query, params=None):
        """Fetch all records from the database."""
        cursor = self.get_cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        """Fetch a single record from the database."""
        cursor = self.get_cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def autocommit(self, value: bool):
        """Set autocommit mode for the connection."""
        if self.connection:
            self.connection.autocommit = value
        else:
            raise RuntimeError("Connection not established. Cannot set autocommit.")
        
    

    def test_connection(self):
        """Test the connection to the database."""
        try:
            print("Testing connection...")
            self.connection = self.connect()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
        
    def test_query(self):
        """Test a simple query to check if the connection is working."""
        try:
            query = "select 1+1".strip()
            params = None
            print("Testing query execution...", query)
            cursor = self.get_cursor()
            cursor.execute(query, params)
            return True
        except Exception as e:
            print(f"Query failed: {e}")
            return False
    
    # context manager methods
    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context related to this object."""
        print(f"Exiting context manager, closing connection... for database {self.database} exe_type={exc_type} exc_val={exc_val} exc_tb={exc_tb}")
        self.close()
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def __str__(self):
        """String representation of the connector."""
        return f"Connector(user={self.user}, host={self.host}, port={self.port}, database={self.database})"
    
    def __repr__(self):
        """Official string representation of the connector."""
        return self.__str__()   
    
    def __del__(self):
        """Destructor to ensure resources are cleaned up."""
        if self.connection:
            self.close()
            self.connection = None
            self.cursor = None
            print(f"Connection to database {self.database} closed.")
