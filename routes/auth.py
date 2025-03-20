from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from flask_bcrypt import Bcrypt

auth_bp = Blueprint("auth", __name__, template_folder="templates")

# ✅ Initialize Bcrypt
bcrypt = Bcrypt()

# ---------------------------------------------Admin-------------------------------------------------------
# ✅ Admin Register
@auth_bp.route("/admin_register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        gender = request.form["gender"].strip().lower()  # ✅ Corrected gender fetching

        # ✅ Check if gender is empty
        if not gender:
            flash("❌ Please select your gender!", "danger")
            return redirect(url_for("auth.admin_register"))

        # ✅ Hash the password securely
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # ✅ Get DB connection
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # ✅ Check if email already exists in the `admin` table
            cursor.execute("SELECT email FROM admin WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("❌ Error: Email already exists!", "danger")
                return redirect(url_for("auth.admin_register"))

            # ✅ Insert new admin record with gender included
            cursor.execute(
                """
                INSERT INTO admin (admin_name, email, password, gender)
                VALUES (%s, %s, %s, %s)
                """,
                (name, email, hashed_password, gender),
            )
            connection.commit()

            flash("✅ Admin Registered Successfully! Please log in.", "success")
            return redirect(url_for("auth.admin_login"))

        except mysql.connector.Error as e:
            connection.rollback()
            flash(f"❌ Database Error: {str(e)}", "danger")

        finally:
            cursor.close()
            connection.close()

    return render_template("admin_register.html")


# ✅ Admin Login
@auth_bp.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        # ✅ Get DB connection
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            # ✅ Check if admin exists with given email
            cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
            admin = cursor.fetchone()

        except mysql.connector.Error:
            flash("❌ Database error occurred! Please try again.", "danger")
            admin = None

        finally:
            cursor.close()
            connection.close()

        # ✅ If admin record is found
        if admin:
            db_password = admin["password"]

            # ✅ Check password validity
            if db_password and bcrypt.check_password_hash(db_password, password):
                session.clear()
                session["admin_id"] = admin["admin_id"]  # Corrected admin_id
                session["admin_name"] = admin["admin_name"]  # ✅ Corrected name assignment
                session["role"] = "Admin"

                flash("✅ Login Successful!", "success")

                # ✅ Redirect to correct admin home route
                return redirect(url_for("admin.admin_home"))

            else:
                flash("❌ Incorrect password or credentials!", "danger")

        else:
            flash("❌ Invalid Email or Password!", "danger")

    return render_template("admin_login.html")


# ------------------------------------Student--------------------------------------------------

# ✅ Student Register
@auth_bp.route("/student_register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        course = request.form.get("course", "").strip()
        gender = request.form.get("gender", "").strip()

        if not name or not email or not password or not course or not gender:
            flash("❌ All fields are required!", "danger")
            return redirect(url_for("auth.student_register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT email FROM student WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("❌ Email already exists!", "danger")
                return redirect(url_for("auth.student_register"))

            cursor.execute(
                """
                INSERT INTO student (email, password, course, gender, name) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (email, hashed_password, course, gender, name),
            )
            connection.commit()

            flash("✅ Registration successful! Please log in.", "success")
            return redirect(url_for("auth.student_login"))

        except mysql.connector.Error as e:
            connection.rollback()
            flash(f"❌ Registration failed: {str(e)}", "danger")

        finally:
            cursor.close()
            connection.close()

    return render_template("student_register.html")


@auth_bp.route("/student_login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM student WHERE email = %s", (email,))
            student = cursor.fetchone()

        except mysql.connector.Error:
            flash("❌ Database error occurred! Please try again.", "danger")
            student = None

        finally:
            cursor.close()
            connection.close()

        if student:
            db_password = student["password"]

            if db_password and bcrypt.check_password_hash(db_password, password):
                session.clear()
                session["student_id"] = student["student_id"]
                session["username"] = student["name"]
                session["role"] = "Student"

                flash("✅ Login Successful!", "success")
                return redirect(url_for("student.student_home"))

            else:
                flash("❌ Incorrect password or credentials!", "danger")

        else:
            flash("❌ Invalid Email or Password!", "danger")

    return render_template("student_login.html")


# ✅ Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("🔓 Logged Out Successfully!", "info")
    return redirect(url_for("auth.login_system"))


# ✅ Login System Page
@auth_bp.route("/login_system")
def login_system():
    return render_template("login_system.html")
