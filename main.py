from flask import Flask, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from routes.auth import auth_bp
from routes.books import books_bp
from routes.transactions import transactions_bp
from routes.admin import admin_bp
from routes.student import student_bp
from config import get_db_connection
from database import get_db_connection
from routes.browse_books import browse_books_bp
import os
from dotenv import load_dotenv

#Load .env Variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Initialize Flask-Bcrypt
bcrypt = Bcrypt(app)

#---------------------------------------------------All Files Blueprints---------------------------------
#registering Blueprints with URL prefixes
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(student_bp, url_prefix="/student")
app.register_blueprint(books_bp, url_prefix="/books")
app.register_blueprint(transactions_bp, url_prefix="/transactions")
app.register_blueprint(browse_books_bp, url_prefix="/browse_books")

#--------------------------------------Routes---------------------------------------------------
@app.route("/")
def index():
    return render_template("login_system.html")

# Admin Routes Redirection
@app.route("/auth/login")
def admin_login_redirect():
    return redirect(url_for("auth.admin_login"))

@app.route("/auth/register")
def admin_register_redirect():
    return redirect(url_for("auth.admin_register"))

@app.route("/admin/admin_home")
def admin_home_redirect():
    return redirect(url_for("admin.admin_home"))

# Student Routes Redirection
@app.route("/auth/student_login")
def student_login_redirect():
    return redirect(url_for("auth.student_login"))

@app.route("/auth/student_register")
def student_register_redirect():
    return redirect(url_for("auth.student_register"))

@app.route("/student/student_home")
def student_home_redirect():
    return redirect(url_for("student.student_home"))

# Books and Other Routes Redirection
@app.route("/books")
def books_redirect():
    return redirect(url_for("books_bp.books"))

@app.route("/transactions")
def transactions_redirect():
    return redirect(url_for("transactions_bp.transactions"))

@app.route("/browse_books")
def browse_books_redirect():
    return redirect(url_for("browse_books_bp.browse_books"))

if __name__ == "__main__":
    app.run(debug=True)
