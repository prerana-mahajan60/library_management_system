import mysql.connector
from flask import Blueprint, render_template, request, redirect, url_for, flash,session

# Set up the Blueprint for books routes
books_bp = Blueprint('books_bp', __name__, template_folder="templates")

# Database connection function
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',  # Your MySQL host (usually localhost)
        user='root',       # Your MySQL username
        password='1234mysql$&**',  # Your MySQL password
        database='library_db',  # Your database name
        auth_plugin='mysql_native_password'
    )
    return conn

# Route to display books
@books_bp.route('/books', methods=['GET'])
def books():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Using dictionary=True to get results as dictionaries

    # Fetch books from the database
    cursor.execute("""
        SELECT * FROM books ORDER BY language, book_name
    """)
    books = cursor.fetchall()

    # Group books by language
    books_by_language = {}
    for book in books:
        lang = book['language']  # Access columns by name (dictionary keys)
        if lang not in books_by_language:
            books_by_language[lang] = []
        books_by_language[lang].append(book)

    conn.close()
    return render_template('books.html', books_by_language=books_by_language, role="Admin")


# =========================
# Route to add a new book (Admin only)
# =========================
@books_bp.route('/books/add', methods=['POST'])
def add_book():
    book_name = request.form['book_name']
    author = request.form['author']
    year = request.form['year']
    available_copies = request.form['available_copies']
    language = request.form['language']
    admin_id = session.get("admin_id")  # ✅ Admin ID from session

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Add the new book to the books table
    cursor.execute("""
        INSERT INTO books (book_name, author, year, available_copies, language)
        VALUES (%s, %s, %s, %s, %s)
    """, (book_name, author, year, available_copies, language))

    # ✅ Update total_books_added for the admin
    cursor.execute("""
        UPDATE admin
        SET total_books_added = total_books_added + 1
        WHERE admin_id = %s
    """, (admin_id,))

    conn.commit()
    cursor.close()
    conn.close()

    flash('✅ Book added successfully!', 'success')
    return redirect(url_for('books_bp.books'))


# =========================
# Route to delete a book (Admin only)
# =========================
@books_bp.route('/books/delete/<int:book_id>', methods=['GET'])
def delete_book(book_id):
    admin_id = session.get("admin_id")  # ✅ Admin ID from session
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Delete the book from the books table
    cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))

    # ✅ Update total_books_removed for the admin
    cursor.execute("""
        UPDATE admin
        SET total_books_removed = total_books_removed + 1
        WHERE admin_id = %s
    """, (admin_id,))

    conn.commit()
    cursor.close()
    conn.close()

    flash('✅ Book removed successfully!', 'success')
    return redirect(url_for('books_bp.books'))


# =========================
# Route to update book details (Admin only)
# =========================
@books_bp.route('/books/update/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        book_name = request.form['book_name']
        author = request.form['author']
        year = request.form['year']
        available_copies = request.form['available_copies']
        language = request.form['language']

        # ✅ Update book details
        cursor.execute("""
            UPDATE books
            SET book_name = %s, author = %s, year = %s, available_copies = %s, language = %s
            WHERE book_id = %s
        """, (book_name, author, year, available_copies, language, book_id))

        conn.commit()
        flash('✅ Book updated successfully!', 'success')
        return redirect(url_for('books_bp.books'))

    # ✅ Get the existing details for the book
    cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('update_book.html', book=book)
