import mysql.connector
from mysql.connector import Error

def paginate_users(page_size, offset):
    """Fetch a specific page of users from the database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='',  # Replace with your MySQL password
            database='ALX_prodev'
        )
        
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
        cursor.execute(query, (page_size, offset))
        
        page = cursor.fetchall()
        # Convert binary UUID to string for each user
        for user in page:
            if 'user_id' in user and isinstance(user['user_id'], bytes):
                user['user_id'] = user['user_id'].hex()
        
        return page
    except Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def lazy_paginate(page_size):
    """Generator that lazily loads paginated user data"""
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:  # No more users to fetch
            break
        yield page
        offset += page_size

# Example usage:
if __name__ == "__main__":
    # Create generator for pages of 5 users
    user_pages = lazy_paginate(5)
    
    # Single loop to process pages as needed
    for page_num, page in enumerate(user_pages, 1):
        print(f"\nPage {page_num}:")
        for user in page:
            print(f"ID: {user['user_id']}, Name: {user['name']}, Age: {user['age']}")