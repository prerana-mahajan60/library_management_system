from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
from datetime import datetime, timedelta

# Create a Blueprint for the "Browse Books" page
browse_books_bp = Blueprint('browse_books_bp', __name__, template_folder="templates")


# Helper function to get DB connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='1234mysql$&**',
        database='library_db',
        auth_plugin="mysql_native_password"
    )
    return conn


# =========================
# Route to display available books
# =========================
@browse_books_bp.route('/browse_books')
def browse_books():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    student_id = request.args.get('student_id')

    cursor.execute("SELECT * FROM books WHERE available_copies > 0")
    available_books = cursor.fetchall()

    books_by_language = {'English': [], 'Hindi': [], 'Marathi': []}
    for book in available_books:
        if book['language'] in books_by_language:
            books_by_language[book['language']].append(book)

    cursor.close()
    conn.close()

    return render_template(
        'browse_books.html',
        books_by_language=books_by_language,
        student_id=student_id
    )


# =========================
# Route to display borrowed books
# =========================
@browse_books_bp.route('/borrowed_books')
def borrowed_books():
    student_id = session.get("student_id")
    if not student_id:
        flash("Error: Student ID not found in session!", "danger")
        return redirect(url_for("auth.student_login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT borrowed_books.borrow_id, books.book_name, books.author, 
               books.year, books.language,  
               borrowed_books.borrow_date, borrowed_books.due_date  
        FROM borrowed_books
        JOIN books ON borrowed_books.book_id = books.book_id
        WHERE borrowed_books.student_id = %s AND borrowed_books.return_date IS NULL
    """, (student_id,))

    borrowed_books = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("borrowed_books.html", borrowed_books=borrowed_books)


# =========================
# Route to borrow a book
# =========================
@browse_books_bp.route('/borrow_book/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    student_id = session.get("student_id")
    if not student_id:
        flash("You must be logged in to borrow a book.", "danger")
        return redirect(url_for('auth.student_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT available_copies FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()

    if book and book[0] > 0:
        # ✅ Decrease available copies by 1
        cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s", (book_id,))

        # ✅ Borrow Book Logic
        cursor.execute("""
            INSERT INTO borrowed_books (student_id, book_id, borrow_date, due_date)
            VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 14 DAY))
        """, (student_id, book_id))

        # ✅ Log transaction
        cursor.execute("""
            INSERT INTO transactions (student_id, book_id, action, borrow_date, due_date, transaction_date)  
            VALUES (%s, %s, 'borrow', NOW(), DATE_ADD(NOW(), INTERVAL 14 DAY), NOW())
        """, (student_id, book_id))

        # ✅ Increment total_books_borrowed for the student
        cursor.execute("""
            UPDATE student
            SET total_books_borrowed = total_books_borrowed + 1
            WHERE student_id = %s
        """, (student_id,))

        conn.commit()
        flash("Book borrowed successfully!", "success")
    else:
        flash("Book is not available!", "danger")

    cursor.close()
    conn.close()

    return redirect(url_for('browse_books_bp.borrowed_books'))


# =========================
# Route to return a book
# =========================
@browse_books_bp.route('/return_book/<int:borrow_id>', methods=['POST'])
def return_book(borrow_id):
    student_id = session.get("student_id")
    if not student_id:
        flash("You must be logged in to return a book.", "danger")
        return redirect(url_for("auth_bp.student_login"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ Get book_id and due_date for the borrowed book
        cursor.execute("""
            SELECT book_id, due_date 
            FROM borrowed_books 
            WHERE borrow_id = %s AND return_date IS NULL
        """, (borrow_id,))

        borrow_record = cursor.fetchone()
        if not borrow_record:
            flash("Borrow record not found or already returned!", "danger")
            return redirect(url_for("browse_books_bp.borrowed_books"))

        book_id = borrow_record["book_id"]
        due_date = borrow_record["due_date"]  # ✅ Get existing due_date

        # ✅ Update return_date in borrowed_books
        cursor.execute("""
            UPDATE borrowed_books 
            SET return_date = NOW() 
            WHERE borrow_id = %s
        """, (borrow_id,))

        # ✅ Corrected: Increase available copies after return
        cursor.execute("""
            UPDATE books 
            SET available_copies = available_copies + 0  -- Fix: Increase by 1
            WHERE book_id = %s
        """, (book_id,))

        # ✅ Increment total_books_returned for the student
        cursor.execute("""
            UPDATE student
            SET total_books_returned = total_books_returned + 1
            WHERE student_id = %s
        """, (student_id,))

        # ✅ Log return transaction with the correct due_date
        cursor.execute("""
            INSERT INTO transactions (student_id, book_id, action, borrow_date, due_date, return_date, transaction_date)
            VALUES (%s, %s, 'return', NOW(), %s, NOW(), NOW())  -- Store due_date and return_date correctly
        """, (student_id, book_id, due_date))

        # ✅ Return Book Logic for returned_books
        cursor.execute("""
            INSERT INTO returned_books (student_id, book_id, return_date)
            VALUES (%s, %s, NOW())
        """, (student_id, book_id))

        conn.commit()
        flash("Book returned successfully!", "success")

    except mysql.connector.Error as e:
        conn.rollback()  # Rollback if error occurs
        flash(f"Database Error: {str(e)}", "danger")

    except Exception as e:
        conn.rollback()
        flash(f"Unexpected Error: {str(e)}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("browse_books_bp.borrowed_books"))
