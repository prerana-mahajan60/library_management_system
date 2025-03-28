from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime, timedelta
from config import get_db_connection
import pytz

# Set IST timezone
IST = pytz.timezone('Asia/Kolkata')

#browse_books_blueprint
browse_books_bp = Blueprint('browse_books_bp', __name__, template_folder="templates")


#to display available books
@browse_books_bp.route('/browse_books')
def browse_books():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    student_id = request.args.get('student_id')

    cursor.execute("SELECT * FROM books WHERE available_copies > 0")
    available_books = cursor.fetchall()

    books_by_language = {'English': [], 'Hindi': [], 'Marathi': []}
    for book in available_books:
        if book['language'] in books_by_language:
            books_by_language[book['language']].append(book)

    cursor.close()
    connection.close()

    return render_template(
        'browse_books.html',
        books_by_language=books_by_language,
        student_id=student_id
    )

def clear_login_success_flash():
    flashes = session.get('_flashes', [])
    session['_flashes'] = [msg for msg in flashes if msg[0] != "success" or msg[1] != "Login Successful!"]

#to display borrowed books
@browse_books_bp.route('/borrowed_books')
def borrowed_books():
    student_id = session.get("student_id")
    if not student_id:
        flash("Error: Student ID not found in session!", "danger")
        return redirect(url_for("auth.student_login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

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
    connection.close()

    return render_template("borrowed_books.html", borrowed_books=borrowed_books)


#to borrow a book
@browse_books_bp.route('/borrow_book/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    student_id = session.get("student_id")
    if not student_id:
        flash("You must be logged in to borrow a book.", "danger")
        return redirect(url_for('auth.student_login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    #Check if the student already borrowed the book and not returned it
    cursor.execute("""
        SELECT COUNT(*)
        FROM borrowed_books
        WHERE student_id = %s AND book_id = %s AND return_date IS NULL
    """, (student_id, book_id))

    already_borrowed = cursor.fetchone()[0]

    if already_borrowed > 0:
        flash("You have already borrowed this book. Return it before borrowing again.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('browse_books_bp.borrowed_books'))

    #Get available copies
    cursor.execute("SELECT available_copies FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()

    if book and book[0] > 0:
        #Decrease available copies by 1
        cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s", (book_id,))

        borrow_date = datetime.now(IST)
        due_date = borrow_date + timedelta(days=14)

        cursor.execute("""
            INSERT INTO borrowed_books (student_id, book_id, borrow_date, due_date)
            VALUES (%s, %s, %s, %s)
        """, (student_id, book_id, borrow_date, due_date))

        #log transaction
        cursor.execute("""
            INSERT INTO transactions (student_id, book_id, action, borrow_date, due_date, transaction_date)  
            VALUES (%s, %s, 'borrow', %s, %s, %s)
        """, (student_id, book_id, borrow_date, due_date, borrow_date))

        #Increment total_books_borrowed
        cursor.execute("""
            UPDATE student
            SET total_books_borrowed = total_books_borrowed + 1
            WHERE student_id = %s
        """, (student_id,))

        connection.commit()
        flash("Book borrowed successfully!", "success")
    else:
        flash("Book is not available!", "danger")

    cursor.close()
    connection.close()

    return redirect(url_for('browse_books_bp.borrowed_books'))


#return a book
@browse_books_bp.route('/return_book/<int:borrow_id>', methods=['POST'])
def return_book(borrow_id):
    student_id = session.get("student_id")
    if not student_id:
        flash("You must be logged in to return a book.", "danger")
        return redirect(url_for("auth.student_login"))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        #get borrow record with actual borrow_date and due_date
        cursor.execute("""
            SELECT book_id, borrow_date, due_date
            FROM borrowed_books
            WHERE borrow_id = %s AND return_date IS NULL
        """, (borrow_id,))

        borrow_record = cursor.fetchone()
        if not borrow_record:
            flash("Borrow record not found or already returned!", "danger")
            return redirect(url_for("browse_books_bp.borrowed_books"))

        book_id = borrow_record["book_id"]
        borrow_date = borrow_record["borrow_date"]
        due_date = borrow_record["due_date"]

        #set return_date properly with IST
        return_date = datetime.now(IST)

        cursor.execute("""
            UPDATE borrowed_books 
            SET return_date = %s
            WHERE borrow_id = %s
        """, (return_date, borrow_id))

        #increase available copies after returning
        cursor.execute("""
            UPDATE books 
            SET available_copies = available_copies + 1
            WHERE book_id = %s
        """, (book_id,))

        #increment total_books_returned for student
        cursor.execute("""
            UPDATE student
            SET total_books_returned = total_books_returned + 1
            WHERE student_id = %s
        """, (student_id,))

        #log return transaction with correct borrow_date and due_date
        cursor.execute("""
            INSERT INTO transactions (student_id, book_id, action, borrow_date, due_date, return_date, transaction_date)
            VALUES (%s, %s, 'return', %s, %s, %s, %s)
        """, (student_id, book_id, borrow_date, due_date, return_date, return_date))

        #return Book Logic for returned_books
        cursor.execute("""
            INSERT INTO returned_books (student_id, book_id, return_date)
            VALUES (%s, %s, %s)
        """, (student_id, book_id, return_date))

        connection.commit()
        flash("Book returned successfully!", "success")

    except mysql.connector.Error as e:
        connection.rollback()
        flash(f"Database Error: {str(e)}", "danger")

    except Exception as e:
        connection.rollback()
        flash(f"Unexpected Error: {str(e)}", "danger")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("browse_books_bp.borrowed_books"))
