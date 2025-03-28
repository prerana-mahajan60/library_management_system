import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
import os
import sys
import io

#Force UTF-8 Encoding for Console Output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

#Load .env Variables
load_dotenv()

#Environment Variables (With Default Values)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "P4545post@*#")
DB_NAME = os.getenv("DB_NAME", "library_db")
DB_PORT = os.getenv("DB_PORT", "5432")

#Print Variables to Verify
print("DB_HOST:", DB_HOST)
print("DB_USER:", DB_USER)
print("DB_PASSWORD:", DB_PASSWORD)
print("DB_NAME:", DB_NAME)
print("DB_PORT:", DB_PORT)

#Database Configuration
db_config = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'dbname': DB_NAME,
    'port': DB_PORT
}

#Function to Get Database Connection
def get_db_connection():
    try:
        connection = psycopg2.connect(**db_config)
        print("PostgreSQL Database Connection Successful!")
        return connection
    except OperationalError as err:
        print(f"PostgreSQL Connection Error: {err}")
        return None
