from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
from models import Book, Transaction

app = Flask(__name__)
app.secret_key = "your_secret_key"

#Home Route
@app.route('/')
def home():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('index.html', books=books)


#Borrow Book
@app.route('/borrow/<int:book_id>')
def borrow(book_id):
    if 'user_id' not in session:
        flash("You must be logged in to borrow a book!", "warning")
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    try:
        # Check if book is available
        cursor.execute("SELECT quantity FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()

        if book and book[0] > 0:
            cursor.execute("""
                INSERT INTO transactions (user_id, book_id, action) VALUES (%s, %s, 'borrow')
            """, (session['user_id'], book_id))
            cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE book_id = %s", (book_id,))
            db.commit()
            flash("Book borrowed successfully!", "success")
        else:
            flash("Book is not available!", "danger")
    except Exception as e:
        db.rollback()
        flash(f"Error borrowing book: {e}", "danger")
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('home'))


#Return Book
@app.route('/return/<int:book_id>')
def return_book(book_id):
    if 'user_id' not in session:
        flash("You must be logged in to return a book!", "warning")
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    try:
        # Check if user has borrowed the book
        cursor.execute("""
            SELECT * FROM transactions WHERE book_id = %s AND user_id = %s AND action = 'borrow'
        """, (book_id, session['user_id']))
        transaction = cursor.fetchone()

        if transaction:
            cursor.execute("""
                INSERT INTO transactions (user_id, book_id, action) VALUES (%s, %s, 'return')
            """, (session['user_id'], book_id))
            cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE book_id = %s", (book_id,))
            db.commit()
            flash("Book returned successfully!", "success")
        else:
            flash("You have not borrowed this book!", "danger")
    except Exception as e:
        db.rollback()
        flash(f"Error returning book: {e}", "danger")
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('home'))


#Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password!", "danger")

    return render_template('login.html')


#Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have logged out!", "info")
    return redirect(url_for('login'))
