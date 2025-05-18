import mysql.connector
from mysql.connector import Error

def stream_users_in_batches(batch_size):
    """Generator function that streams users in batches from the database"""
    try:
        # Establish database connection
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='',  # Replace with your MySQL password
            database='ALX_prodev'
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Execute query and stream results in batches
        cursor.execute("SELECT * FROM user_data")
        
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            # Convert binary UUID to string for each user in batch
            for user in batch:
                if 'user_id' in user and isinstance(user['user_id'], bytes):
                    user['user_id'] = user['user_id'].hex()
            yield batch
            
    except Error as e:
        print(f"Database error: {e}")
        yield None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def batch_processing(batch_size):
    """Process batches to filter users over age 25"""
    batch_generator = stream_users_in_batches(batch_size)
    
    for batch in batch_generator:
        if batch is None:
            continue
            
        # Filter users over 25 in the current batch
        filtered_users = [user for user in batch if user['age'] > 25]
        yield filtered_users

# Example usage:
if __name__ == "__main__":
    # Process users in batches of 10
    processor = batch_processing(10)
    
    # First loop: iterate through batches
    for batch_num, users_over_25 in enumerate(processor, 1):
        print(f"\nBatch {batch_num} - Users over 25:")
        
        # Second loop: process users in current batch
        for user in users_over_25:
            print(f"ID: {user['user_id']}, Name: {user['name']}, Age: {user['age']}")
            
            
yield 