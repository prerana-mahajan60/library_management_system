from flask import Blueprint, render_template, redirect, url_for, flash, session, request
import mysql.connector  # ✅ Import MySQL connector
from flask import current_app
from database import get_db_connection  # ✅ Import database connection function

# Define the admin blueprint
admin_bp = Blueprint("admin", __name__, template_folder="templates")

# =========================
# Admin Home Route
# =========================
@admin_bp.route("/admin_home")
def admin_home():
    current_app.logger.debug("Session in admin_home: " + str(dict(session)))

    # ✅ Check if admin is logged in
    if "admin_id" not in session:
        flash("❌ Please log in first!", "danger")
        return redirect(url_for("auth.admin_login"))

    # ✅ Fetch books from the database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT book_id, book_name, author, year, available_copies, language, cover_image FROM books")
    books = cursor.fetchall()

    # ✅ Debugging output for books
    print("Fetched books:")
    for book in books:
        print(book)  # Ensuring `language` and other data is fetched correctly

    cursor.close()
    connection.close()

    # ✅ Include admin name and ID correctly
    admin = {
        "id": session.get("admin_id"),  # Get admin_id from session
        "name": session.get("admin_name")  # Get admin_name from session
    }

    # ✅ Render template with corrected admin data
    return render_template("admin_home.html", admin=admin, books=books, admin_id=admin["id"])


# =========================
# Admin Profile Route
# =========================
@admin_bp.route("/admin/profile")
def admin_profile():
    if "admin_id" not in session:
        flash("❌ Please log in first!", "danger")
        return redirect(url_for("auth.admin_login"))

    admin_id = session["admin_id"]
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # ✅ Fetch admin data directly from `admin` table
        cursor.execute("""
            SELECT admin_id, admin_name, email, gender, total_books_added, total_books_removed, created_at
            FROM admin
            WHERE admin_id = %s
        """, (admin_id,))
        admin = cursor.fetchone()

        if not admin:
            flash("❌ Admin not found!", "danger")
            return redirect(url_for("admin.admin_home"))

        # ✅ Dynamically assign profile image based on gender
        gender = admin.get("gender", "other").strip().lower()
        gender_image_map = {
            "male": "image/madmin.avif",
            "female": "image/fadmin2.avif",
            "other": "image/other.avif"
        }
        admin["profile_image"] = url_for("static", filename=gender_image_map.get(gender, "image/other.avif"))

        # ✅ Refresh admin data after update (THIS LINE ADDED)
        connection.commit()  # 👈 Isse latest data fetch hoga

        return render_template("admin_profile.html", admin=admin)

    except Exception as e:
        flash(f"❌ Error fetching admin data: {str(e)}", "danger")
        return redirect(url_for("admin.admin_home"))

    finally:
        cursor.close()
        connection.close()



# =========================
@admin_bp.route('/admin/update_profile', methods=['GET', 'POST'])
def update_profile():
    if "admin_id" not in session:
        return redirect(url_for('auth.admin_login'))  # Redirect if not logged in

    admin_id = session["admin_id"]
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        gender = request.form['gender']

        try:
            # ✅ Update admin_name, email & gender in `admin` table directly
            cursor.execute(
                "UPDATE admin SET admin_name = %s, email = %s, gender = %s WHERE admin_id = %s",
                (name, email, gender, admin_id)
            )
            connection.commit()  # ✅ Commit all changes

            # ✅ Update session with new name if not blank
            session["admin_name"] = name if name else session.get("admin_name")
            flash("✅ Profile updated successfully!", "success")

        except Exception as e:
            connection.rollback()  # ❌ Rollback if error occurs
            flash(f"⚠️ Error updating profile: {str(e)}", "danger")

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('admin.admin_profile'))

    # ✅ Fetch admin details from `admin` table directly
    cursor.execute("""
        SELECT admin_id, admin_name, email, gender
        FROM admin
        WHERE admin_id = %s
    """, (admin_id,))
    admin = cursor.fetchone()

    cursor.close()
    connection.close()

    if not admin:
        flash("⚠️ Admin not found!", "warning")
        return redirect(url_for("auth.admin_login"))

    # ✅ Assign profile image based on gender
    gender = admin.get("gender", "other").strip().lower()
    gender_image_map = {
        "male": "image/madmin.avif",
        "female": "image/fadmin2.avif",
        "other": "image/other.avif"
    }
    profile_image = url_for("static", filename=gender_image_map.get(gender, "image/other.avif"))

    return render_template("update_admin_profile.html", admin=admin, profile_image=profile_image)

# =========================
# Delete Admin Profile Route
# =========================
@admin_bp.route('/admin/delete_profile', methods=['POST'])
def delete_profile():
    if "admin_id" not in session:
        flash("❌ Please log in first!", "danger")
        return redirect(url_for("auth.admin_login"))

    admin_id = session["admin_id"]
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # ✅ Delete the admin record directly from `admin` table
        cursor.execute("DELETE FROM admin WHERE admin_id = %s", (admin_id,))
        connection.commit()

        # ✅ Clear session and redirect to login
        session.clear()
        flash("✅ Your profile has been deleted successfully!", "success")

    except Exception as e:
        connection.rollback()  # ❌ Rollback if error occurs
        flash(f"⚠️ Error deleting profile: {str(e)}", "danger")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("auth.admin_login"))


# =========================
# Admin Logout Route
# =========================
@admin_bp.route("/admin_logout")
def admin_logout():
    session.clear()
    flash("✅ Logged out successfully!", "info")
    return redirect(url_for("auth.admin_login"))
