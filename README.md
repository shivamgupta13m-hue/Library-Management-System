# 📚 Library Management System (DBMS Project)

An enterprise-grade **Database Management System (DBMS)** project built with **HTML5, CSS3, Modern JavaScript (ES6+), Python (Flask), MySQL, and ER Modeling**.

This system features complete **relational database modeling up to 3NF/BCNF**, automated business rules via **SQL Triggers**, real-time analytical projections via **SQL Views**, concurrency protection with **ACID Stored Procedures**, and an interactive single-page dashboard.

---

## 🌟 Key Features

1. **Entity-Relationship (ER) Modeling**:
   - 8 normalized entities resolving 1:1, 1:N, and M:N relationships.
   - Comprehensive documentation of attributes, primary keys, foreign keys, and participation constraints.
2. **Advanced DBMS Architecture (MySQL 8.0+)**:
   - **Triggers**: Auto-updates book inventory on checkout/return and automatically calculates late fees.
   - **Stored Procedures & ACID Transactions**: Atomic execution for issuing and returning books with row-level locks.
   - **Views**: Pre-computed projections (`v_book_catalog`, `v_active_loans`, `v_overdue_loans`, `v_popular_books`).
   - **Integrity Constraints**: Primary keys, unique candidate keys, check constraints, cascade rules.
3. **Dual Database Adapter**:
   - Seamlessly runs with **MySQL** as the primary enterprise database.
   - Includes automatic zero-configuration **SQLite fallback** allowing instant local testing without needing an active MySQL server setup.
4. **Modern Responsive Web Interface**:
   - **Dashboard**: Live counter cards for titles, shelf copies, active loans, overdue items, and fines collected.
   - **Book Catalog**: Real-time search, genre filtering, stock status badges, modal-based CRUD.
   - **Member Directory**: Patron registration, borrow limits, and comprehensive loan history.
   - **Circulation Desk**: Fast book checkout, automated return date calculations, and overdue fine estimator.
   - **Fine & Overdue Management**: Penalty ledger with instant multi-channel payment settlements (Cash, Card, UPI, Online).
   - **Interactive DBMS & ER Docs**: Built-in Mermaid ER diagram viewer and live SQL view inspector.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Modern Flexbox & CSS Variables), Vanilla JavaScript (ES6+ Fetch API), FontAwesome 6, Mermaid.js |
| **Backend** | Python 3.9+, Flask 3.0, Werkzeug |
| **Database** | MySQL 8.0+ / SQLite 3 (Dual Engine with Automatic Fallback) |
| **Database Modeling** | Chen ER Modeling, Crow's Foot ER Diagram, Relational Schema Normalization (1NF, 2NF, 3NF, BCNF) |

---

## 📁 Project Directory Structure

```
library_management_system/
├── app.py                      # Flask Application Entrypoint & REST API Endpoints
├── config.py                   # Configuration (MySQL credentials & SQLite fallback mode)
├── requirements.txt            # Python dependencies (Flask, mysql-connector-python, etc.)
├── README.md                   # Comprehensive Project Report and Setup Guide
├── database/
│   ├── schema.sql              # MySQL DDL (Tables, Constraints, Triggers, Views, Procedures)
│   ├── seed_data.sql           # Realistic seed dataset for immediate testing
│   ├── er_diagram_doc.md       # Full DBMS report & ER documentation (1NF, 2NF, 3NF analysis)
│   └── db.py                   # Robust Database wrapper (MySQL with auto SQLite fallback)
├── static/
│   ├── css/
│   │   └── style.css           # Modern, responsive UI styling (glassmorphism/clean design)
│   └── js/
│       └── app.js              # Single-page dynamic interactivity, AJAX, notifications, charts
└── templates/
    └── index.html              # Main multi-view application shell
```

---

## 🚀 Quick Start Guide

### Step 1: Install Dependencies
Ensure you have Python 3.8+ installed. In your terminal or command prompt:

```bash
cd library_management_system
pip install -r requirements.txt
```

### Step 2: Run the System

#### Option A: Zero-Config Instant Run (Embedded SQLite Mode)
Simply start the Flask server. The system will automatically initialize all tables, triggers, views, and seed data:

```bash
python app.py
```

Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

#### Option B: Enterprise MySQL Run
1. Open your MySQL client or MySQL Workbench.
2. Execute `database/schema.sql` to create `library_db` and all tables, triggers, views, and procedures:
   ```bash
   mysql -u root -p < database/schema.sql
   mysql -u root -p library_db < database/seed_data.sql
   ```
3. Configure your MySQL credentials in a `.env` file or environment variables:
   ```env
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=library_db
   ```
4. Start the server:
   ```bash
   python app.py
   ```

---

## 📐 Database Management System (DBMS) Specifications

