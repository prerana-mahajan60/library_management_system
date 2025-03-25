from main import app
from config import get_db_connection

#To Test Database Connection
try:
    connection = get_db_connection()
    if connection.is_connected():
        print("Database Connected Successfully!")
        connection.close()  # Close the connection after checking
    else:
        print("Database Connection Failed!")
except Exception as e:
    print(f" Error: {e}")

#For Running the Application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
