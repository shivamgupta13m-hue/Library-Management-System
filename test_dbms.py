import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import (
    init_database, get_dashboard_stats, get_books, add_book_record,
    issue_book_transaction, return_book_transaction, pay_fine_record,
    query_all, query_one
)

def run_tests():
    print("--------------------------------------------------")
    print("Testing Library Management System (DBMS) Backend")
    print("--------------------------------------------------")

    # 1. Initialize DB
    init_database()
    print("[PASS] Database initialized successfully.")

    # 2. Test Dashboard Stats
    stats = get_dashboard_stats()
    assert stats['total_titles'] > 0, "Expected seeded book titles"
    print(f"[PASS] Dashboard stats loaded: {stats['total_titles']} titles, {stats['active_loans']} active loans.")

    # 3. Test Get Books
    books = get_books()
    assert len(books) > 0, "Expected books list"
    print(f"[PASS] Books query returned {len(books)} books.")

    # 4. Test Search Book
    clean_code_search = get_books(search="Clean Code")
    assert len(clean_code_search) >= 1, "Expected Clean Code to be found"
    print(f"[PASS] Book search found: {clean_code_search[0]['title']}.")

    # 5. Test Issue Book Transaction
    # Member 3 has no active loan limits
    issue_res = issue_book_transaction(book_id=3, member_id=3, loan_days=14)
    assert issue_res['success'] is True, f"Failed to issue book: {issue_res.get('error')}"
    new_loan_id = issue_res['loan_id']
    print(f"[PASS] Issued Book ID 3 to Member ID 3 -> Loan ID #{new_loan_id}.")

    # 6. Test Return Book Transaction (on-time)
    return_res = return_book_transaction(loan_id=new_loan_id)
    assert return_res['success'] is True, f"Failed to return book: {return_res.get('error')}"
    print(f"[PASS] Returned Loan #{new_loan_id} -> Result: {return_res['message']}")

    # 7. Test Return Book Overdue with Fine
    # Loan 2 is overdue
    return_overdue = return_book_transaction(loan_id=2)
    assert return_overdue['success'] is True, f"Failed to return overdue book: {return_overdue.get('error')}"
    print(f"[PASS] Returned Overdue Loan #2 -> Fine: ${return_overdue['fine_amount']:.2f}")

    # 8. Test Pay Fine
    # Find unpaid fine
    unpaid = query_one("SELECT fine_id, amount FROM fines WHERE payment_status = 'Unpaid' LIMIT 1")
    if unpaid:
        pay_res = pay_fine_record(unpaid['fine_id'], payment_method="UPI")
        assert pay_res['success'] is True, f"Failed to pay fine: {pay_res.get('error')}"
        print(f"[PASS] Paid Fine #{unpaid['fine_id']} (${unpaid['amount']:.2f}) -> {pay_res['message']}")

    # 9. Verify Views
    active_loans_view = query_all("SELECT * FROM v_active_loans")
    print(f"[PASS] v_active_loans view returned {len(active_loans_view)} rows.")
    
    popular_books_view = query_all("SELECT * FROM v_popular_books")
    print(f"[PASS] v_popular_books view returned {len(popular_books_view)} rows.")

    print("--------------------------------------------------")
    print("ALL DBMS BACKEND AND RELATIONAL LOGIC TESTS PASSED!")
    print("--------------------------------------------------")

if __name__ == '__main__':
    run_tests()
