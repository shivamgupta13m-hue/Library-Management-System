from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime, date
import os

from config import Config
from database.db import (
    init_database, get_dashboard_stats, get_books, add_book_record,
    issue_book_transaction, return_book_transaction, pay_fine_record,
    query_all, query_one, execute_dml, DB_ENGINE, get_db
)

app = Flask(
    __name__,
    static_folder='static',
    static_url_path='/static',
    template_folder='templates'
)
app.config.from_object(Config)

# Initialize database schema on startup
with app.app_context():
    init_database()

# -----------------------------------------------------------------------------
# Web Page & Static Assets Routes (CSS, JS, HTML)
# -----------------------------------------------------------------------------
def _serve_file_from_dirs(filename, candidate_dirs, default_dir):
    """Safely locate and serve static assets across candidate project directories."""
    for rel_dir in candidate_dirs:
        full_dir = os.path.join(app.root_path, rel_dir)
        file_path = os.path.join(full_dir, filename)
        if os.path.exists(file_path):
            return send_from_directory(full_dir, filename)
    return send_from_directory(os.path.join(app.root_path, default_dir), filename)

@app.route('/')
@app.route('/index.html')
def index():
    """Render the single-page application dashboard."""
    return render_template('index.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS stylesheets from static/css or css directory."""
    return _serve_file_from_dirs(filename, ['static/css', 'css', 'templates'], 'static/css')

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JS scripts from static/js or js directory."""
    return _serve_file_from_dirs(filename, ['static/js', 'js', 'templates'], 'static/js')

@app.route('/style.css')
def serve_root_style():
    """Fallback route for direct style.css requests."""
    return _serve_file_from_dirs('style.css', ['static/css', 'css', 'templates'], 'static/css')

@app.route('/app.js')
def serve_root_app_js():
    """Fallback route for direct app.js requests."""
    return _serve_file_from_dirs('app.js', ['static/js', 'js', 'templates'], 'static/js')

# -----------------------------------------------------------------------------
# REST API: Status & Dashboard KPIs
# -----------------------------------------------------------------------------
@app.route('/api/status', methods=['GET'])
def get_system_status():
    from database.db import DB_ENGINE
    return jsonify({
        "status": "online",
        "system": "Library Management DBMS",
        "database_engine": DB_ENGINE,
        "server_time": datetime.now().isoformat()
    })

@app.route('/api/dashboard/stats', methods=['GET'])
def api_dashboard_stats():
    try:
        stats = get_dashboard_stats()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------------------
# REST API: Books Catalog
# -----------------------------------------------------------------------------
@app.route('/api/books', methods=['GET'])
def api_get_books():
    try:
        search = request.args.get('search', '').strip()
        category_id = request.args.get('category_id')
        availability = request.args.get('availability')
        books = get_books(search=search if search else None, 
                          category_id=int(category_id) if category_id else None, 
                          availability=availability)
        return jsonify({"success": True, "count": len(books), "data": books})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/books', methods=['POST'])
def api_add_book():
    try:
        data = request.get_json()
        if not data or not data.get('isbn') or not data.get('title') or not data.get('category_id'):
            return jsonify({"success": False, "error": "ISBN, Title, and Category are required."}), 400
        
        result = add_book_record(data)
        if result.get("success"):
            return jsonify(result), 201
        return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/books/<int:book_id>', methods=['GET'])
def api_get_book(book_id):
    try:
        book = query_one("""
            SELECT b.*, c.name AS category_name, GROUP_CONCAT(a.name, ', ') AS authors
            FROM books b
            JOIN categories c ON b.category_id = c.category_id
            LEFT JOIN book_authors ba ON b.book_id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.author_id
            WHERE b.book_id = ?
            GROUP BY b.book_id
        """, (book_id,))
        if not book:
            return jsonify({"success": False, "error": "Book not found."}), 404
        return jsonify({"success": True, "data": book})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def api_update_book(book_id):
    try:
        data = request.get_json()
        total_copies = int(data.get('total_copies', 1))
        
        # Calculate available copies change
        existing = query_one("SELECT total_copies, available_copies FROM books WHERE book_id = ?", (book_id,))
        if not existing:
            return jsonify({"success": False, "error": "Book not found."}), 404
        
        diff = total_copies - existing['total_copies']
        new_avail = max(0, existing['available_copies'] + diff)

        execute_dml("""
            UPDATE books 
            SET title = ?, category_id = ?, publisher = ?, publication_year = ?, 
                edition = ?, total_copies = ?, available_copies = ?, shelf_location = ?
            WHERE book_id = ?
        """, (
            data['title'], data['category_id'], data.get('publisher'),
            data.get('publication_year'), data.get('edition'),
            total_copies, new_avail, data.get('shelf_location'), book_id
        ))

        return jsonify({"success": True, "message": "Book details updated successfully."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def api_delete_book(book_id):
    try:
        # Check active loans
        active = query_one("SELECT COUNT(*) AS count FROM loans WHERE book_id = ? AND return_date IS NULL", (book_id,))
        if active and active['count'] > 0:
            return jsonify({"success": False, "error": "Cannot delete book while active loan copies exist."}), 400
        
        execute_dml("DELETE FROM books WHERE book_id = ?", (book_id,))
        return jsonify({"success": True, "message": "Book deleted from catalog."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------------------
# REST API: Members Management
# -----------------------------------------------------------------------------
@app.route('/api/members', methods=['GET'])
def api_get_members():
    try:
        search = request.args.get('search', '').strip()
        if search:
            term = f"%{search}%"
            members = query_all("""
                SELECT m.*, 
                    (SELECT COUNT(*) FROM loans l WHERE l.member_id = m.member_id AND l.return_date IS NULL) AS active_borrow_count,
                    (SELECT IFNULL(SUM(f.amount), 0) FROM fines f JOIN loans l ON f.loan_id = l.loan_id WHERE l.member_id = m.member_id AND f.payment_status = 'Unpaid') AS unpaid_fine_amount
                FROM members m
                WHERE m.first_name LIKE ? OR m.last_name LIKE ? OR m.email LIKE ? OR m.phone LIKE ?
                ORDER BY m.first_name ASC
            """, (term, term, term, term))
        else:
            members = query_all("""
                SELECT m.*, 
                    (SELECT COUNT(*) FROM loans l WHERE l.member_id = m.member_id AND l.return_date IS NULL) AS active_borrow_count,
                    (SELECT IFNULL(SUM(f.amount), 0) FROM fines f JOIN loans l ON f.loan_id = l.loan_id WHERE l.member_id = m.member_id AND f.payment_status = 'Unpaid') AS unpaid_fine_amount
                FROM members m
                ORDER BY m.first_name ASC
            """)
        return jsonify({"success": True, "count": len(members), "data": members})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/members', methods=['POST'])
def api_add_member():
    try:
        data = request.get_json()
        if not data or not data.get('first_name') or not data.get('last_name') or not data.get('email') or not data.get('phone'):
            return jsonify({"success": False, "error": "First Name, Last Name, Email, and Phone are required."}), 400
        
        # Check duplicate email
        existing = query_one("SELECT member_id FROM members WHERE email = ?", (data['email'],))
        if existing:
            return jsonify({"success": False, "error": "A member with this email address already exists."}), 400

        result = execute_dml("""
            INSERT INTO members (first_name, last_name, email, phone, address, status, max_books_allowed)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            data['first_name'], data['last_name'], data['email'], data['phone'],
            data.get('address', ''), data.get('status', 'Active'), int(data.get('max_books_allowed', 5))
        ))
        return jsonify({"success": True, "member_id": result['last_id'], "message": "Member registered successfully."}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/members/<int:member_id>/history', methods=['GET'])
def api_get_member_history(member_id):
    try:
        history = query_all("""
            SELECT l.loan_id, b.title AS book_title, b.isbn, l.issue_date, l.due_date, l.return_date, l.status,
                   f.amount AS fine_amount, f.payment_status AS fine_status
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            LEFT JOIN fines f ON l.loan_id = f.loan_id
            WHERE l.member_id = ?
            ORDER BY l.loan_id DESC
        """, (member_id,))
        return jsonify({"success": True, "data": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------------------
# REST API: Circulation & Loans (Issue / Return / Overdue)
# -----------------------------------------------------------------------------
@app.route('/api/loans', methods=['GET'])
def api_get_loans():
    try:
        status = request.args.get('status')
        if status == 'active':
            loans = query_all("SELECT * FROM v_active_loans ORDER BY issue_date DESC")
        elif status == 'overdue':
            loans = query_all("SELECT * FROM v_overdue_loans ORDER BY days_late DESC")
        else:
            loans = query_all("""
                SELECT l.loan_id, b.title AS book_title, b.isbn,
                       (m.first_name || ' ' || m.last_name) AS member_name, m.email AS member_email,
                       l.issue_date, l.due_date, l.return_date, l.status,
                       f.amount AS fine_amount, f.payment_status AS fine_status
                FROM loans l
                JOIN books b ON l.book_id = b.book_id
                JOIN members m ON l.member_id = m.member_id
                LEFT JOIN fines f ON l.loan_id = f.loan_id
                ORDER BY l.loan_id DESC
            """)
        return jsonify({"success": True, "count": len(loans), "data": loans})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/loans/issue', methods=['POST'])
def api_issue_book():
    try:
        data = request.get_json()
        if not data or not data.get('book_id') or not data.get('member_id'):
            return jsonify({"success": False, "error": "Book ID and Member ID are required."}), 400
        
        loan_days = int(data.get('loan_days', Config.DEFAULT_LOAN_DAYS))
        result = issue_book_transaction(int(data['book_id']), int(data['member_id']), loan_days=loan_days)
        
        if result.get("success"):
            return jsonify(result), 200
        return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/loans/return', methods=['POST'])
def api_return_book():
    try:
        data = request.get_json()
        if not data or not data.get('loan_id'):
            return jsonify({"success": False, "error": "Loan ID is required."}), 400
        
        return_date = data.get('return_date')
        result = return_book_transaction(int(data['loan_id']), return_date_str=return_date)
        
        if result.get("success"):
            return jsonify(result), 200
        return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------------------
# REST API: Fines Management
# -----------------------------------------------------------------------------
@app.route('/api/fines', methods=['GET'])
def api_get_fines():
    try:
        fines = query_all("""
            SELECT f.fine_id, f.loan_id, f.amount, f.fine_date, f.payment_date, f.payment_status, f.payment_method, f.remarks,
                   b.title AS book_title, (m.first_name || ' ' || m.last_name) AS member_name, m.email AS member_email
            FROM fines f
            JOIN loans l ON f.loan_id = l.loan_id
            JOIN books b ON l.book_id = b.book_id
            JOIN members m ON l.member_id = m.member_id
            ORDER BY f.fine_id DESC
        """)
        return jsonify({"success": True, "count": len(fines), "data": fines})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/fines/pay', methods=['POST'])
def api_pay_fine():
    try:
        data = request.get_json()
        if not data or not data.get('fine_id'):
            return jsonify({"success": False, "error": "Fine ID is required."}), 400
        
        payment_method = data.get('payment_method', 'Cash')
        result = pay_fine_record(int(data['fine_id']), payment_method=payment_method)
        
        if result.get("success"):
            return jsonify(result), 200
        return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------------------
# REST API: Categories & Authors Metadata
# -----------------------------------------------------------------------------
@app.route('/api/categories', methods=['GET'])
def api_get_categories():
    try:
        categories = query_all("SELECT * FROM categories ORDER BY name ASC")
        return jsonify({"success": True, "data": categories})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/authors', methods=['GET'])
def api_get_authors():
    try:
        authors = query_all("SELECT * FROM authors ORDER BY name ASC")
        return jsonify({"success": True, "data": authors})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------------------
# REST API: DBMS Views & Stored Procedures Inspector
# -----------------------------------------------------------------------------
@app.route('/api/dbms/views/<view_name>', methods=['GET'])
def api_inspect_view(view_name):
    allowed_views = ['v_book_catalog', 'v_active_loans', 'v_overdue_loans', 'v_popular_books']
    if view_name not in allowed_views:
        return jsonify({"success": False, "error": f"Invalid view name. Permitted: {', '.join(allowed_views)}"}), 400
    try:
        data = query_all(f"SELECT * FROM {view_name} LIMIT 50")
        return jsonify({"success": True, "view": view_name, "count": len(data), "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("📚 LIBRARY MANAGEMENT SYSTEM (DBMS PROJECT)")
    print(f"🚀 Server running on http://127.0.0.1:{Config.PORT}")
    print("=" * 70)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