### 1. Relational Schema Mapping
- **`categories`** (`category_id` [PK], `name` [UK], `description`, `created_at`)
- **`authors`** (`author_id` [PK], `name`, `biography`, `country`, `created_at`)
- **`books`** (`book_id` [PK], `isbn` [UK], `title`, `category_id` [FK], `publisher`, `publication_year`, `edition`, `total_copies`, `available_copies`, `shelf_location`, `created_at`, `updated_at`)
- **`book_authors`** (`book_id` [PK, FK], `author_id` [PK, FK], `is_primary_author`)
- **`members`** (`member_id` [PK], `first_name`, `last_name`, `email` [UK], `phone`, `address`, `membership_date`, `status`, `max_books_allowed`, `created_at`)
- **`staff_users`** (`user_id` [PK], `username` [UK], `password_hash`, `full_name`, `email` [UK], `role`, `is_active`, `created_at`)
- **`loans`** (`loan_id` [PK], `book_id` [FK], `member_id` [FK], `issued_by` [FK], `issue_date`, `due_date`, `return_date`, `status`, `notes`, `created_at`, `updated_at`)
- **`fines`** (`fine_id` [PK], `loan_id` [FK, UK], `amount`, `fine_date`, `payment_date`, `payment_status`, `payment_method`, `remarks`, `created_at`, `updated_at`)

---

### 2. Normalization Analysis (1NF to 3NF/BCNF)

1. **1NF (First Normal Form)**:
   - All attribute values are atomic (e.g., author names are separated into distinct records; member first and last names are stored atomically).
   - Repeating groups of authors are decomposed into the `book_authors` associative table.
2. **2NF (Second Normal Form)**:
   - In 1NF and contains **NO partial functional dependencies**.
   - In `book_authors(book_id, author_id)`, the non-key attribute `is_primary_author` depends strictly on the entire composite key `(book_id, author_id)`.
3. **3NF (Third Normal Form)**:
   - In 2NF and contains **NO transitive functional dependencies**.
   - Category metadata (`name`, `description`) is factored out into `categories`; only `category_id` is referenced in `books`.
4. **BCNF (Boyce-Codd Normal Form)**:
   - For all functional dependencies $X \rightarrow Y$, $X$ is a superkey / candidate key (`isbn`, `email`, `username`, `(book_id, author_id)`).

---

### 3. Triggers & Stored Procedures

#### Trigger: Auto Calculate Fines on Return
```sql
CREATE TRIGGER trg_auto_create_fine_on_return
AFTER UPDATE ON loans
FOR EACH ROW
BEGIN
    DECLARE days_overdue INT;
    DECLARE daily_rate DECIMAL(10, 2) DEFAULT 2.00;
    DECLARE total_fine DECIMAL(10, 2);

    IF (OLD.return_date IS NULL AND NEW.return_date IS NOT NULL) THEN
        IF NEW.return_date > NEW.due_date THEN
            SET days_overdue = DATEDIFF(NEW.return_date, NEW.due_date);
            SET total_fine = days_overdue * daily_rate;
            
            INSERT INTO fines (loan_id, amount, fine_date, payment_status, remarks)
            VALUES (NEW.loan_id, total_fine, CURRENT_DATE, 'Unpaid', 
                    CONCAT('Overdue by ', days_overdue, ' day(s) at $', daily_rate, '/day'))
            ON DUPLICATE KEY UPDATE amount = total_fine;
        END IF;
    END IF;
END;
```

#### Stored Procedure: Safe Book Checkout (sp_issue_book)
```sql
CALL sp_issue_book(
    p_book_id, 
    p_member_id, 
    p_staff_id, 
    p_loan_days, 
    @p_loan_id, 
    @p_status_code, 
    @p_message
);
```
Validates stock availability, member status, active loan limits, and checks for unpaid overdue balances before issuing.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | System health check & active database engine info |
| `GET` | `/api/dashboard/stats` | Live KPI metrics and category distribution |
| `GET` | `/api/books` | List books with search, category, and availability filters |
| `POST` | `/api/books` | Register a new book title into catalog |
| `GET` | `/api/books/<id>` | Fetch book details |
| `PUT` | `/api/books/<id>` | Update book details and inventory |
| `DELETE` | `/api/books/<id>` | Remove book from catalog (if no active loans) |
| `GET` | `/api/members` | List members with active borrow counts |
| `POST` | `/api/members` | Register new library member |
| `GET` | `/api/members/<id>/history` | Fetch member borrowing and return history |
| `GET` | `/api/loans` | List loans (`?status=active`, `?status=overdue`) |
| `POST` | `/api/loans/issue` | Execute book checkout transaction |
| `POST` | `/api/loans/return` | Process return and auto-calculate late fines |
| `GET` | `/api/fines` | Fetch overdue fine ledger |
| `POST` | `/api/fines/pay` | Settle fine payment |
| `GET` | `/api/dbms/views/<view_name>` | Query SQL views dynamically |

---

## 🐙 Pushing to GitHub & Continuous Integration (CI)

### 1. First-Time Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Complete Library Management System"
git branch -M main
git remote add origin https://github.com/shivamgupta13m-hue/library-management-system.git
git push -u origin main
```

### 2. Frequent Push Workflow (Daily Updates)
Whenever you make updates to your code:
```bash
git status
git add .
git commit -m "feat: your concise commit message"
git push
```

### 3. Automated Verification via GitHub Actions
This project includes [`.github/workflows/ci.yml`](.github/workflows/ci.yml), which automatically installs dependencies and executes the entire DBMS test suite (`test_dbms.py`) across Python 3.10, 3.11, and 3.12 on every push.

