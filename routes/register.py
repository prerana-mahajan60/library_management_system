import bcrypt
import mysql.connector
from database import get_db_connection  # ✅ Sahi import

def register_user(name, email, password, role):
    try:
        conn = get_db_connection()  # ✅ Database connection leke aao
        if conn is None:
            print("❌ Database connection failed!")
            return False

        cursor = conn.cursor()  # ✅ Cursor banao

        # ✅ Password Hashing
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # ✅ Insert Query
        query = "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)"
        values = (name, email, hashed_password, role)
        cursor.execute(query, values)

        conn.commit()  # ✅ Save to DB
        print("✅ User Registered Successfully!")

        cursor.close()
        conn.close()  # ✅ Connection close karna mat bhool

        return True

    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return False

