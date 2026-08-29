-- ============================================================================
-- DATABASE SCHEMA: Library Management System (DBMS Project)
-- RDBMS: MySQL 8.0+
-- Description: Complete Relational Schema with Tables, Constraints, 
--              Foreign Keys, Indexes, Triggers, Views, and Stored Procedures.
-- ============================================================================

-- Create Database if not exists
CREATE DATABASE IF NOT EXISTS library_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE library_db;

-- ----------------------------------------------------------------------------
-- Drop existing objects in reverse dependency order
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS v_popular_books;
DROP VIEW IF EXISTS v_overdue_loans;
DROP VIEW IF EXISTS v_active_loans;
DROP VIEW IF EXISTS v_book_catalog;

DROP PROCEDURE IF EXISTS sp_return_book;
DROP PROCEDURE IF EXISTS sp_issue_book;

DROP TABLE IF EXISTS fines;
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS book_authors;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS staff_users;

-- ----------------------------------------------------------------------------
-- 1. CATEGORIES TABLE
-- Classifies books into different literary/academic genres
-- ----------------------------------------------------------------------------
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 2. AUTHORS TABLE
-- Stores details about book authors
-- ----------------------------------------------------------------------------
CREATE TABLE authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    biography TEXT,
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_author_name (name)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 3. BOOKS TABLE
-- Core catalog entity with inventory tracking and foreign key to categories
-- ----------------------------------------------------------------------------
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    publisher VARCHAR(150),
    publication_year INT CHECK (publication_year >= 1000 AND publication_year <= 2100),
    edition VARCHAR(50) DEFAULT '1st Edition',
    total_copies INT NOT NULL DEFAULT 1 CHECK (total_copies >= 0),
    available_copies INT NOT NULL DEFAULT 1 CHECK (available_copies >= 0 AND available_copies <= total_copies),
    shelf_location VARCHAR(50),
    cover_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    INDEX idx_book_isbn (isbn),
    INDEX idx_book_title (title)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 4. BOOK_AUTHORS (Bridge Table for M:N Relationship)
