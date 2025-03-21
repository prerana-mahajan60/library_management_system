import mysql.connector

#Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234mysql$&**',
    'database': 'library_db',
    'auth_plugin': 'mysql_native_password'
}

#Function to Get Database Connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            return conn
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
    return None
