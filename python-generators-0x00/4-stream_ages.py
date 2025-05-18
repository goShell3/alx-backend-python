import mysql.connector
from mysql.connector import Error

def stream_user_ages():
    """Generator that streams user ages one by one from the database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='',  # Replace with your MySQL password
            database='ALX_prodev'
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row[0]  # Yield just the age value
            
    except Error as e:
        print(f"Database error: {e}")
        yield None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def calculate_average_age():
    """Calculate average age using the streaming generator"""
    age_generator = stream_user_ages()
    total = 0
    count = 0
    
    # Single loop to process all ages
    for age in age_generator:
        total += age
        count += 1
    
    return total / count if count > 0 else 0

if __name__ == "__main__":
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age:.2f}")