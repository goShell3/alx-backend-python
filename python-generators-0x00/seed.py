import mysql.connector
import uuid
import csv
from mysql.connector import Error

def connect_db():
    """Connect to the MySQL database server"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password=''   # Replace with your MySQL password
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Create the database ALX_prodev if it doesn't exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created successfully or already exists")
    except Error as e:
        print(f"Error creating database: {e}")

def connect_to_prodev():
    """Connect to the ALX_prodev database in MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='',  # Replace with your MySQL password
            database='ALX_prodev'
        )
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None

def create_table(connection):
    """Create table user_data if it doesn't exist with required fields"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id BINARY(16) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(3,1) NOT NULL,
            UNIQUE INDEX email_index (email)
        )
        """)
        print("Table user_data created successfully or already exists")
    except Error as e:
        print(f"Error creating table: {e}")

def read_csv_data(filename):
    """Read data from CSV file and prepare for insertion"""
    data = []
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Convert UUID string to binary for storage
            user_uuid = uuid.UUID(row['user_id']).bytes if 'user_id' in row else uuid.uuid4().bytes
            data.append((
                user_uuid,
                row['name'],
                row['email'],
                float(row['age'])
            ))
    return data

def insert_data(connection, data):
    """Insert data into the database if it doesn't exist"""
    try:
        cursor = connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM user_data")
        if cursor.fetchone()[0] > 0:
            print("Data already exists in the table")
            return
        
        # Insert new data
        insert_query = """
        INSERT INTO user_data (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(insert_query, data)
        connection.commit()
        print(f"Inserted {cursor.rowcount} records successfully")
    except Error as e:
        print(f"Error inserting data: {e}")
    finally:
        if connection.is_connected():
            cursor.close()

def main():
    # Step 1: Connect to MySQL server
    connection = connect_db()
    if not connection:
        return
    
    # Step 2: Create database
    create_database(connection)
    connection.close()
    
    # Step 3: Connect to ALX_prodev database
    connection = connect_to_prodev()
    if not connection:
        return
    
    # Step 4: Create table
    create_table(connection)
    
    # Step 5: Read and insert data
    data = read_csv_data('user_data.csv')  # Replace with your CSV file path
    insert_data(connection, data)
    
    # Clean up
    connection.close()
    print("Database setup complete")

if __name__ == "__main__":
    main()