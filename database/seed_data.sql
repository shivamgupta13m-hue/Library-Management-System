-- ============================================================================
-- SEED DATA: Library Management System
-- Provides realistic initial data for testing and demonstration
-- ============================================================================

USE library_db;

-- ----------------------------------------------------------------------------
-- 1. Insert Categories
-- ----------------------------------------------------------------------------
INSERT INTO categories (category_id, name, description) VALUES
(1, 'Computer Science & IT', 'Books on algorithms, programming, databases, AI, and systems engineering.'),
(2, 'Mathematics & Statistics', 'Calculus, linear algebra, discrete mathematics, and probability.'),
(3, 'Physics & Astronomy', 'Classical mechanics, quantum physics, thermodynamics, and astrophysics.'),
(4, 'Literature & Fiction', 'Classic and contemporary novels, drama, and short stories.'),
(5, 'History & Civilizations', 'World history, ancient empires, and political revolutions.'),
(6, 'Philosophy & Ethics', 'Epistemology, moral philosophy, and logic.'),
(7, 'Economics & Finance', 'Microeconomics, macroeconomics, investments, and corporate finance.');

-- ----------------------------------------------------------------------------
-- 2. Insert Authors
-- ----------------------------------------------------------------------------
INSERT INTO authors (author_id, name, biography, country) VALUES
(1, 'Abraham Silberschatz', 'Professor of Computer Science at Yale University, renowned for Database System Concepts.', 'USA'),
(2, 'Henry F. Korth', 'Professor at Lehigh University, co-author of Database System Concepts.', 'USA'),
(3, 'S. Sudarshan', 'Subrao M. Nilekani Chair Professor at IIT Bombay, expert in relational databases.', 'India'),
(4, 'Donald E. Knuth', 'Professor Emeritus at Stanford University, author of The Art of Computer Programming.', 'USA'),
(5, 'Robert C. Martin', 'Software engineer and author famously known as Uncle Bob.', 'USA'),
(6, 'Martin Kleppmann', 'Researcher in distributed systems at University of Cambridge.', 'UK'),
(7, 'Yuval Noah Harari', 'Historian and author of Sapiens: A Brief History of Humankind.', 'Israel'),
(8, 'George Orwell', 'English novelist, essayist, journalist and critic.', 'UK');

-- ----------------------------------------------------------------------------
-- 3. Insert Books
-- ----------------------------------------------------------------------------
INSERT INTO books (book_id, isbn, title, category_id, publisher, publication_year, edition, total_copies, available_copies, shelf_location) VALUES
(1, '978-0078022159', 'Database System Concepts', 1, 'McGraw-Hill Education', 2019, '7th Edition', 8, 6, 'CS-A1-04'),
(2, '978-0132350884', 'Clean Code: A Handbook of Agile Software Craftsmanship', 1, 'Prentice Hall', 2008, '1st Edition', 5, 4, 'CS-B2-11'),
(3, '978-1449373320', 'Designing Data-Intensive Applications', 1, 'O''Reilly Media', 2017, '1st Edition', 6, 5, 'CS-B3-02'),
(4, '978-0201896831', 'The Art of Computer Programming, Vol 1', 1, 'Addison-Wesley', 1997, '3rd Edition', 3, 3, 'CS-A0-01'),
(5, '978-0062316097', 'Sapiens: A Brief History of Humankind', 5, 'Harper', 2015, '1st Edition', 7, 5, 'HIS-C1-08'),
(6, '978-0451524935', '1984', 4, 'Signet Classic', 1950, 'Reissue', 10, 8, 'LIT-D4-19'),
(7, '978-0131103627', 'The C Programming Language', 1, 'Prentice Hall', 1988, '2nd Edition', 4, 3, 'CS-A2-15'),
(8, '978-0262033848', 'Introduction to Algorithms (CLRS)', 1, 'MIT Press', 2009, '3rd Edition', 6, 4, 'CS-A1-01');

-- ----------------------------------------------------------------------------
-- 4. Insert Book-Author Relationships
-- ----------------------------------------------------------------------------
INSERT INTO book_authors (book_id, author_id, is_primary_author) VALUES
(1, 1, TRUE),
(1, 2, FALSE),
(1, 3, FALSE),
(2, 5, TRUE),
(3, 6, TRUE),
(4, 4, TRUE),
(5, 7, TRUE),
(6, 8, TRUE),
(7, 4, TRUE),
(8, 4, TRUE);

