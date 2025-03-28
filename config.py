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

#Environment Variables with Fallback Defaults
DB_HOST = os.getenv("DB_HOST", "dpg-cvjbu9emcj7s73eb6o90-a")
DB_USER = os.getenv("DB_USER", "library_db_0l2b_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "0NgHIcyC4q344jk5aGMrlgV13MHano6N")
DB_NAME = os.getenv("DB_NAME", "library_db_0l2b")
DB_PORT = os.getenv("DB_PORT", "5432")

#Print Variables to Verify (For Debugging)
print(f"DB_HOST: {DB_HOST}")
print(f"DB_USER: {DB_USER}")
print(f"DB_NAME: {DB_NAME}")
print(f"DB_PORT: {DB_PORT}")

#Database Configuration Dictionary
db_config = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "dbname": DB_NAME,
    "port": DB_PORT,
}

#Function to Get Database Connection
def get_db_connection():
    try:
        #Establish Connection to PostgreSQL
        connection = psycopg2.connect(**db_config)
        print("PostgreSQL Database Connection Successful!")
        return connection
    except OperationalError as err:
        print(f"PostgreSQL Connection Error: {err}")
        return None
