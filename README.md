# 📚 Library Management System (DBMS Project)

An enterprise-grade **Database Management System (DBMS)** web application built with **HTML5, CSS3, Modern JavaScript (ES6+), Python (Flask), MySQL / SQLite, and Relational ER Modeling**.

This system implements **relational database normalization up to 3NF/BCNF**, automated business rules via **SQL Triggers**, real-time analytical projections via **SQL Views**, concurrency protection with **ACID Stored Procedures**, and a responsive single-page dashboard.

---

## 🌟 Table of Contents
1. [Project Overview & Key Features](#-key-features)
2. [Complete File-by-File Guide](#-complete-file-by-file-guide)
3. [How to Access & Run the Application](#-how-to-access--run-the-application)
4. [Operations Guide (How to Use the App)](#-operations-guide)
   - [Managing Books (Add, Edit, Delete)](#1-managing-books)
   - [Managing Members (Add, History, Suspend/Delete)](#2-managing-members)
   - [Circulation Desk (Issue & Return Books)](#3-circulation-desk)
   - [Fines & Payments](#4-fines--overdue-payments)
5. [Database Architecture & DBMS Specifications](#-database-architecture--dbms-specifications)
   - [Relational Schema Mapping](#1-relational-schema-mapping)
   - [Normalization Analysis (1NF to 3NF/BCNF)](#2-normalization-analysis)
   - [SQL Triggers & Stored Procedures](#3-sql-triggers--stored-procedures)
6. [REST API Reference](#-rest-api-reference)
7. [GitHub & CI/CD Deployment Guide](#-github--cicd-deployment-guide)

---

## 🌟 Key Features

- **Relational Entity-Relationship (ER) Modeling**: 8 normalized entities handling 1:1, 1:N, and M:N relationships.
- **ACID Transactions & Stored Procedures**: Safe checkouts ensuring books cannot be double-borrowed or issued to suspended members.
- **Automated SQL Triggers**: Real-time stock decrement on issue, stock increment on return, and automated penalty calculation on overdue returns.
- **Dual Database Adapter**: Seamlessly runs with **MySQL** for enterprise environments, or automatically falls back to an embedded zero-config **SQLite** database for instant local evaluation.
- **Live Cloud Deployment & CI/CD**: Fully deployed on Render with automated testing pipelines via GitHub Actions across Python 3.10, 3.11, and 3.12.

---

## 📁 Complete File-by-File Guide

Here is the clean directory structure and an explanation of every file and folder in the project:

```text
library_management_system/
├── .github/workflows/ci.yml   # Automated GitHub Actions CI test suite
├── .env.example                # Safe environment variables template
├── .gitignore                  # Git instructions on files to ignore
├── README.md                   # Complete documentation & project manual
├── app.py                      # Main Flask backend server & REST API
├── config.py                   # Configuration parameters & business constants
├── requirements.txt            # Python dependencies (Flask, gunicorn, etc.)
├── test_dbms.py                # Automated DBMS integration & unit test suite
│
├── database/                   # Database schemas, seed data & access logic
│   ├── schema.sql              # MySQL DDL (Tables, triggers, views, procedures)
│   ├── seed_data.sql           # Realistic seed dataset for immediate testing
│   ├── er_diagram_doc.md       # Comprehensive ER modeling & normalization report
│   └── db.py                   # Robust database adapter (MySQL + SQLite fallback)
│
├── static/                     # Frontend Static Assets
│   ├── css/
│   │   └── style.css           # Modern responsive design, cards, colors & layout
│   └── js/
│       └── app.js              # Asynchronous JavaScript controller & API caller
│
└── templates/                  # Flask HTML Templates
    └── index.html              # Single-Page Application UI rendered by Flask
```

---

### 1. Backend & Server Files

#### 🐍 `app.py`
- **What it does**: The central Python backend application powered by **Flask**.
- **How it is used**:
  - Run `python app.py` to start the web server locally on `http://127.0.0.1:5000`.
  - Serves the frontend single-page dashboard (`/`) and static assets (`/static`).
  - Implements complete REST API endpoints:
    - `/api/status`: System health check & active database engine info.
    - `/api/dashboard/stats`: Live KPI counters and category distribution.
    - `/api/books`: Catalog search, book registration, updates, and deletions.
    - `/api/members`: Member registration, directory listings, and borrowing histories.
    - `/api/loans/issue`: Atomic checkout transactions.
    - `/api/loans/return`: Return processing and automated late fine calculation.
    - `/api/fines`: Overdue fine ledger and multi-channel payment settlements.
    - `/api/dbms/views/<name>`: Live SQL analytical view queries.

#### ⚙️ `config.py`
- **What it does**: Centralized configuration and environment variable loader.
- **How it is used**:
  - Reads database credentials (`MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`).
  - Configures business rule constants such as `DAILY_FINE_RATE = 2.00` ($2.00/day late fee) and `DEFAULT_LOAN_DAYS = 14`.

#### 📦 `requirements.txt`
- **What it does**: Manifest of all external Python dependencies.
- **How it is used**:
  - Run `pip install -r requirements.txt` to install `Flask`, `gunicorn`, `mysql-connector-python`, `python-dotenv`, and `Werkzeug`.

#### 🧪 `test_dbms.py`
- **What it does**: Automated end-to-end testing script for the database layer.
- **How it is used**:
  - Run `python test_dbms.py` to test database initialization, book checkouts, overdue calculations, and fine settlements from the terminal.

---

### 2. Database Layer (`database/`)

#### 🗄️ `database/schema.sql`
- **What it does**: The complete MySQL Data Definition Language (DDL) file.
- **How it is used**:
  - Defines all 8 relational tables (`categories`, `authors`, `books`, `book_authors`, `members`, `staff_users`, `loans`, `fines`).
  - Enforces entity and referential integrity (Primary Keys, Foreign Keys with `ON DELETE RESTRICT` / `CASCADE`, Unique constraints, and Check constraints).
  - Contains database Triggers (`trg_after_loan_insert`, `trg_after_loan_update`, `trg_auto_create_fine_on_return`).
  - Contains stored procedures (`sp_issue_book`, `sp_return_book`) with transaction controls (`START TRANSACTION`, `COMMIT`, `ROLLBACK`).
  - Defines analytical SQL views (`v_book_catalog`, `v_active_loans`, `v_overdue_loans`, `v_popular_books`).

#### 🌱 `database/seed_data.sql`
- **What it does**: Realistic sample dataset for immediate testing.
- **How it is used**:
  - Pre-populates the database with categories, computer science/literature books, authors, members, active loans, and overdue records.

#### 📊 `database/er_diagram_doc.md`
- **What it does**: Academic DBMS documentation and project report.
- **How it is used**:
  - Documents the Entity-Relationship (ER) model using both Chen notation and Crow's Foot diagrams.
  - Documents functional dependencies and mathematical normalization proofs up to **1NF, 2NF, 3NF, and BCNF**.

#### 🔌 `database/db.py`
- **What it does**: Database abstraction and connection management layer.
- **How it is used**:
  - Implements a **Dual-Engine Architecture**: connects to MySQL if available; otherwise, automatically initializes and queries an embedded SQLite database (`library_local.sqlite`) with identical schemas and business triggers.

---

### 3. Frontend & User Interface

#### 🌐 `templates/index.html`
- **What it does**: The Single-Page Application (SPA) user interface rendered by Flask.
- **How it is used**:
  - Divided into 6 interactive panels:
    1. **Dashboard Overview**: KPI cards and category distribution charts.
    2. **Book Catalog**: Searchable inventory table with "+ Add Book", Edit, and Delete actions.
    3. **Members Directory**: Patron directory, contact details, and borrowing history modals.
    4. **Circulation Desk**: Book checkout form and active loan monitoring with return processing.
    5. **Fines & Overdues**: Late fee ledger and payment settlement dialog.
    6. **DBMS & ER Docs**: Interactive Mermaid ER diagram viewer and live SQL view inspector.

#### 🎨 `static/css/style.css`
- **What it does**: The stylesheet controlling visual appearance, modern typography, glassmorphism, and responsive layout.
- **How it is used**:
  - Provides variables for theming, sidebar styling, metric cards, badges, modals, and mobile media queries.

#### ⚡ `static/js/app.js`
- **What it does**: The client-side JavaScript engine.
- **How it is used**:
  - Manages view switching without page reloads.
  - Performs asynchronous `fetch()` API requests to Flask endpoints for seamless CRUD operations, live searches, and toast notifications.

---

### 4. Git, CI/CD & Configuration Files

#### 🤖 `.github/workflows/ci.yml`
- **What it does**: Automated GitHub Actions CI pipeline.
- **How it is used**:
  - Automatically installs dependencies and runs the entire DBMS test suite (`test_dbms.py`) across Python 3.10, 3.11, and 3.12 on every push.

#### 🔒 `.env.example`
- **What it does**: Template for configuration settings and database credentials without exposing private secrets.

#### 🙈 `.gitignore`
- **What it does**: Prevents temporary, private, or compiled files (`__pycache__/`, `.env`, `venv/`, local `.sqlite` runtime files) from being tracked in Git.

---

## 🚀 How to Access & Run the Application

### Option 1: Live Cloud Website (Instant Access - No Setup)
The project is hosted live on the web:
👉 **[Open Live Library Management System](https://library-management-system-5wdr.onrender.com)** *(or your Render URL)*

---

### Option 2: Run Locally on Your Computer (Developer Mode)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/shivamgupta13m-hue/library-management-system.git
   cd library-management-system
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**:
   ```bash
   python app.py
   ```

4. **Open in your browser**:
   👉 **`http://127.0.0.1:5000`**

*(If MySQL is running locally, it connects automatically; otherwise, it boots instantly with the embedded SQLite database and seed data ready for testing!)*

---

## 📖 Operations Guide

### 1. Managing Books

#### How to Add a Book:
1. Go to the **Book Catalog** tab in the sidebar.
2. Click the blue **"+ New Book"** button in the top right.
3. Fill in the ISBN, Title, Category, Author, Publisher, Year, and Total Copies.
4. Click **"Save Book"**.

#### How to Edit a Book:
1. In the **Book Catalog** table, find the book you want to modify.
2. Click the grey **"Edit"** button in the Actions column.
3. Update the details and click **"Update Book"**.

#### How to Delete a Book:
1. In the **Book Catalog** table, click the red **Trash button (`🗑️`)** next to the book.
2. A confirmation prompt will appear:
   > *"Are you sure you want to delete this book? This will succeed only if there are no active loans."*
3. Click **OK**.

> [!IMPORTANT]
> **Database Foreign Key Rule**: In a relational database, you cannot delete a book if a copy is currently borrowed by a member (`active loan`). If a book has active loans, go to the **Circulation Desk** and click **"Return Book"** first.

---

### 2. Managing Members

#### How to Register a Member:
1. Click on the **Members** tab in the sidebar.
2. Click the **"+ Register Member"** button.
3. Enter First Name, Last Name, Email, Phone Number, Address, and Borrow Limit.
4. Click **"Register Member"**.

#### How to View Member Borrowing History:
1. Find the member in the directory.
2. Click the **"Loan History"** button.
3. A modal opens showing every book borrowed, checkout date, due date, return date, and fines.

#### How to Suspend or Delete a Member:
- **Suspension (Recommended)**: Set the member's status to **`Suspended`**. The checkout procedure will automatically block loan requests for suspended accounts while preserving historical records.
- **Deletion via SQL**:
  ```sql
  DELETE FROM fines WHERE loan_id IN (SELECT loan_id FROM loans WHERE member_id = 2);
  DELETE FROM loans WHERE member_id = 2;
  DELETE FROM members WHERE member_id = 2;
  ```

---

### 3. Circulation Desk

#### How to Issue a Book:
1. Click on the **Circulation Desk** tab in the sidebar.
2. Select a registered member from the dropdown.
3. Select an available book from the dropdown.
4. Enter the loan duration in days (default is 14 days).
5. Click **"Execute Issue Transaction"**.
   - Validates that copies are available, member is Active, and member limit is not exceeded.
   - Available stock count is automatically decremented.

#### How to Return a Book:
1. Under **Active Borrowings**, locate the loan.
2. Click the green **"Return Book"** button.
3. Verify or adjust the return date.
   - On time: no fine is assessed.
   - Overdue: automatically calculates late fine ($2.00/day).
4. Click **"Confirm Return"**.
   - Book is marked returned, stock count is incremented, and fine ledger is updated.

---

### 4. Fines & Overdue Payments

#### How to Settle a Fine:
1. Click on the **Fines & Overdues** tab in the sidebar.
2. Find the unpaid penalty record.
3. Click the blue **"Pay Fine"** button.
4. Select the payment method (**Cash at Desk**, **UPI / QR Code**, **Debit / Credit Card**, or **Online Portal**).
5. Click **"Confirm Payment"**.

---

## 📐 Database Architecture & DBMS Specifications

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

### 2. Normalization Analysis

1. **1NF (First Normal Form)**:
   - All attribute values are atomic; repeating author groups are decomposed into the `book_authors` junction table.
2. **2NF (Second Normal Form)**:
   - Contains **no partial functional dependencies**. In `book_authors(book_id, author_id)`, `is_primary_author` depends strictly on the entire composite key.
3. **3NF (Third Normal Form)**:
   - Contains **no transitive functional dependencies**. Category details are isolated in `categories`; only `category_id` is referenced in `books`.
4. **BCNF (Boyce-Codd Normal Form)**:
   - For every non-trivial functional dependency $X \rightarrow Y$, $X$ is a superkey (`isbn`, `email`, `username`, `(book_id, author_id)`).

---

### 3. SQL Triggers & Stored Procedures

#### Trigger: Auto-Calculate Fines on Return
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

#### Stored Procedure: Safe Book Checkout (`sp_issue_book`)
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
| `GET` | `/api/dashboard/stats` | KPI metrics and category distribution |
| `GET` | `/api/books` | List books with search, category, and availability filters |
| `POST` | `/api/books` | Register a new book title |
| `GET` | `/api/books/<id>` | Fetch specific book details |
| `PUT` | `/api/books/<id>` | Update book details and inventory copies |
| `DELETE` | `/api/books/<id>` | Remove book from catalog (if no active loans) |
| `GET` | `/api/members` | List members with active borrow counts |
| `POST` | `/api/members` | Register new library member |
| `GET` | `/api/members/<id>/history` | Fetch member borrowing and return history |
| `GET` | `/api/loans` | List loans (`?status=active`, `?status=overdue`) |
| `POST` | `/api/loans/issue` | Execute book checkout transaction |
| `POST` | `/api/loans/return` | Process return and auto-calculate late fines |
| `GET` | `/api/fines` | Fetch overdue fine ledger |
| `POST` | `/api/fines/pay` | Settle fine payment |
| `GET` | `/api/dbms/views/<view_name>` | Query SQL analytical views dynamically |

---

## 🐙 GitHub & CI/CD Deployment Guide

### Frequent Push Workflow (Daily Updates)
Whenever you make updates to your project:
```bash
git status
git add .
git commit -m "feat: your concise commit message"
git push origin main
```

### Automated CI Testing via GitHub Actions
Every time you push code to GitHub:
- The [`.github/workflows/ci.yml`](.github/workflows/ci.yml) workflow triggers automatically.
- Tests database queries, transactions, views, and business rules across Python 3.10, 3.11, and 3.12.
- Provides a green checkmark (**✔ passing**) on your commit.

### Continuous Deployment via Render
- Render is connected directly to your GitHub repository.
- Every time you push changes to `main`, Render automatically rebuilds and redeploys the live application with zero manual effort!
