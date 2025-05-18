import mysql.connector
from mysql.connector import Error

def stream_users():
    """Generator function that streams users from the database one by one"""
    try:
        # Establish database connection
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='',  # Replace with your MySQL password
            database='ALX_prodev'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Execute query and stream results
        cursor.execute("SELECT * FROM user_data")
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            # Convert binary UUID to string if needed
            if 'user_id' in row and isinstance(row['user_id'], bytes):
                row['user_id'] = row['user_id'].hex()
            yield row
            
    except Error as e:
        print(f"Database error: {e}")
        yield None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# Example usage:
if __name__ == "__main__":
    user_generator = stream_users()
    for user in user_generator:
        print(user)