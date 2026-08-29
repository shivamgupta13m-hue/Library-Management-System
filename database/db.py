import os
import sqlite3
from datetime import datetime, timedelta, date
from config import Config

# Global variable indicating which DB backend is currently active
DB_ENGINE = "Unknown"

def try_mysql_connection():
    """Attempts to establish connection to MySQL database."""
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            connection_timeout=2
        )
        return conn
    except Exception as e:
        return None

def get_db():
    """
    Returns an active database connection.
    Prioritizes MySQL if available and accessible.
    Falls back gracefully to SQLite to ensure zero-friction local execution.
    """
    global DB_ENGINE
    mysql_conn = try_mysql_connection()
    if mysql_conn is not None:
        DB_ENGINE = "MySQL (Active)"
        return mysql_conn, "mysql"
    else:
        DB_ENGINE = "SQLite (Local Zero-Config Fallback)"
        conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn, "sqlite"

def init_database():
    """
    Initializes database tables, triggers, views, and seed data if using SQLite
    or verifies schema if using MySQL.
    """
    conn, engine = get_db()
    if engine == "mysql":
        print("[DBMS] Successfully connected to MySQL server database: library_db")
        conn.close()
        return

    print("[DBMS] MySQL server not detected locally. Initializing embedded SQLite database with identical relational schema...")
    cursor = conn.cursor()

    # Create Categories Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create Authors Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS authors (
            author_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            biography TEXT,
            country TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create Books Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            publisher TEXT,
            publication_year INTEGER,
            edition TEXT DEFAULT '1st Edition',
            total_copies INTEGER NOT NULL DEFAULT 1 CHECK (total_copies >= 0),
            available_copies INTEGER NOT NULL DEFAULT 1 CHECK (available_copies >= 0),
            shelf_location TEXT,
            cover_image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON UPDATE CASCADE ON DELETE RESTRICT
        );
    """)

    # Create Book Authors Junction Table (M:N)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_authors (
            book_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            is_primary_author INTEGER DEFAULT 1,
            PRIMARY KEY (book_id, author_id),
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (author_id) REFERENCES authors(author_id) ON UPDATE CASCADE ON DELETE CASCADE
        );
    """)

    # Create Members Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            address TEXT,
            membership_date DATE DEFAULT (DATE('now')),
            status TEXT DEFAULT 'Active',
            max_books_allowed INTEGER DEFAULT 5 CHECK (max_books_allowed >= 1),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create Staff Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff_users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT DEFAULT 'Librarian',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create Loans Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            issued_by INTEGER,
            issue_date DATE DEFAULT (DATE('now')),
            due_date DATE NOT NULL,
            return_date DATE NULL,
            status TEXT DEFAULT 'Active',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY (member_id) REFERENCES members(member_id) ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY (issued_by) REFERENCES staff_users(user_id) ON UPDATE CASCADE ON DELETE SET NULL
        );
    """)

    # Create Fines Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fines (
            fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER NOT NULL UNIQUE,
            amount REAL NOT NULL CHECK (amount >= 0),
            fine_date DATE DEFAULT (DATE('now')),
            payment_date DATE NULL,
            payment_status TEXT DEFAULT 'Unpaid',
            payment_method TEXT DEFAULT 'None',
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (loan_id) REFERENCES loans(loan_id) ON UPDATE CASCADE ON DELETE CASCADE
        );
    """)

    # Create Triggers for SQLite
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_after_loan_insert
        AFTER INSERT ON loans
        WHEN NEW.status = 'Active' OR NEW.status = 'Overdue'
        BEGIN
            UPDATE books SET available_copies = available_copies - 1 WHERE book_id = NEW.book_id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_after_loan_update
        AFTER UPDATE OF return_date ON loans
        WHEN OLD.return_date IS NULL AND NEW.return_date IS NOT NULL
        BEGIN
            UPDATE books SET available_copies = available_copies + 1 WHERE book_id = NEW.book_id;
        END;
    """)

    # Create Views for SQLite
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_book_catalog AS
        SELECT 
            b.book_id,
            b.isbn,
            b.title,
            c.category_id,
            c.name AS category_name,
            GROUP_CONCAT(a.name, ', ') AS authors,
            b.publisher,
            b.publication_year,
            b.edition,
            b.total_copies,
            b.available_copies,
            b.shelf_location,
            CASE 
                WHEN b.available_copies > 0 THEN 'Available'
                ELSE 'Out of Stock'
            END AS stock_status
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        LEFT JOIN book_authors ba ON b.book_id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.author_id
        GROUP BY b.book_id;
    """)

    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_active_loans AS
        SELECT 
            l.loan_id,
            l.book_id,
            b.title AS book_title,
            b.isbn,
            l.member_id,
            (m.first_name || ' ' || m.last_name) AS member_name,
            m.email AS member_email,
            m.phone AS member_phone,
            l.issue_date,
            l.due_date,
            CAST(julianday('now') - julianday(l.due_date) AS INTEGER) AS days_overdue,
            CASE 
                WHEN date('now') > l.due_date THEN 'Overdue'
                ELSE 'Active'
            END AS calculated_status,
            s.full_name AS issued_by_name
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        JOIN members m ON l.member_id = m.member_id
        LEFT JOIN staff_users s ON l.issued_by = s.user_id
        WHERE l.return_date IS NULL;
    """)

    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_overdue_loans AS
        SELECT 
            l.loan_id,
            b.title AS book_title,
            (m.first_name || ' ' || m.last_name) AS member_name,
            m.email AS member_email,
            m.phone AS member_phone,
            l.issue_date,
            l.due_date,
            CAST(julianday('now') - julianday(l.due_date) AS INTEGER) AS days_late,
            (CAST(julianday('now') - julianday(l.due_date) AS INTEGER) * 2.00) AS estimated_fine,
            f.fine_id,
            f.amount AS recorded_fine,
            IFNULL(f.payment_status, 'Unrecorded') AS fine_status
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        JOIN members m ON l.member_id = m.member_id
        LEFT JOIN fines f ON l.loan_id = f.loan_id
        WHERE l.return_date IS NULL AND date('now') > l.due_date;
    """)

    cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_popular_books AS
        SELECT 
            b.book_id,
            b.title,
            b.isbn,
            c.name AS category,
            COUNT(l.loan_id) AS total_times_borrowed,
            MAX(l.issue_date) AS last_borrowed_date
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        LEFT JOIN loans l ON b.book_id = l.book_id
        GROUP BY b.book_id
        ORDER BY total_times_borrowed DESC;
    """)

    # Populate Sample Seed Data if empty
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        print("[DBMS] Seeding sample categories, authors, books, members, and transactions...")
        
        # Categories
        cursor.executemany("INSERT INTO categories (category_id, name, description) VALUES (?, ?, ?);", [
            (1, 'Computer Science & IT', 'Books on algorithms, programming, databases, AI, and systems engineering.'),
            (2, 'Mathematics & Statistics', 'Calculus, linear algebra, discrete mathematics, and probability.'),
            (3, 'Physics & Astronomy', 'Classical mechanics, quantum physics, thermodynamics, and astrophysics.'),
            (4, 'Literature & Fiction', 'Classic and contemporary novels, drama, and short stories.'),
            (5, 'History & Civilizations', 'World history, ancient empires, and political revolutions.'),
            (6, 'Philosophy & Ethics', 'Epistemology, moral philosophy, and logic.'),
            (7, 'Economics & Finance', 'Microeconomics, macroeconomics, investments, and corporate finance.')
        ])

        # Authors
        cursor.executemany("INSERT INTO authors (author_id, name, biography, country) VALUES (?, ?, ?, ?);", [
            (1, 'Abraham Silberschatz', 'Professor of Computer Science at Yale University, renowned for Database System Concepts.', 'USA'),
            (2, 'Henry F. Korth', 'Professor at Lehigh University, co-author of Database System Concepts.', 'USA'),
            (3, 'S. Sudarshan', 'Subrao M. Nilekani Chair Professor at IIT Bombay, expert in relational databases.', 'India'),
            (4, 'Donald E. Knuth', 'Professor Emeritus at Stanford University, author of The Art of Computer Programming.', 'USA'),
            (5, 'Robert C. Martin', 'Software engineer and author famously known as Uncle Bob.', 'USA'),
            (6, 'Martin Kleppmann', 'Researcher in distributed systems at University of Cambridge.', 'UK'),
            (7, 'Yuval Noah Harari', 'Historian and author of Sapiens: A Brief History of Humankind.', 'Israel'),
            (8, 'George Orwell', 'English novelist, essayist, journalist and critic.', 'UK')
        ])

        # Books
        cursor.executemany("""
            INSERT INTO books (book_id, isbn, title, category_id, publisher, publication_year, edition, total_copies, available_copies, shelf_location) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            (1, '978-0078022159', 'Database System Concepts', 1, 'McGraw-Hill Education', 2019, '7th Edition', 8, 6, 'CS-A1-04'),
            (2, '978-0132350884', 'Clean Code: A Handbook of Agile Software Craftsmanship', 1, 'Prentice Hall', 2008, '1st Edition', 5, 4, 'CS-B2-11'),
            (3, '978-1449373320', 'Designing Data-Intensive Applications', 1, 'O''Reilly Media', 2017, '1st Edition', 6, 6, 'CS-B3-02'),
            (4, '978-0201896831', 'The Art of Computer Programming, Vol 1', 1, 'Addison-Wesley', 1997, '3rd Edition', 3, 3, 'CS-A0-01'),
            (5, '978-0062316097', 'Sapiens: A Brief History of Humankind', 5, 'Harper', 2015, '1st Edition', 7, 7, 'HIS-C1-08'),
            (6, '978-0451524935', '1984', 4, 'Signet Classic', 1950, 'Reissue', 10, 9, 'LIT-D4-19'),
            (7, '978-0131103627', 'The C Programming Language', 1, 'Prentice Hall', 1988, '2nd Edition', 4, 3, 'CS-A2-15'),
            (8, '978-0262033848', 'Introduction to Algorithms (CLRS)', 1, 'MIT Press', 2009, '3rd Edition', 6, 6, 'CS-A1-01')
        ])

        # Book Authors
        cursor.executemany("INSERT INTO book_authors (book_id, author_id, is_primary_author) VALUES (?, ?, ?);", [
            (1, 1, 1),
            (1, 2, 0),
            (1, 3, 0),
            (2, 5, 1),
            (3, 6, 1),
            (4, 4, 1),
            (5, 7, 1),
            (6, 8, 1),
            (7, 4, 1),
            (8, 4, 1)
        ])

        # Members
        cursor.executemany("""
            INSERT INTO members (member_id, first_name, last_name, email, phone, address, membership_date, status, max_books_allowed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            (1, 'Aarav', 'Sharma', 'aarav.sharma@example.com', '+91-9876543210', '42 MG Road, Bengaluru, Karnataka', '2023-01-15', 'Active', 5),
            (2, 'Diya', 'Patel', 'diya.patel@example.com', '+91-9876543211', '108 SG Highway, Ahmedabad, Gujarat', '2023-02-20', 'Active', 5),
            (3, 'Rohan', 'Verma', 'rohan.verma@example.com', '+91-9876543212', '15 Park Street, Kolkata, West Bengal', '2023-03-10', 'Active', 5),
            (4, 'Ananya', 'Iyer', 'ananya.iyer@example.com', '+91-9876543213', '7 Anna Salai, Chennai, Tamil Nadu', '2023-04-05', 'Active', 5),
            (5, 'Vikram', 'Malhotra', 'vikram.m@example.com', '+91-9876543214', '88 Connaught Place, New Delhi', '2022-11-12', 'Suspended', 2),
            (6, 'Sneha', 'Reddy', 'sneha.reddy@example.com', '+91-9876543215', '24 Banjara Hills, Hyderabad, Telangana', '2023-06-01', 'Active', 5)
        ])

        # Staff
        cursor.executemany("""
            INSERT INTO staff_users (user_id, username, password_hash, full_name, email, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, [
            (1, 'admin', 'pbkdf2:sha256:260000$admin$defaultpasswordhash', 'Chief Librarian Sarah', 'admin.library@example.com', 'Admin', 1),
            (2, 'librarian1', 'pbkdf2:sha256:260000$lib1$defaultpasswordhash', 'James Wilson', 'james.w@example.com', 'Librarian', 1)
        ])

        # Loans with real dates relative to today
        today = date.today()
        d_minus_4 = (today - timedelta(days=4)).isoformat()
        d_plus_10 = (today + timedelta(days=10)).isoformat()
        
        d_minus_19 = (today - timedelta(days=19)).isoformat()
        d_minus_5 = (today - timedelta(days=5)).isoformat()
        
        d_minus_20 = (today - timedelta(days=20)).isoformat()
        d_minus_6 = (today - timedelta(days=6)).isoformat()
        d_minus_7 = (today - timedelta(days=7)).isoformat()
        
        d_minus_30 = (today - timedelta(days=30)).isoformat()
        d_minus_16 = (today - timedelta(days=16)).isoformat()
        d_minus_11 = (today - timedelta(days=11)).isoformat()

        d_minus_22 = (today - timedelta(days=22)).isoformat()
        d_minus_8 = (today - timedelta(days=8)).isoformat()

        d_minus_8_b = (today - timedelta(days=8)).isoformat()
        d_plus_6 = (today + timedelta(days=6)).isoformat()

        cursor.executemany("""
            INSERT INTO loans (loan_id, book_id, member_id, issued_by, issue_date, due_date, return_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            (1, 1, 1, 1, d_minus_4, d_plus_10, None, 'Active', 'Standard 14-day loan'),
            (2, 2, 2, 1, d_minus_19, d_minus_5, None, 'Overdue', 'Automatic notification sent'),
            (3, 3, 3, 2, d_minus_20, d_minus_6, d_minus_7, 'Returned', 'Returned in good condition'),
            (4, 5, 4, 1, d_minus_30, d_minus_16, d_minus_11, 'Returned', 'Returned 5 days late'),
            (5, 6, 1, 2, d_minus_22, d_minus_8, None, 'Overdue', 'Second notice dispatched'),
            (6, 7, 4, 2, d_minus_8_b, d_plus_6, None, 'Active', 'Exam preparation')
        ])

        # Fine for loan 4
        cursor.execute("""
            INSERT INTO fines (fine_id, loan_id, amount, fine_date, payment_date, payment_status, payment_method, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (1, 4, 10.00, d_minus_11, d_minus_11, 'Paid', 'UPI', 'Paid at circulation desk via UPI QR'))

    conn.commit()
    conn.close()

# -----------------------------------------------------------------------------
# Database Utility Query Handlers
# -----------------------------------------------------------------------------

def query_all(sql, params=()):
    """Executes a SELECT query and returns a list of dictionaries."""
    conn, engine = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        if engine == "mysql":
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            results = [dict(row) for row in cursor.fetchall()]
        return results
    finally:
        cursor.close()
        conn.close()

def query_one(sql, params=()):
    """Executes a SELECT query and returns a single dictionary or None."""
    conn, engine = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        if engine == "mysql":
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        else:
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        cursor.close()
        conn.close()

def execute_dml(sql, params=()):
    """Executes an INSERT, UPDATE, or DELETE query and returns lastrowid / rowcount."""
    conn, engine = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        conn.commit()
        last_id = cursor.lastrowid
        row_count = cursor.rowcount
        return {"last_id": last_id, "row_count": row_count}
    finally:
        cursor.close()
        conn.close()

# -----------------------------------------------------------------------------
# Core Domain Operations (ACID Stored Procedure & Transaction Emulation)
# -----------------------------------------------------------------------------

def get_dashboard_stats():
    """Returns aggregated KPIs for the dashboard view."""
    total_books = query_one("SELECT COUNT(*) AS count, IFNULL(SUM(total_copies), 0) AS total_copies, IFNULL(SUM(available_copies), 0) AS available_copies FROM books")
    total_members = query_one("SELECT COUNT(*) AS total_members, SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) AS active_members FROM members")
    active_loans = query_one("SELECT COUNT(*) AS active_loans FROM loans WHERE return_date IS NULL")
    
    # Overdue count
    overdue_loans = query_one("""
        SELECT COUNT(*) AS overdue_loans 
        FROM loans 
        WHERE return_date IS NULL AND DATE('now') > due_date
    """) if DB_ENGINE.startswith("SQLite") else query_one("""
        SELECT COUNT(*) AS overdue_loans 
        FROM loans 
        WHERE return_date IS NULL AND CURRENT_DATE > due_date
    """)

    # Fines stats
    fines_summary = query_one("""
        SELECT 
            IFNULL(SUM(CASE WHEN payment_status = 'Paid' THEN amount ELSE 0 END), 0) AS total_collected,
            IFNULL(SUM(CASE WHEN payment_status = 'Unpaid' THEN amount ELSE 0 END), 0) AS total_pending
        FROM fines
    """)

    # Category distribution for chart
    categories_stat = query_all("""
        SELECT c.name, COUNT(b.book_id) AS book_count, IFNULL(SUM(b.total_copies), 0) as copy_count
        FROM categories c
        LEFT JOIN books b ON c.category_id = b.category_id
        GROUP BY c.category_id, c.name
    """)

    # Recent transactions
    recent_loans = query_all("""
        SELECT 
            l.loan_id, b.title AS book_title, 
            (m.first_name || ' ' || m.last_name) AS member_name, 
            l.issue_date, l.due_date, l.return_date, l.status
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        JOIN members m ON l.member_id = m.member_id
        ORDER BY l.loan_id DESC
        LIMIT 6
    """) if DB_ENGINE.startswith("SQLite") else query_all("""
        SELECT 
            l.loan_id, b.title AS book_title, 
            CONCAT(m.first_name, ' ', m.last_name) AS member_name, 
            l.issue_date, l.due_date, l.return_date, l.status
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        JOIN members m ON l.member_id = m.member_id
        ORDER BY l.loan_id DESC
        LIMIT 6
    """)

    return {
        "engine": DB_ENGINE,
        "total_titles": total_books["count"] if total_books else 0,
        "total_copies": total_books["total_copies"] if total_books else 0,
        "available_copies": total_books["available_copies"] if total_books else 0,
        "total_members": total_members["total_members"] if total_members else 0,
        "active_members": total_members["active_members"] if total_members else 0,
        "active_loans": active_loans["active_loans"] if active_loans else 0,
        "overdue_loans": overdue_loans["overdue_loans"] if overdue_loans else 0,
        "fines_collected": float(fines_summary["total_collected"]) if fines_summary else 0.0,
        "fines_pending": float(fines_summary["total_pending"]) if fines_summary else 0.0,
        "category_distribution": categories_stat,
        "recent_loans": recent_loans
    }

def get_books(search=None, category_id=None, availability=None):
    """Retrieves books with author and category details and optional filters."""
    query = """
        SELECT 
            b.book_id, b.isbn, b.title, b.publisher, b.publication_year, b.edition,
            b.total_copies, b.available_copies, b.shelf_location,
            c.category_id, c.name AS category_name,
            GROUP_CONCAT(a.name, ', ') AS authors
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        LEFT JOIN book_authors ba ON b.book_id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.author_id
        WHERE 1=1
    """ if DB_ENGINE.startswith("SQLite") else """
        SELECT 
            b.book_id, b.isbn, b.title, b.publisher, b.publication_year, b.edition,
            b.total_copies, b.available_copies, b.shelf_location,
            c.category_id, c.name AS category_name,
            GROUP_CONCAT(a.name ORDER BY ba.is_primary_author DESC SEPARATOR ', ') AS authors
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        LEFT JOIN book_authors ba ON b.book_id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.author_id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (b.title LIKE ? OR b.isbn LIKE ? OR a.name LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
    if category_id:
        query += " AND b.category_id = ?"
        params.append(category_id)
    if availability == "available":
        query += " AND b.available_copies > 0"
    elif availability == "out_of_stock":
        query += " AND b.available_copies = 0"

    query += " GROUP BY b.book_id ORDER BY b.title ASC"
    return query_all(query, params)

def add_book_record(data):
    """Inserts a new book and associates authors within a transaction."""
    conn, engine = get_db()
    cursor = conn.cursor()
    try:
        # Check unique ISBN
        cursor.execute("SELECT book_id FROM books WHERE isbn = ?", (data['isbn'],))
        if cursor.fetchone():
            return {"success": False, "error": "A book with this ISBN already exists."}

        cursor.execute("""
            INSERT INTO books (isbn, title, category_id, publisher, publication_year, edition, total_copies, available_copies, shelf_location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            data['isbn'], data['title'], data['category_id'], data.get('publisher'),
            data.get('publication_year'), data.get('edition', '1st Edition'),
            data.get('total_copies', 1), data.get('total_copies', 1), data.get('shelf_location')
        ))
        book_id = cursor.lastrowid

        # Insert author association
        author_name = data.get('author_name', '').strip()
        if author_name:
            # Check or create author
            cursor.execute("SELECT author_id FROM authors WHERE name = ?", (author_name,))
            author_row = cursor.fetchone()
            if author_row:
                author_id = author_row[0]
            else:
                cursor.execute("INSERT INTO authors (name) VALUES (?);", (author_name,))
                author_id = cursor.lastrowid
            
            cursor.execute("INSERT INTO book_authors (book_id, author_id, is_primary_author) VALUES (?, ?, 1);", (book_id, author_id))

        conn.commit()
        return {"success": True, "book_id": book_id, "message": "Book registered successfully."}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()

def issue_book_transaction(book_id, member_id, staff_id=1, loan_days=14):
    """
    Executes book issue transaction with full ACID consistency and business logic checks.
    Emulates sp_issue_book stored procedure.
    """
    conn, engine = get_db()
    cursor = conn.cursor()
    try:
        # 1. Validate Book Availability
        cursor.execute("SELECT title, available_copies FROM books WHERE book_id = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            return {"success": False, "error": "Book not found."}
        if (book['available_copies'] if engine == 'sqlite' else book[1]) <= 0:
            return {"success": False, "error": "No available copies in stock for this book."}

        # 2. Validate Member Status
        cursor.execute("SELECT status, max_books_allowed FROM members WHERE member_id = ?", (member_id,))
        member = cursor.fetchone()
        if not member:
            return {"success": False, "error": "Member not found."}
        
        status = member['status'] if engine == 'sqlite' else member[0]
        max_allowed = member['max_books_allowed'] if engine == 'sqlite' else member[1]

        if status != 'Active':
            return {"success": False, "error": f"Member account is currently '{status}'. Cannot issue books."}

        # 3. Check active loan limit
        cursor.execute("SELECT COUNT(*) FROM loans WHERE member_id = ? AND return_date IS NULL", (member_id,))
        active_loans_count = cursor.fetchone()[0]
        if active_loans_count >= max_allowed:
            return {"success": False, "error": f"Member has reached their maximum borrowing limit ({max_allowed} books)."}

        # 4. Check unpaid dues
        cursor.execute("""
            SELECT IFNULL(SUM(f.amount), 0.0) 
            FROM fines f
            JOIN loans l ON f.loan_id = l.loan_id
            WHERE l.member_id = ? AND f.payment_status = 'Unpaid'
        """, (member_id,))
        unpaid_fines = cursor.fetchone()[0]
        if unpaid_fines and unpaid_fines > 20.0:
            return {"success": False, "error": f"Member has ${unpaid_fines:.2f} in unpaid fines. Outstanding balance must be settled first."}

        # 5. Calculate issue and due date
        today_date = date.today()
        due_date = today_date + timedelta(days=loan_days)

        # 6. Insert Loan Record
        cursor.execute("""
            INSERT INTO loans (book_id, member_id, issued_by, issue_date, due_date, status)
            VALUES (?, ?, ?, ?, ?, 'Active');
        """, (book_id, member_id, staff_id, today_date.isoformat(), due_date.isoformat()))
        loan_id = cursor.lastrowid

        # Update available copies (if trigger didn't fire in plain connection)
        cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?", (book_id,))

        conn.commit()
        return {
            "success": True, 
            "loan_id": loan_id, 
            "due_date": due_date.isoformat(),
            "message": f"Book issued successfully. Due on {due_date.strftime('%b %d, %Y')}."
        }
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()

def return_book_transaction(loan_id, return_date_str=None):
    """
    Executes book return transaction, restores copy count, and auto-calculates overdue fines.
    Emulates sp_return_book stored procedure.
    """
    conn, engine = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT book_id, member_id, due_date, return_date FROM loans WHERE loan_id = ?", (loan_id,))
        loan = cursor.fetchone()
        if not loan:
            return {"success": False, "error": "Loan record not found."}

        book_id = loan['book_id'] if engine == 'sqlite' else loan[0]
        due_date_val = loan['due_date'] if engine == 'sqlite' else loan[2]
        already_returned = loan['return_date'] if engine == 'sqlite' else loan[3]

        if already_returned:
            return {"success": False, "error": "This loan has already been closed and the book returned."}

        actual_return_date = date.fromisoformat(return_date_str) if return_date_str else date.today()
        if isinstance(due_date_val, str):
            due_date = date.fromisoformat(due_date_val)
        else:
            due_date = due_date_val

        fine_amount = 0.0
        days_late = (actual_return_date - due_date).days

        # Update loan record
        cursor.execute("""
            UPDATE loans 
            SET return_date = ?, status = 'Returned'
            WHERE loan_id = ?
        """, (actual_return_date.isoformat(), loan_id))

        # Restore book inventory count
        cursor.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?", (book_id,))

        # Calculate and record fine if overdue
        if days_late > 0:
            fine_amount = round(days_late * Config.DAILY_FINE_RATE, 2)
            cursor.execute("""
                INSERT INTO fines (loan_id, amount, fine_date, payment_status, remarks)
                VALUES (?, ?, ?, 'Unpaid', ?)
            """, (
                loan_id, fine_amount, actual_return_date.isoformat(),
                f"Overdue by {days_late} day(s) at ${Config.DAILY_FINE_RATE:.2f}/day"
            ))

        conn.commit()
        return {
            "success": True,
            "days_late": max(0, days_late),
            "fine_amount": fine_amount,
            "message": f"Book returned successfully. {'Fine incurred: $' + str(fine_amount) if fine_amount > 0 else 'Returned on time without fines.'}"
        }
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()

def pay_fine_record(fine_id, payment_method="Cash"):
    """Marks an unpaid fine as Paid."""
    conn, engine = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT amount, payment_status FROM fines WHERE fine_id = ?", (fine_id,))
        fine = cursor.fetchone()
        if not fine:
            return {"success": False, "error": "Fine record not found."}
        
        status = fine['payment_status'] if engine == 'sqlite' else fine[1]
        if status == 'Paid':
            return {"success": False, "error": "This fine has already been paid."}

        cursor.execute("""
            UPDATE fines 
            SET payment_status = 'Paid', payment_date = ?, payment_method = ?
            WHERE fine_id = ?
        """, (date.today().isoformat(), payment_method, fine_id))

        conn.commit()
        return {"success": True, "message": f"Payment of ${fine['amount'] if engine == 'sqlite' else fine[0]:.2f} processed successfully via {payment_method}."}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()
