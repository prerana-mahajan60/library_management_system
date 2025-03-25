import mysql.connector
from database import get_db_connection


def create_users_table():
    connection = get_db_connection()

    if connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()
    else:
        print("Error: Could not connect to the database!")