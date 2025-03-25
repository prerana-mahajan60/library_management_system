import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

#Load .env Variables
load_dotenv()

#Environment Variables (With Default Values)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234mysql$&&*")
DB_NAME = os.getenv("DB_NAME", "library_db")

#Database Configuration
db_config = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME,
    'auth_plugin': 'mysql_native_password'
}

#Function to Get Database Connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return conn
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
    return None