-- Resolves Many-to-Many relationship between Books and Authors
-- ----------------------------------------------------------------------------
CREATE TABLE book_authors (
    book_id INT NOT NULL,
    author_id INT NOT NULL,
    is_primary_author BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(author_id) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 5. MEMBERS TABLE
-- Stores patron information, membership status, and loan limits
-- ----------------------------------------------------------------------------
CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(30) NOT NULL,
    address TEXT,
    membership_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    status ENUM('Active', 'Suspended', 'Expired') DEFAULT 'Active',
    max_books_allowed INT DEFAULT 5 CHECK (max_books_allowed >= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_member_email (email),
    INDEX idx_member_status (status)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 6. STAFF_USERS TABLE
-- Librarians and administrators managing the system
-- ----------------------------------------------------------------------------
CREATE TABLE staff_users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    role ENUM('Admin', 'Librarian', 'Assistant') DEFAULT 'Librarian',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 7. LOANS (Borrow Transactions)
-- Records book issue and return cycles (ACID tracking)
-- ----------------------------------------------------------------------------
CREATE TABLE loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    issued_by INT,
    issue_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    due_date DATE NOT NULL,
    return_date DATE NULL,
    status ENUM('Active', 'Returned', 'Overdue') DEFAULT 'Active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(book_id) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    FOREIGN KEY (member_id) REFERENCES members(member_id) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    FOREIGN KEY (issued_by) REFERENCES staff_users(user_id) 
        ON UPDATE CASCADE 
        ON DELETE SET NULL,
    INDEX idx_loan_status (status),
    INDEX idx_loan_dates (issue_date, due_date)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 8. FINES TABLE
-- Tracks penalty amounts calculated for overdue or damaged items
-- ----------------------------------------------------------------------------
CREATE TABLE fines (
    fine_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT NOT NULL UNIQUE,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    fine_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    payment_date DATE NULL,
    payment_status ENUM('Unpaid', 'Paid', 'Waived') DEFAULT 'Unpaid',
    payment_method ENUM('Cash', 'Card', 'UPI', 'Online', 'None') DEFAULT 'None',
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    INDEX idx_fine_status (payment_status)
) ENGINE=InnoDB;

-- ============================================================================
-- DATABASE TRIGGERS
-- ============================================================================

DELIMITER $$

-- Trigger 1: Decrement available copies when a loan is created
CREATE TRIGGER trg_after_loan_insert
AFTER INSERT ON loans
FOR EACH ROW
BEGIN
    IF NEW.status = 'Active' OR NEW.status = 'Overdue' THEN
        UPDATE books 
        SET available_copies = available_copies - 1
        WHERE book_id = NEW.book_id;
    END IF;
END$$

-- Trigger 2: Increment available copies when a book is returned
CREATE TRIGGER trg_after_loan_update
AFTER UPDATE ON loans
FOR EACH ROW
BEGIN
    -- If book was active/overdue and is now returned
    IF (OLD.return_date IS NULL AND NEW.return_date IS NOT NULL) THEN
        UPDATE books 
        SET available_copies = available_copies + 1
        WHERE book_id = NEW.book_id;
    END IF;
END$$

-- Trigger 3: Automatically compute and create fine if returned late
CREATE TRIGGER trg_auto_create_fine_on_return
AFTER UPDATE ON loans
FOR EACH ROW
BEGIN
    DECLARE days_overdue INT;
    DECLARE daily_rate DECIMAL(10, 2) DEFAULT 2.00; -- \$2.00 per day fine
    DECLARE total_fine DECIMAL(10, 2);

    IF (OLD.return_date IS NULL AND NEW.return_date IS NOT NULL) THEN
        IF NEW.return_date > NEW.due_date THEN
            SET days_overdue = DATEDIFF(NEW.return_date, NEW.due_date);
            SET total_fine = days_overdue * daily_rate;
            
            INSERT INTO fines (loan_id, amount, fine_date, payment_status, remarks)
            VALUES (NEW.loan_id, total_fine, CURRENT_DATE, 'Unpaid', 
                    CONCAT('Overdue by ', days_overdue, ' day(s) at \$', daily_rate, '/day'))
            ON DUPLICATE KEY UPDATE 
                amount = total_fine,
                remarks = CONCAT('Overdue by ', days_overdue, ' day(s) at \$', daily_rate, '/day');
        END IF;
    END IF;
END$$

DELIMITER ;

-- ============================================================================
-- DATABASE VIEWS
-- ============================================================================

-- View 1: Unified Book Catalog with Category and Authors concatenated
CREATE OR REPLACE VIEW v_book_catalog AS
SELECT 
    b.book_id,
    b.isbn,
    b.title,
    c.category_id,
    c.name AS category_name,
    GROUP_CONCAT(a.name ORDER BY ba.is_primary_author DESC, a.name SEPARATOR ', ') AS authors,
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
GROUP BY b.book_id, b.isbn, b.title, c.category_id, c.name, b.publisher, 
         b.publication_year, b.edition, b.total_copies, b.available_copies, b.shelf_location;

-- View 2: Active Borrowings View
CREATE OR REPLACE VIEW v_active_loans AS
SELECT 
    l.loan_id,
    l.book_id,
    b.title AS book_title,
    b.isbn,
    l.member_id,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.email AS member_email,
    m.phone AS member_phone,
    l.issue_date,
    l.due_date,
    DATEDIFF(CURRENT_DATE, l.due_date) AS days_overdue,
    CASE 
        WHEN CURRENT_DATE > l.due_date THEN 'Overdue'
        ELSE 'Active'
    END AS calculated_status,
    s.full_name AS issued_by_name
FROM loans l
JOIN books b ON l.book_id = b.book_id
JOIN members m ON l.member_id = m.member_id
LEFT JOIN staff_users s ON l.issued_by = s.user_id
WHERE l.return_date IS NULL;

-- View 3: Overdue Loans with Fine Estimates View
CREATE OR REPLACE VIEW v_overdue_loans AS
SELECT 
    l.loan_id,
    b.title AS book_title,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.email AS member_email,
    m.phone AS member_phone,
    l.issue_date,
    l.due_date,
    DATEDIFF(CURRENT_DATE, l.due_date) AS days_late,
    (DATEDIFF(CURRENT_DATE, l.due_date) * 2.00) AS estimated_fine,
    f.fine_id,
    f.amount AS recorded_fine,
    IFNULL(f.payment_status, 'Unrecorded') AS fine_status
FROM loans l
JOIN books b ON l.book_id = b.book_id
JOIN members m ON l.member_id = m.member_id
LEFT JOIN fines f ON l.loan_id = f.loan_id
WHERE l.return_date IS NULL AND CURRENT_DATE > l.due_date;

-- View 4: Popular Books View (Analytics)
CREATE OR REPLACE VIEW v_popular_books AS
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
GROUP BY b.book_id, b.title, b.isbn, c.name
ORDER BY total_times_borrowed DESC;

-- ============================================================================
-- STORED PROCEDURES (ACID Transactions)
-- ============================================================================

DELIMITER $$

-- Stored Procedure: Issue a book safely with ACID validation
CREATE PROCEDURE sp_issue_book(
    IN p_book_id INT,
    IN p_member_id INT,
    IN p_staff_id INT,
    IN p_loan_days INT,
    OUT p_loan_id INT,
    OUT p_status_code INT,
    OUT p_message VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_available INT DEFAULT 0;
    DECLARE v_member_status VARCHAR(20);
    DECLARE v_current_loans INT DEFAULT 0;
    DECLARE v_max_allowed INT DEFAULT 5;
    DECLARE v_unpaid_fines DECIMAL(10, 2) DEFAULT 0.00;
    DECLARE v_due_date DATE;

    -- Error handler for unexpected SQL exceptions
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_loan_id = NULL;
        SET p_status_code = 500;
        SET p_message = 'Transaction rolled back due to an internal database error.';
    END;

    START TRANSACTION;

    -- Check Book Availability
    SELECT available_copies INTO v_available 
    FROM books 
    WHERE book_id = p_book_id 
    FOR UPDATE;

    IF v_available IS NULL THEN
        ROLLBACK;
        SET p_status_code = 404;
        SET p_message = 'Book ID not found in library catalog.';
        LEAVE proc_label;
    END IF;

    IF v_available <= 0 THEN
        ROLLBACK;
        SET p_status_code = 400;
        SET p_message = 'No available copies left for this book.';
        LEAVE proc_label;
    END IF;

    -- Check Member Status & Limit
    SELECT status, max_books_allowed INTO v_member_status, v_max_allowed 
    FROM members 
    WHERE member_id = p_member_id;

    IF v_member_status IS NULL THEN
        ROLLBACK;
        SET p_status_code = 404;
        SET p_message = 'Member ID not found.';
        LEAVE proc_label;
    END IF;

    IF v_member_status != 'Active' THEN
        ROLLBACK;
        SET p_status_code = 403;
        SET p_message = CONCAT('Cannot issue book. Member account is ', v_member_status, '.');
        LEAVE proc_label;
    END IF;

    -- Check Active Borrow Count
    SELECT COUNT(*) INTO v_current_loans 
    FROM loans 
    WHERE member_id = p_member_id AND return_date IS NULL;

    IF v_current_loans >= v_max_allowed THEN
        ROLLBACK;
        SET p_status_code = 400;
        SET p_message = CONCAT('Member has reached the maximum allowed limit of ', v_max_allowed, ' books.');
        LEAVE proc_label;
    END IF;

    -- Check Unpaid Overdue Fines
    SELECT IFNULL(SUM(f.amount), 0.00) INTO v_unpaid_fines
    FROM fines f
    JOIN loans l ON f.loan_id = l.loan_id
    WHERE l.member_id = p_member_id AND f.payment_status = 'Unpaid';

    IF v_unpaid_fines > 20.00 THEN
        ROLLBACK;
        SET p_status_code = 403;
        SET p_message = CONCAT('Member has outstanding unpaid fines of \$', v_unpaid_fines, '. Please clear dues first.');
        LEAVE proc_label;
    END IF;

    -- Default loan duration 14 days if not specified
    IF p_loan_days IS NULL OR p_loan_days <= 0 THEN
        SET p_loan_days = 14;
    END IF;
    SET v_due_date = DATE_ADD(CURRENT_DATE, INTERVAL p_loan_days DAY);

    -- Insert Loan Record (Trigger will automatically decrement book availability)
    INSERT INTO loans (book_id, member_id, issued_by, issue_date, due_date, status)
    VALUES (p_book_id, p_member_id, p_staff_id, CURRENT_DATE, v_due_date, 'Active');

    SET p_loan_id = LAST_INSERT_ID();
    SET p_status_code = 200;
    SET p_message = 'Book issued successfully.';

    COMMIT;
END$$

-- Stored Procedure: Return a book safely
CREATE PROCEDURE sp_return_book(
    IN p_loan_id INT,
    IN p_return_date DATE,
    OUT p_fine_amount DECIMAL(10, 2),
    OUT p_status_code INT,
    OUT p_message VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_book_id INT;
    DECLARE v_due_date DATE;
    DECLARE v_existing_return DATE;
    DECLARE v_days_late INT DEFAULT 0;
    DECLARE v_fine DECIMAL(10, 2) DEFAULT 0.00;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status_code = 500;
        SET p_message = 'Transaction rolled back due to error during return processing.';
    END;

    START TRANSACTION;

    SELECT book_id, due_date, return_date INTO v_book_id, v_due_date, v_existing_return
    FROM loans
    WHERE loan_id = p_loan_id
    FOR UPDATE;

    IF v_book_id IS NULL THEN
        ROLLBACK;
        SET p_status_code = 404;
        SET p_message = 'Loan transaction record not found.';
        LEAVE proc_label;
    END IF;

    IF v_existing_return IS NOT NULL THEN
        ROLLBACK;
        SET p_status_code = 400;
        SET p_message = 'This book has already been returned previously.';
        LEAVE proc_label;
    END IF;

    IF p_return_date IS NULL THEN
        SET p_return_date = CURRENT_DATE;
    END IF;

    -- Calculate Fine if Overdue
    IF p_return_date > v_due_date THEN
        SET v_days_late = DATEDIFF(p_return_date, v_due_date);
        SET v_fine = v_days_late * 2.00; -- \$2 per day
    END IF;

    -- Update Loan Record (Trigger will automatically increment book availability & create fine record)
    UPDATE loans 
    SET return_date = p_return_date,
        status = 'Returned'
    WHERE loan_id = p_loan_id;

    SET p_fine_amount = v_fine;
    SET p_status_code = 200;
    IF v_fine > 0 THEN
        SET p_message = CONCAT('Book returned successfully. Overdue by ', v_days_late, ' day(s). Fine incurred: \$', v_fine);
    ELSE
        SET p_message = 'Book returned successfully on time with no fines.';
    END IF;

    COMMIT;
END$$

DELIMITER ;
