from flask import Blueprint, render_template, session, redirect
from database import get_db_connection  # ✅ Yeh sahi import hai!


dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    db = get_db_connection()  # ✅ connect_db() hata, yeh use kar
    if db is None:
        return "Database Connection Failed", 500  # ❌ Error handle kar

    if "user_id" not in session:
        return redirect("/login")  # ✅ FIX: Redirect unauthenticated users

    user_id = session["user_id"]
    role = session.get("role", "Student")  # ✅ FIX: Default role if missing

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        # ✅ FIX: Corrected column name from `id` to `user_id` (matches DB structure)
        cursor.execute("SELECT name FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        user_name = user["name"] if user else "Guest"  # ✅ FIX: Handle missing user
    except Exception as e:
        print(f"Database Error: {e}")  # ✅ LOG: Print error for debugging
        user_name = "Guest"  # ✅ Ensure user_name is set even in case of error
    finally:
        cursor.close()
        db.close()

    return render_template("dashboard.html", user_name=user_name, role=role)

@dashboard_bp.route("/admin_dashboard")
def admin_dashboard():
    if "user_id" not in session:
        return redirect("/login")  # ✅ Redirect if not logged in

    return render_template("admin_dashboard.html")  # ✅ Yeh file `templates` folder me honi chahiye

@dashboard_bp.route("/student_dashboard")
def student_dashboard():
    if "user_id" not in session:
        return redirect("/login")  # ✅ Redirect if not logged in

    return render_template("student_dashboard.html")  # ✅ Yeh bhi `templates` me honi chahiye