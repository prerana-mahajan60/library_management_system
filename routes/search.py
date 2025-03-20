from flask import Blueprint, request, jsonify
from database import get_db_connection  # ✅ Correct import

search_bp = Blueprint("search", __name__)

# 📌 Search Books API (By Name, Author, or Language)
@search_bp.route("/search_books")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])  # ✅ If no query, return empty list

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # ✅ Search in book_name, author, and language
    sql = """
        SELECT * FROM books 
        WHERE book_name LIKE %s OR author LIKE %s OR language LIKE %s
        ORDER BY book_id DESC
    """
    search_term = f"%{query}%"  # ✅ Allow partial matches
    cursor.execute(sql, (search_term, search_term, search_term))

    results = cursor.fetchall()

    cursor.close()
    db.close()
    return jsonify(results)  # ✅ Send results as JSON