-- ----------------------------------------------------------------------------
-- 5. Insert Members
-- ----------------------------------------------------------------------------
INSERT INTO members (member_id, first_name, last_name, email, phone, address, membership_date, status, max_books_allowed) VALUES
(1, 'Aarav', 'Sharma', 'aarav.sharma@example.com', '+91-9876543210', '42 MG Road, Bengaluru, Karnataka', '2023-01-15', 'Active', 5),
(2, 'Diya', 'Patel', 'diya.patel@example.com', '+91-9876543211', '108 SG Highway, Ahmedabad, Gujarat', '2023-02-20', 'Active', 5),
(3, 'Rohan', 'Verma', 'rohan.verma@example.com', '+91-9876543212', '15 Park Street, Kolkata, West Bengal', '2023-03-10', 'Active', 5),
(4, 'Ananya', 'Iyer', 'ananya.iyer@example.com', '+91-9876543213', '7 Anna Salai, Chennai, Tamil Nadu', '2023-04-05', 'Active', 5),
(5, 'Vikram', 'Malhotra', 'vikram.m@example.com', '+91-9876543214', '88 Connaught Place, New Delhi', '2022-11-12', 'Suspended', 2),
(6, 'Sneha', 'Reddy', 'sneha.reddy@example.com', '+91-9876543215', '24 Banjara Hills, Hyderabad, Telangana', '2023-06-01', 'Active', 5);

-- ----------------------------------------------------------------------------
-- 6. Insert Staff / Librarians
-- ----------------------------------------------------------------------------
INSERT INTO staff_users (user_id, username, password_hash, full_name, email, role, is_active) VALUES
(1, 'admin', 'pbkdf2:sha256:260000$admin$defaultpasswordhash', 'Chief Librarian Sarah', 'admin.library@example.com', 'Admin', TRUE),
(2, 'librarian1', 'pbkdf2:sha256:260000$lib1$defaultpasswordhash', 'James Wilson', 'james.w@example.com', 'Librarian', TRUE);

-- ----------------------------------------------------------------------------
-- 7. Insert Loans
-- ----------------------------------------------------------------------------
-- Loan 1: Active, On-time (due in 10 days)
INSERT INTO loans (loan_id, book_id, member_id, issued_by, issue_date, due_date, return_date, status, notes) VALUES
(1, 1, 1, 1, DATE_SUB(CURRENT_DATE, INTERVAL 4 DAY), DATE_ADD(CURRENT_DATE, INTERVAL 10 DAY), NULL, 'Active', 'Standard issue for 14 days'),

-- Loan 2: Active, OVERDUE (due 5 days ago)
(2, 2, 2, 1, DATE_SUB(CURRENT_DATE, INTERVAL 19 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 5 DAY), NULL, 'Overdue', 'Automatic notification sent'),

-- Loan 3: Returned on time
(3, 3, 3, 2, DATE_SUB(CURRENT_DATE, INTERVAL 20 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 6 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY), 'Returned', 'Returned in perfect condition'),

-- Loan 4: Returned late with Fine
(4, 5, 4, 1, DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 16 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 11 DAY), 'Returned', 'Returned 5 days late'),

-- Loan 5: Active, OVERDUE (due 8 days ago)
(5, 6, 1, 2, DATE_SUB(CURRENT_DATE, INTERVAL 22 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 8 DAY), NULL, 'Overdue', 'Second notice dispatched'),

-- Loan 6: Active, On-time (due in 6 days)
(6, 1, 4, 2, DATE_SUB(CURRENT_DATE, INTERVAL 8 DAY), DATE_ADD(CURRENT_DATE, INTERVAL 6 DAY), NULL, 'Active', 'Exam preparation borrow');

-- ----------------------------------------------------------------------------
-- 8. Insert Fines
-- ----------------------------------------------------------------------------
-- Fine for Loan 4 (Returned 5 days late @ \$2/day = \$10.00, Marked as Paid)
INSERT INTO fines (fine_id, loan_id, amount, fine_date, payment_date, payment_status, payment_method, remarks) VALUES
(1, 4, 10.00, DATE_SUB(CURRENT_DATE, INTERVAL 11 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 11 DAY), 'Paid', 'UPI', 'Paid at circulation desk via UPI QR');

-- Update available copies count accurately to reflect loans inserted above
-- Book 1: 8 total - 2 active loans = 6 available
-- Book 2: 5 total - 1 active loan = 4 available
-- Book 3: 6 total - 0 active = 6 available
-- Book 5: 7 total - 0 active = 7 available (Loan 4 returned, Loan 5 is Book 6)
-- Book 6: 10 total - 1 active loan = 9 available
-- Book 7: 4 total - 1 active loan = 3 available (from Loan 6: Book 7 or adjust)
UPDATE books SET available_copies = 6 WHERE book_id = 1;
UPDATE books SET available_copies = 4 WHERE book_id = 2;
UPDATE books SET available_copies = 6 WHERE book_id = 3;
UPDATE books SET available_copies = 3 WHERE book_id = 4;
UPDATE books SET available_copies = 7 WHERE book_id = 5;
UPDATE books SET available_copies = 9 WHERE book_id = 6;
UPDATE books SET available_copies = 4 WHERE book_id = 7;
UPDATE books SET available_copies = 6 WHERE book_id = 8;
