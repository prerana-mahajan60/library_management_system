import mysql.connector
from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from config import get_db_connection
#books_blueprint
books_bp = Blueprint('books_bp', __name__, template_folder="templates")


#to display books
@books_bp.route('/books', methods=['GET'])
def books():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetching books from database
    cursor.execute("""
        SELECT * FROM books ORDER BY language, book_name
    """)
    books = cursor.fetchall()

    #sort books by language
    books_by_language = {}
    for book in books:
        lang = book['language']
        if lang not in books_by_language:
            books_by_language[lang] = []
        books_by_language[lang].append(book)

    connection.close()
    return render_template('books.html', books_by_language=books_by_language, role="Admin")


#to add a new book (Admin only)
@books_bp.route('/books/add', methods=['POST'])
def add_book():
    book_name = request.form['book_name']
    author = request.form['author']
    year = request.form['year']
    available_copies = request.form['available_copies']
    language = request.form['language']
    admin_id = session.get("admin_id")

    connection = get_db_connection()
    cursor = connection.cursor()

    #Adding new book
    cursor.execute("""
        INSERT INTO books (book_name, author, year, available_copies, language)
        VALUES (%s, %s, %s, %s, %s)
    """, (book_name, author, year, available_copies, language))

    #Updating total_books_added
    cursor.execute("""
        UPDATE admin
        SET total_books_added = total_books_added + 1
        WHERE admin_id = %s
    """, (admin_id,))

    connection.commit()
    cursor.close()
    connection.close()

    flash('Book added successfully!', 'success')
    return redirect(url_for('books_bp.books'))

#Route to delete a book (Admin only)
@books_bp.route('/books/delete/<int:book_id>', methods=['GET'])
def delete_book(book_id):
    admin_id = session.get("admin_id")
    connection = get_db_connection()
    cursor = connection.cursor()

    # Delete the book
    cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))

    # Update total_books_removed
    cursor.execute("""
        UPDATE admin
        SET total_books_removed = total_books_removed + 1
        WHERE admin_id = %s
    """, (admin_id,))

    connection.commit()
    cursor.close()
    connection.close()

    flash('Book removed successfully!', 'success')
    return redirect(url_for('books_bp.books'))


#to update book details (Admin only)
@books_bp.route('/books/update/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    connection= get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        book_name = request.form['book_name']
        author = request.form['author']
        year = request.form['year']
        available_copies = request.form['available_copies']
        language = request.form['language']

        #Update book details
        cursor.execute("""
            UPDATE books
            SET book_name = %s, author = %s, year = %s, available_copies = %s, language = %s
            WHERE book_id = %s
        """, (book_name, author, year, available_copies, language, book_id))

        connection.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books_bp.books'))

    cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template('update_book.html', book=book)
