from flask import Blueprint, render_template, session, redirect
from database import get_db_connection  # ✅ Yeh sahi import hai!
profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")  # ✅ FIXED (Unauthorized users redirected)

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    user_id = session["user_id"]

    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        db.close()
        return redirect("/login")  # ✅ FIXED (If user not found, redirect)

    profile_data = {"user": user}  # ✅ (Store common user data)

    if user["role"] == "Admin":
        cursor.execute("SELECT COUNT(*) AS total_books FROM books")
        profile_data["admin_books_count"] = cursor.fetchone()["total_books"]

    else:
        cursor.execute("SELECT COUNT(*) AS borrowed_books FROM transactions WHERE user_id = %s AND action = 'borrow'", (user_id,))
        profile_data["student_borrowed_books"] = cursor.fetchone()["borrowed_books"]

    cursor.close()  # ✅ FIXED (Close cursor)
    db.close()      # ✅ FIXED (Close database)

    return render_template("student_profile.html", **profile_data)  # ✅ (Pass dynamic profile data)
