/**
 * Library Management System (DBMS Project) - Frontend Controller
 * Fully asynchronous ES6+ application handling REST API communication,
 * DOM updates, modal management, and DBMS view inspection.
 * Includes seamless Offline / Static Preview Fallback for GitHub Pages and local file preview.
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadDashboardStats();
    loadCategoriesDropdowns();
    initEventListeners();
});

// Global state cache
let categoriesCache = [];
let membersCache = [];
let booksCache = [];
let isOfflineMode = false;

// Realistic Demo Dataset used when Flask server is offline or HTML is opened as file
const MOCK_DATA = {
    stats: {
        engine: "Demo Mode (Run 'python app.py' for Live SQL Database)",
        total_titles: 8,
        total_copies: 49,
        available_copies: 40,
        active_loans: 4,
        overdue_loans: 2,
        fines_collected: 10.00,
        category_distribution: [
            { name: "Computer Science & IT", copy_count: 22, book_count: 5 },
            { name: "Literature & Fiction", copy_count: 10, book_count: 1 },
            { name: "History & Civilizations", copy_count: 7, book_count: 1 },
            { name: "Mathematics & Statistics", copy_count: 6, book_count: 1 },
            { name: "Economics & Finance", copy_count: 4, book_count: 0 }
        ],
        recent_loans: [
            { loan_id: 1, book_title: "Database System Concepts", member_name: "Aarav Sharma", issue_date: "2026-08-22", due_date: "2026-09-05", status: "Active" },
            { loan_id: 2, book_title: "Clean Code", member_name: "Diya Patel", issue_date: "2026-08-07", due_date: "2026-08-21", status: "Overdue" },
            { loan_id: 3, book_title: "Designing Data-Intensive Applications", member_name: "Rohan Verma", issue_date: "2026-08-06", due_date: "2026-08-20", status: "Returned" },
            { loan_id: 4, book_title: "1984", member_name: "Ananya Iyer", issue_date: "2026-08-04", due_date: "2026-08-18", status: "Overdue" }
        ]
    },
    categories: [
        { category_id: 1, name: "Computer Science & IT" },
        { category_id: 2, name: "Mathematics & Statistics" },
        { category_id: 3, name: "Physics & Astronomy" },
        { category_id: 4, name: "Literature & Fiction" },
        { category_id: 5, name: "History & Civilizations" },
        { category_id: 6, name: "Economics & Finance" }
    ],
    books: [
        { book_id: 1, isbn: "978-0078022159", title: "Database System Concepts", category_id: 1, category_name: "Computer Science & IT", authors: "Abraham Silberschatz, Henry F. Korth, S. Sudarshan", publisher: "McGraw-Hill Education", publication_year: 2019, edition: "7th Edition", total_copies: 8, available_copies: 6, shelf_location: "CS-A1-04" },
        { book_id: 2, isbn: "978-0132350884", title: "Clean Code: A Handbook of Agile Software Craftsmanship", category_id: 1, category_name: "Computer Science & IT", authors: "Robert C. Martin", publisher: "Prentice Hall", publication_year: 2008, edition: "1st Edition", total_copies: 5, available_copies: 4, shelf_location: "CS-B2-11" },
        { book_id: 3, isbn: "978-1449373320", title: "Designing Data-Intensive Applications", category_id: 1, category_name: "Computer Science & IT", authors: "Martin Kleppmann", publisher: "O'Reilly Media", publication_year: 2017, edition: "1st Edition", total_copies: 6, available_copies: 5, shelf_location: "CS-B3-02" },
        { book_id: 4, isbn: "978-0201896831", title: "The Art of Computer Programming, Vol 1", category_id: 1, category_name: "Computer Science & IT", authors: "Donald E. Knuth", publisher: "Addison-Wesley", publication_year: 1997, edition: "3rd Edition", total_copies: 3, available_copies: 3, shelf_location: "CS-A0-01" },
        { book_id: 5, isbn: "978-0062316097", title: "Sapiens: A Brief History of Humankind", category_id: 5, category_name: "History & Civilizations", authors: "Yuval Noah Harari", publisher: "Harper", publication_year: 2015, edition: "1st Edition", total_copies: 7, available_copies: 5, shelf_location: "HIS-C1-08" },
        { book_id: 6, isbn: "978-0451524935", title: "1984", category_id: 4, category_name: "Literature & Fiction", authors: "George Orwell", publisher: "Signet Classic", publication_year: 1950, edition: "Reissue", total_copies: 10, available_copies: 8, shelf_location: "LIT-D4-19" },
        { book_id: 7, isbn: "978-0131103627", title: "The C Programming Language", category_id: 1, category_name: "Computer Science & IT", authors: "Brian W. Kernighan, Dennis M. Ritchie", publisher: "Prentice Hall", publication_year: 1988, edition: "2nd Edition", total_copies: 4, available_copies: 3, shelf_location: "CS-A2-15" },
        { book_id: 8, isbn: "978-0262033848", title: "Introduction to Algorithms (CLRS)", category_id: 1, category_name: "Computer Science & IT", authors: "Thomas H. Cormen, Charles E. Leiserson", publisher: "MIT Press", publication_year: 2009, edition: "3rd Edition", total_copies: 6, available_copies: 6, shelf_location: "CS-A1-01" }
    ],
    members: [
        { member_id: 1, first_name: "Aarav", last_name: "Sharma", email: "aarav.sharma@example.com", phone: "+91-9876543210", status: "Active", active_borrow_count: 2, max_books_allowed: 5, unpaid_fine_amount: 0.00 },
        { member_id: 2, first_name: "Diya", last_name: "Patel", email: "diya.patel@example.com", phone: "+91-9876543211", status: "Active", active_borrow_count: 1, max_books_allowed: 5, unpaid_fine_amount: 10.00 },
        { member_id: 3, first_name: "Rohan", last_name: "Verma", email: "rohan.verma@example.com", phone: "+91-9876543212", status: "Active", active_borrow_count: 0, max_books_allowed: 5, unpaid_fine_amount: 0.00 },
        { member_id: 4, first_name: "Ananya", last_name: "Iyer", email: "ananya.iyer@example.com", phone: "+91-9876543213", status: "Active", active_borrow_count: 1, max_books_allowed: 5, unpaid_fine_amount: 0.00 },
        { member_id: 5, first_name: "Vikram", last_name: "Malhotra", email: "vikram.m@example.com", phone: "+91-9876543214", status: "Suspended", active_borrow_count: 0, max_books_allowed: 2, unpaid_fine_amount: 25.00 },
        { member_id: 6, first_name: "Sneha", last_name: "Reddy", email: "sneha.reddy@example.com", phone: "+91-9876543215", status: "Active", active_borrow_count: 0, max_books_allowed: 5, unpaid_fine_amount: 0.00 }
    ],
    loans: [
        { loan_id: 1, book_id: 1, book_title: "Database System Concepts", member_id: 1, member_name: "Aarav Sharma", member_email: "aarav.sharma@example.com", issue_date: "2026-08-22", due_date: "2026-09-05", days_overdue: 0, status: "Active" },
        { loan_id: 2, book_id: 2, book_title: "Clean Code", member_id: 2, member_name: "Diya Patel", member_email: "diya.patel@example.com", issue_date: "2026-08-07", due_date: "2026-08-21", days_overdue: 5, status: "Overdue" },
        { loan_id: 5, book_id: 6, book_title: "1984", member_id: 1, member_name: "Aarav Sharma", member_email: "aarav.sharma@example.com", issue_date: "2026-08-04", due_date: "2026-08-18", days_overdue: 8, status: "Overdue" },
        { loan_id: 6, book_id: 7, book_title: "The C Programming Language", member_id: 4, member_name: "Ananya Iyer", member_email: "ananya.iyer@example.com", issue_date: "2026-08-18", due_date: "2026-09-01", days_overdue: 0, status: "Active" }
    ],
    fines: [
        { fine_id: 1, member_name: "Diya Patel", member_email: "diya.patel@example.com", book_title: "Clean Code", amount: 10.00, fine_date: "2026-08-21", payment_status: "Unpaid", payment_method: "None" },
        { fine_id: 2, member_name: "Ananya Iyer", member_email: "ananya.iyer@example.com", book_title: "Sapiens", amount: 10.00, fine_date: "2026-08-15", payment_status: "Paid", payment_method: "UPI" }
    ]
};

// -----------------------------------------------------------------------------
// 1. Navigation & View Switching
// -----------------------------------------------------------------------------
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const viewPanels = document.querySelectorAll('.view-panel');
    const pageTitle = document.getElementById('pageTitleText');
    const pageSubtitle = document.getElementById('pageSubtitleText');

    const viewTitles = {
        'dashboard-view': { title: 'Dashboard Overview', sub: 'Real-time library analytics, KPIs, and recent activity' },
        'books-view': { title: 'Book Catalog & Inventory', sub: 'Manage titles, authors, genres, and stock quantities' },
        'members-view': { title: 'Library Members Directory', sub: 'Manage patron memberships, borrow limits, and histories' },
        'circulation-view': { title: 'Circulation Desk', sub: 'Issue new books, process returns, and track overdue items' },
        'fines-view': { title: 'Fine & Overdue Management', sub: 'Track penalty collections, dues, and payment statuses' },
        'dbms-docs-view': { title: 'DBMS Architecture & ER Modeling', sub: 'Inspect relational schemas, normalization proofs, views, and triggers' }
    };

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetView = link.getAttribute('data-view');
            if (!targetView) return;

            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            viewPanels.forEach(panel => {
                if (panel.id === targetView) {
                    panel.classList.add('active');
                } else {
                    panel.classList.remove('active');
                }
            });

            if (viewTitles[targetView]) {
                pageTitle.textContent = viewTitles[targetView].title;
                pageSubtitle.textContent = viewTitles[targetView].sub;
            }

            // Lazy load view data
            if (targetView === 'dashboard-view') loadDashboardStats();
            if (targetView === 'books-view') loadBooks();
            if (targetView === 'members-view') loadMembers();
            if (targetView === 'circulation-view') loadCirculationData();
            if (targetView === 'fines-view') loadFines();
            if (targetView === 'dbms-docs-view') inspectDbmsView('v_book_catalog');
        });
    });
}

// -----------------------------------------------------------------------------
// 2. Dashboard KPIs & Charts
// -----------------------------------------------------------------------------
async function loadDashboardStats() {
    let data;
    try {
        const res = await fetch('/api/dashboard/stats');
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        data = json.data;
        isOfflineMode = false;
    } catch (err) {
        // Graceful fallback for static preview / GitHub Pages
        isOfflineMode = true;
        data = MOCK_DATA.stats;
    }

    renderDashboardData(data);
}

function renderDashboardData(data) {
    const badgeEl = document.getElementById('dbEngineBadge');
    if (badgeEl) {
        badgeEl.textContent = data.engine;
        const dot = document.querySelector('.status-dot');
        if (dot) {
            dot.style.backgroundColor = isOfflineMode ? 'var(--warning)' : 'var(--success)';
            dot.style.boxShadow = isOfflineMode ? '0 0 8px var(--warning)' : '0 0 8px var(--success)';
        }
    }

    document.getElementById('statTotalTitles').textContent = data.total_titles;
    document.getElementById('statTotalCopies').textContent = data.total_copies;
    document.getElementById('statAvailableCopies').textContent = data.available_copies;
    document.getElementById('statActiveLoans').textContent = data.active_loans;
    document.getElementById('statOverdueLoans').textContent = data.overdue_loans;
    document.getElementById('statFinesCollected').textContent = `$${parseFloat(data.fines_collected).toFixed(2)}`;

    // Render Category Progress Bars
    const catContainer = document.getElementById('categoryProgressContainer');
    if (catContainer) {
        catContainer.innerHTML = '';
        const maxCopies = Math.max(...data.category_distribution.map(c => c.copy_count || 0), 1);

        data.category_distribution.forEach(cat => {
            const percent = Math.round(((cat.copy_count || 0) / maxCopies) * 100);
            const row = document.createElement('div');
            row.className = 'category-stat-row';
            row.innerHTML = `
                <div class="category-stat-header">
                    <span>${escapeHtml(cat.name)}</span>
                    <span><strong>${cat.copy_count || 0} copies</strong> (${cat.book_count || 0} titles)</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${percent}%"></div>
                </div>
            `;
            catContainer.appendChild(row);
        });
    }

    // Render Recent Activity
    const recentTable = document.getElementById('recentActivityTableBody');
    if (recentTable) {
        recentTable.innerHTML = '';
        if (!data.recent_loans || data.recent_loans.length === 0) {
            recentTable.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#888;">No recent borrow transactions recorded.</td></tr>`;
        } else {
            data.recent_loans.forEach(loan => {
                const tr = document.createElement('tr');
                const badgeClass = loan.status === 'Returned' ? 'badge-success' : (loan.status === 'Overdue' ? 'badge-danger' : 'badge-info');
                tr.innerHTML = `
                    <td><strong>#${loan.loan_id}</strong></td>
                    <td>${escapeHtml(loan.book_title)}</td>
                    <td>${escapeHtml(loan.member_name)}</td>
                    <td>${loan.issue_date}</td>
                    <td>${loan.due_date}</td>
                    <td><span class="badge ${badgeClass}">${loan.status}</span></td>
                `;
                recentTable.appendChild(tr);
            });
        }
    }
}

// -----------------------------------------------------------------------------
// 3. Books Catalog Operations
// -----------------------------------------------------------------------------
async function loadBooks() {
    const search = (document.getElementById('bookSearchInput')?.value || '').toLowerCase();
    const catId = document.getElementById('bookCategoryFilter')?.value || '';
    const availability = document.getElementById('bookAvailabilityFilter')?.value || '';

    try {
        const url = new URL('/api/books', window.location.origin);
        if (search) url.searchParams.append('search', search);
        if (catId) url.searchParams.append('category_id', catId);
        if (availability) url.searchParams.append('availability', availability);

        const res = await fetch(url);
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        booksCache = json.data;
    } catch (err) {
        // Fallback for offline / static preview
        booksCache = MOCK_DATA.books.filter(b => {
            const matchesSearch = !search || b.title.toLowerCase().includes(search) || b.isbn.includes(search) || (b.authors && b.authors.toLowerCase().includes(search));
            const matchesCat = !catId || b.category_id == catId;
            const matchesStock = !availability || (availability === 'available' ? b.available_copies > 0 : b.available_copies === 0);
            return matchesSearch && matchesCat && matchesStock;
        });
    }

    renderBooksTable(booksCache);
}

function renderBooksTable(books) {
    const tbody = document.getElementById('booksTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!books || books.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem; color:#888;">No books match your criteria.</td></tr>`;
        return;
    }

    books.forEach(book => {
        const tr = document.createElement('tr');
        const stockBadge = book.available_copies > 0 
            ? `<span class="badge badge-success">${book.available_copies} of ${book.total_copies} Available</span>`
            : `<span class="badge badge-danger">Out of Stock (${book.total_copies} Total)</span>`;

        tr.innerHTML = `
            <td><code>${escapeHtml(book.isbn)}</code></td>
            <td>
                <strong>${escapeHtml(book.title)}</strong>
                <div style="font-size:0.75rem; color:var(--gray-500);">${escapeHtml(book.publisher || 'Unknown Publisher')} • ${book.edition || '1st Ed.'} (${book.publication_year || 'N/A'})</div>
            </td>
            <td><span class="badge badge-secondary">${escapeHtml(book.category_name)}</span></td>
            <td>${escapeHtml(book.authors || 'Unknown')}</td>
            <td>${stockBadge}</td>
            <td><span style="font-size:0.8rem; font-family:monospace; background:var(--gray-100); padding:2px 6px; border-radius:4px;">${escapeHtml(book.shelf_location || 'General')}</span></td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick="openEditBookModal(${book.book_id})"><i class="fas fa-edit"></i> Edit</button>
                <button class="btn btn-danger btn-sm" onclick="deleteBook(${book.book_id})"><i class="fas fa-trash"></i></button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function handleAddBook(e) {
    e.preventDefault();
    const form = e.target;
    const payload = {
        isbn: form.isbn.value.trim(),
        title: form.title.value.trim(),
        category_id: parseInt(form.category_id.value),
        author_name: form.author_name.value.trim(),
        publisher: form.publisher.value.trim(),
        publication_year: parseInt(form.publication_year.value) || 2024,
        edition: form.edition.value.trim(),
        total_copies: parseInt(form.total_copies.value) || 1,
        shelf_location: form.shelf_location.value.trim()
    };

    try {
        const res = await fetch('/api/books', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        showToast('Book added successfully!', 'success');
    } catch (err) {
        // Offline demo addition
        payload.book_id = MOCK_DATA.books.length + 1;
        payload.authors = payload.author_name;
        payload.available_copies = payload.total_copies;
        const cat = MOCK_DATA.categories.find(c => c.category_id === payload.category_id);
        payload.category_name = cat ? cat.name : 'General';
        MOCK_DATA.books.unshift(payload);
        showToast('Book added to catalog (Demo Mode)!', 'success');
    }

    closeModal('addBookModal');
    form.reset();
    loadBooks();
    loadDashboardStats();
}

function openEditBookModal(bookId) {
    const book = booksCache.find(b => b.book_id === bookId) || MOCK_DATA.books.find(b => b.book_id === bookId);
    if (!book) return;

    const form = document.getElementById('editBookForm');
    form.book_id.value = book.book_id;
    form.title.value = book.title;
    form.category_id.value = book.category_id;
    form.publisher.value = book.publisher || '';
    form.publication_year.value = book.publication_year || '';
    form.edition.value = book.edition || '1st Edition';
    form.total_copies.value = book.total_copies;
    form.shelf_location.value = book.shelf_location || '';

    openModal('editBookModal');
}

async function handleUpdateBook(e) {
    e.preventDefault();
    const form = e.target;
    const bookId = parseInt(form.book_id.value);
    const payload = {
        title: form.title.value.trim(),
        category_id: parseInt(form.category_id.value),
        publisher: form.publisher.value.trim(),
        publication_year: parseInt(form.publication_year.value) || null,
        edition: form.edition.value.trim(),
        total_copies: parseInt(form.total_copies.value) || 1,
        shelf_location: form.shelf_location.value.trim()
    };

    try {
        const res = await fetch(`/api/books/${bookId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        showToast('Book updated successfully!', 'success');
    } catch (err) {
        // Offline demo update
        const idx = MOCK_DATA.books.findIndex(b => b.book_id === bookId);
        if (idx !== -1) {
            Object.assign(MOCK_DATA.books[idx], payload);
        }
        showToast('Book updated (Demo Mode)!', 'success');
    }

    closeModal('editBookModal');
    loadBooks();
    loadDashboardStats();
}

async function deleteBook(bookId) {
    if (!confirm('Are you sure you want to delete this book? This will succeed only if there are no active loans.')) return;

    try {
        const res = await fetch(`/api/books/${bookId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        showToast('Book deleted from catalog.', 'success');
    } catch (err) {
        MOCK_DATA.books = MOCK_DATA.books.filter(b => b.book_id !== bookId);
        showToast('Book removed (Demo Mode).', 'success');
    }

    loadBooks();
    loadDashboardStats();
}

// -----------------------------------------------------------------------------
// 4. Members Operations
// -----------------------------------------------------------------------------
async function loadMembers() {
    const search = (document.getElementById('memberSearchInput')?.value || '').toLowerCase();

    try {
        const url = new URL('/api/members', window.location.origin);
        if (search) url.searchParams.append('search', search);

        const res = await fetch(url);
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        membersCache = json.data;
    } catch (err) {
        membersCache = MOCK_DATA.members.filter(m => {
            return !search || m.first_name.toLowerCase().includes(search) || m.last_name.toLowerCase().includes(search) || m.email.toLowerCase().includes(search);
        });
    }

    renderMembersTable(membersCache);
}

function renderMembersTable(members) {
    const tbody = document.getElementById('membersTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!members || members.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem; color:#888;">No members found.</td></tr>`;
        return;
    }

    members.forEach(m => {
        const tr = document.createElement('tr');
        const statusBadge = m.status === 'Active' ? 'badge-success' : 'badge-danger';
        const fineBadge = m.unpaid_fine_amount > 0 
            ? `<span class="badge badge-danger">$${parseFloat(m.unpaid_fine_amount).toFixed(2)} Due</span>`
            : `<span class="badge badge-success">Clear ($0)</span>`;

        tr.innerHTML = `
            <td><strong>#${m.member_id}</strong></td>
            <td><strong>${escapeHtml(m.first_name)} ${escapeHtml(m.last_name)}</strong></td>
            <td>
                <div>${escapeHtml(m.email)}</div>
                <div style="font-size:0.75rem; color:var(--gray-500);">${escapeHtml(m.phone)}</div>
            </td>
            <td><span class="badge ${statusBadge}">${m.status}</span></td>
            <td><strong>${m.active_borrow_count}</strong> / ${m.max_books_allowed} books</td>
            <td>${fineBadge}</td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick="viewMemberHistory(${m.member_id})"><i class="fas fa-history"></i> Loan History</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function handleAddMember(e) {
    e.preventDefault();
    const form = e.target;
    const payload = {
        first_name: form.first_name.value.trim(),
        last_name: form.last_name.value.trim(),
        email: form.email.value.trim(),
        phone: form.phone.value.trim(),
        address: form.address.value.trim(),
        max_books_allowed: parseInt(form.max_books_allowed.value) || 5,
        status: form.status.value
    };

    try {
        const res = await fetch('/api/members', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        showToast('Member registered successfully!', 'success');
    } catch (err) {
        payload.member_id = MOCK_DATA.members.length + 1;
        payload.active_borrow_count = 0;
        payload.unpaid_fine_amount = 0;
        MOCK_DATA.members.unshift(payload);
        showToast('Member registered (Demo Mode)!', 'success');
    }

    closeModal('addMemberModal');
    form.reset();
    loadMembers();
    loadDashboardStats();
}

async function viewMemberHistory(memberId) {
    let history = [];
    try {
        const res = await fetch(`/api/members/${memberId}/history`);
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        history = json.data;
    } catch (err) {
        history = MOCK_DATA.loans.filter(l => l.member_id === memberId);
    }

    const tbody = document.getElementById('memberHistoryTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (history.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:1.5rem; color:#888;">No borrowing history for this member.</td></tr>`;
    } else {
        history.forEach(item => {
            const tr = document.createElement('tr');
            const badge = item.status === 'Returned' ? 'badge-success' : (item.status === 'Overdue' ? 'badge-danger' : 'badge-info');
            tr.innerHTML = `
                <td>#${item.loan_id}</td>
                <td><strong>${escapeHtml(item.book_title)}</strong></td>
                <td>${item.issue_date}</td>
                <td>${item.due_date}</td>
                <td>${item.return_date || '<em>Not Returned</em>'}</td>
                <td><span class="badge ${badge}">${item.status}</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    openModal('memberHistoryModal');
}

// -----------------------------------------------------------------------------
// 5. Circulation Operations (Issue & Return Book)
// -----------------------------------------------------------------------------
async function loadCirculationData() {
    loadMembersDropdown();
    loadAvailableBooksDropdown();
    loadActiveLoansTable();
}

async function loadMembersDropdown() {
    let members = [];
    try {
        const res = await fetch('/api/members');
        if (!res.ok) throw new Error();
        const json = await res.json();
        members = json.data;
    } catch (err) {
        members = MOCK_DATA.members;
    }

    const select = document.getElementById('issueMemberSelect');
    if (!select) return;
    select.innerHTML = '<option value="">-- Choose Member --</option>';
    members.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.member_id;
        opt.textContent = `${m.first_name} ${m.last_name} (${m.email}) [Active: ${m.active_borrow_count}/${m.max_books_allowed}]`;
        select.appendChild(opt);
    });
}

async function loadAvailableBooksDropdown() {
    let books = [];
    try {
        const res = await fetch('/api/books?availability=available');
        if (!res.ok) throw new Error();
        const json = await res.json();
        books = json.data;
    } catch (err) {
        books = MOCK_DATA.books.filter(b => b.available_copies > 0);
    }

    const select = document.getElementById('issueBookSelect');
    if (!select) return;
    select.innerHTML = '<option value="">-- Choose Available Book --</option>';
    books.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b.book_id;
        opt.textContent = `${b.title} (ISBN: ${b.isbn}) - ${b.available_copies} copy(s) in stock`;
        select.appendChild(opt);
    });
}

async function loadActiveLoansTable() {
    let loans = [];
    try {
        const res = await fetch('/api/loans?status=active');
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        loans = json.data;
    } catch (err) {
        loans = MOCK_DATA.loans;
    }

    const tbody = document.getElementById('activeLoansTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!loans || loans.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:#888;">No active loans at this time. All books are accounted for!</td></tr>`;
        return;
    }

    loans.forEach(loan => {
        const tr = document.createElement('tr');
        const isLate = (loan.days_overdue || 0) > 0;
        const statusBadge = isLate 
            ? `<span class="badge badge-danger">Overdue (${loan.days_overdue} days)</span>` 
            : `<span class="badge badge-info">Active</span>`;

        tr.innerHTML = `
            <td><strong>#${loan.loan_id}</strong></td>
            <td><strong>${escapeHtml(loan.book_title)}</strong></td>
            <td>
                <div>${escapeHtml(loan.member_name)}</div>
                <div style="font-size:0.75rem; color:var(--gray-500);">${escapeHtml(loan.member_email)}</div>
            </td>
            <td>${loan.issue_date}</td>
            <td><strong>${loan.due_date}</strong></td>
            <td>${statusBadge}</td>
            <td>
                <button class="btn btn-success btn-sm" onclick="openReturnModal(${loan.loan_id}, '${escapeHtml(loan.book_title)}', '${loan.due_date}')">
                    <i class="fas fa-undo"></i> Return Book
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function handleIssueBook(e) {
    e.preventDefault();
    const form = e.target;
    const bookId = parseInt(form.book_id.value);
    const memberId = parseInt(form.member_id.value);
    const loanDays = parseInt(form.loan_days.value) || 14;

    try {
        const res = await fetch('/api/loans/issue', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ book_id: bookId, member_id: memberId, loan_days: loanDays })
        });
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        showToast(json.message || 'Book issued successfully!', 'success');
    } catch (err) {
        // Offline demo issuance
        const book = MOCK_DATA.books.find(b => b.book_id === bookId);
        const member = MOCK_DATA.members.find(m => m.member_id === memberId);
        if (book && member) {
            book.available_copies = Math.max(0, book.available_copies - 1);
            member.active_borrow_count += 1;
            const due = new Date();
            due.setDate(due.getDate() + loanDays);
            MOCK_DATA.loans.unshift({
                loan_id: MOCK_DATA.loans.length + 1,
                book_id: bookId,
                book_title: book.title,
                member_id: memberId,
                member_name: `${member.first_name} ${member.last_name}`,
                member_email: member.email,
                issue_date: new Date().toISOString().split('T')[0],
                due_date: due.toISOString().split('T')[0],
                days_overdue: 0,
                status: 'Active'
            });
            showToast('Book issued (Demo Mode)!', 'success');
        }
    }

    form.reset();
    loadCirculationData();
    loadDashboardStats();
}

function openReturnModal(loanId, bookTitle, dueDate) {
    const form = document.getElementById('returnBookForm');
    form.loan_id.value = loanId;
    document.getElementById('returnModalBookTitle').textContent = bookTitle;
    document.getElementById('returnModalDueDate').textContent = dueDate;
    
    const todayStr = new Date().toISOString().split('T')[0];
    form.return_date.value = todayStr;
    calculateReturnEstimate();

    openModal('returnBookModal');
}

function calculateReturnEstimate() {
    const form = document.getElementById('returnBookForm');
    const dueDateStr = document.getElementById('returnModalDueDate').textContent;
    const returnDateStr = form.return_date.value;

    const previewBox = document.getElementById('returnFinePreview');
    if (!dueDateStr || !returnDateStr) return;

    const due = new Date(dueDateStr);
    const ret = new Date(returnDateStr);
    const diffDays = Math.ceil((ret - due) / (1000 * 60 * 60 * 24));

    if (diffDays > 0) {
        const fine = (diffDays * 2.00).toFixed(2);
        previewBox.innerHTML = `<div style="color:var(--danger); font-weight:600;"><i class="fas fa-exclamation-triangle"></i> Book is ${diffDays} day(s) late. An automated fine of $${fine} ($2.00/day) will be registered.</div>`;
    } else {
        previewBox.innerHTML = `<div style="color:var(--success); font-weight:600;"><i class="fas fa-check-circle"></i> On-time return. No fines applicable.</div>`;
    }
}

async function handleReturnBook(e) {
    e.preventDefault();
    const form = e.target;
    const loanId = parseInt(form.loan_id.value);
    const returnDate = form.return_date.value;

    try {
        const res = await fetch('/api/loans/return', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ loan_id: loanId, return_date: returnDate })
        });
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        showToast(json.message || 'Book returned successfully!', 'success');
    } catch (err) {
        const loanIdx = MOCK_DATA.loans.findIndex(l => l.loan_id === loanId);
        if (loanIdx !== -1) {
            const loan = MOCK_DATA.loans[loanIdx];
            const book = MOCK_DATA.books.find(b => b.book_id === loan.book_id);
            if (book) book.available_copies += 1;
            MOCK_DATA.loans.splice(loanIdx, 1);
            showToast('Book returned successfully (Demo Mode)!', 'success');
        }
    }

    closeModal('returnBookModal');
    loadCirculationData();
    loadDashboardStats();
}

// -----------------------------------------------------------------------------
// 6. Fines Management
// -----------------------------------------------------------------------------
async function loadFines() {
    let fines = [];
    try {
        const res = await fetch('/api/fines');
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        fines = json.data;
    } catch (err) {
        fines = MOCK_DATA.fines;
    }

    const tbody = document.getElementById('finesTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!fines || fines.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:#888;">No fines recorded on file.</td></tr>`;
        return;
    }

    fines.forEach(fine => {
        const tr = document.createElement('tr');
        const statusBadge = fine.payment_status === 'Paid' ? 'badge-success' : 'badge-danger';
        const actionBtn = fine.payment_status === 'Unpaid' 
            ? `<button class="btn btn-primary btn-sm" onclick="openPayFineModal(${fine.fine_id}, ${fine.amount})"><i class="fas fa-credit-card"></i> Pay Fine</button>`
            : `<span style="font-size:0.8rem; color:var(--success);"><i class="fas fa-check"></i> Settled (${fine.payment_method})</span>`;

        tr.innerHTML = `
            <td><strong>#${fine.fine_id}</strong></td>
            <td><strong>${escapeHtml(fine.member_name)}</strong><br><small style="color:#666">${fine.member_email}</small></td>
            <td>${escapeHtml(fine.book_title)}</td>
            <td><strong style="color:var(--danger);">$${parseFloat(fine.amount).toFixed(2)}</strong></td>
            <td>${fine.fine_date}</td>
            <td><span class="badge ${statusBadge}">${fine.payment_status}</span></td>
            <td>${actionBtn}</td>
        `;
        tbody.appendChild(tr);
    });
}

function openPayFineModal(fineId, amount) {
    const form = document.getElementById('payFineForm');
    form.fine_id.value = fineId;
    document.getElementById('payFineAmountText').textContent = `$${parseFloat(amount).toFixed(2)}`;
    openModal('payFineModal');
}

async function handlePayFine(e) {
    e.preventDefault();
    const form = e.target;
    const fineId = parseInt(form.fine_id.value);
    const paymentMethod = form.payment_method.value;

    try {
        const res = await fetch('/api/fines/pay', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fine_id: fineId, payment_method: paymentMethod })
        });
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        showToast(json.message || 'Fine paid successfully!', 'success');
    } catch (err) {
        const fine = MOCK_DATA.fines.find(f => f.fine_id === fineId);
        if (fine) {
            fine.payment_status = 'Paid';
            fine.payment_method = paymentMethod;
        }
        showToast(`Fine settled via ${paymentMethod} (Demo Mode)!`, 'success');
    }

    closeModal('payFineModal');
    loadFines();
    loadDashboardStats();
}

// -----------------------------------------------------------------------------
// 7. DBMS Architecture & View Inspector
// -----------------------------------------------------------------------------
async function inspectDbmsView(viewName) {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        if (btn.getAttribute('data-view-name') === viewName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    let viewData = [];
    try {
        const res = await fetch(`/api/dbms/views/${viewName}`);
        if (!res.ok) throw new Error('API offline');
        const json = await res.json();
        if (!json.success) throw new Error(json.error);
        viewData = json.data;
    } catch (err) {
        // Provide mock view data
        if (viewName === 'v_book_catalog') {
            viewData = MOCK_DATA.books.map(b => ({
                book_id: b.book_id,
                isbn: b.isbn,
                title: b.title,
                category_name: b.category_name,
                authors: b.authors,
                available_copies: b.available_copies,
                total_copies: b.total_copies,
                stock_status: b.available_copies > 0 ? 'Available' : 'Out of Stock'
            }));
        } else if (viewName === 'v_active_loans') {
            viewData = MOCK_DATA.loans;
        } else if (viewName === 'v_overdue_loans') {
            viewData = MOCK_DATA.loans.filter(l => l.status === 'Overdue').map(l => ({
                loan_id: l.loan_id,
                book_title: l.book_title,
                member_name: l.member_name,
                days_late: l.days_overdue,
                estimated_fine: (l.days_overdue * 2.0).toFixed(2)
            }));
        } else {
            viewData = [
                { title: "Database System Concepts", total_times_borrowed: 14, category: "Computer Science" },
                { title: "Clean Code", total_times_borrowed: 11, category: "Computer Science" },
                { title: "1984", total_times_borrowed: 9, category: "Literature" }
            ];
        }
    }

    const container = document.getElementById('dbmsViewResultContainer');
    if (!container) return;

    if (viewData.length === 0) {
        container.innerHTML = `<div style="padding:1rem; color:#888;">View returned 0 rows.</div>`;
        return;
    }

    const columns = Object.keys(viewData[0]);
    let html = `<div class="table-responsive"><table class="data-table"><thead><tr>`;
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += `</tr></thead><tbody>`;

    viewData.forEach(row => {
        html += `<tr>`;
        columns.forEach(col => {
            const val = row[col] !== null && row[col] !== undefined ? row[col] : '<em>NULL</em>';
            html += `<td>${escapeHtml(String(val))}</td>`;
        });
        html += `</tr>`;
    });

    html += `</tbody></table></div>`;
    container.innerHTML = html;
}

// -----------------------------------------------------------------------------
// 8. Event Listeners & Modals Helper
// -----------------------------------------------------------------------------
function initEventListeners() {
    document.getElementById('bookSearchInput')?.addEventListener('input', debounce(loadBooks, 300));
    document.getElementById('bookCategoryFilter')?.addEventListener('change', loadBooks);
    document.getElementById('bookAvailabilityFilter')?.addEventListener('change', loadBooks);
    document.getElementById('addBookForm')?.addEventListener('submit', handleAddBook);
    document.getElementById('editBookForm')?.addEventListener('submit', handleUpdateBook);

    document.getElementById('memberSearchInput')?.addEventListener('input', debounce(loadMembers, 300));
    document.getElementById('addMemberForm')?.addEventListener('submit', handleAddMember);

    document.getElementById('issueBookForm')?.addEventListener('submit', handleIssueBook);
    document.getElementById('returnBookForm')?.addEventListener('submit', handleReturnBook);
    document.getElementById('returnDateInput')?.addEventListener('change', calculateReturnEstimate);

    document.getElementById('payFineForm')?.addEventListener('submit', handlePayFine);
}

async function loadCategoriesDropdowns() {
    let categories = [];
    try {
        const res = await fetch('/api/categories');
        if (!res.ok) throw new Error();
        const json = await res.json();
        categories = json.data;
    } catch (err) {
        categories = MOCK_DATA.categories;
    }
    categoriesCache = categories;

    const filterSelect = document.getElementById('bookCategoryFilter');
    const addSelect = document.getElementById('addBookCategorySelect');
    const editSelect = document.getElementById('editBookCategorySelect');

    if (filterSelect) {
        filterSelect.innerHTML = '<option value="">All Categories</option>';
        categories.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.category_id;
            opt.textContent = c.name;
            filterSelect.appendChild(opt);
        });
    }

    [addSelect, editSelect].forEach(select => {
        if (select) {
            select.innerHTML = '<option value="">-- Select Category --</option>';
            categories.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.category_id;
                opt.textContent = c.name;
                select.appendChild(opt);
            });
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
}

// Utility: Toast Notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? 'fa-check-circle' : (type === 'error' ? 'fa-times-circle' : 'fa-info-circle');
    toast.innerHTML = `<i class="fas ${icon}"></i> <span>${escapeHtml(message)}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Utility: Debounce
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Utility: HTML Escaper
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
