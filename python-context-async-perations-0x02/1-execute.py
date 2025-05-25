import sqlite3

class ExecuteQuery:
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.connection = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        """Called when entering the context manager"""
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        if self.params:
            self.cursor.execute(self.query, self.params)
        else:
            self.cursor.execute(self.query)
        self.results = self.cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting the context manager"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

# Example usage of the context manager
with ExecuteQuery('users.db', "SELECT * FROM users WHERE age > ?", (25,)) as results:
    print("Users older than 25:", results) 