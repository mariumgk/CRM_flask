from flask import Flask, render_template, request, redirect, flash, url_for, session
from decimal import Decimal
from functools import wraps
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapper
import hashlib
import psycopg2

app = Flask(__name__)
app.secret_key = 'crm_project'

def get_db_connection():
    return psycopg2.connect(
        dbname="CRM",
        user="postgres",
        password="admin",
        host="localhost"
    )
@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    # Basic Counts
    cur.execute("SELECT COUNT(*) FROM Users")
    user_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM Accounts")
    account_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM Contacts")
    contact_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM Leads")
    lead_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM Opportunities")
    opportunity_count = cur.fetchone()[0]

    cur.execute("SELECT SUM(expected_revenue) FROM Opportunities")
    revenue_forecast = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM Tickets WHERE status = 'Open'")
    open_ticket_count = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM Tasks
        WHERE due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
    """)
    tasks_due_week = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template('index.html', 
        user_count=user_count,
        account_count=account_count,
        contact_count=contact_count,
        lead_count=lead_count,
        opportunity_count=opportunity_count,
        revenue_forecast=revenue_forecast,
        open_ticket_count=open_ticket_count,
        tasks_due_week=tasks_due_week
    )
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/users')
@login_required
def users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, email, role FROM Users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, name FROM Users WHERE email = %s AND password_hash = %s", (email, password_hash))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password!", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO Users (name, email, role, password_hash) VALUES (%s, %s, %s, %s)",
                (name, email, role, password_hash)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash("User added successfully!", "success")
            return redirect(url_for('users'))

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("A user with this email already exists!", "danger")
            return redirect(url_for('add_user'))

    return render_template('add_user.html')

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']

        cur.execute("""
            UPDATE Users
            SET name = %s, email = %s, role = %s
            WHERE user_id = %s
        """, (name, email, role, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('users'))

    cur.execute("SELECT * FROM Users WHERE user_id = %s", (id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit_user.html', user=user)


@app.route('/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Users WHERE user_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('users'))


@app.route('/accounts')
@login_required
def accounts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT account_id, name, industry, website FROM Accounts")
    accounts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('accounts.html', accounts=accounts)
@app.route('/accounts/add', methods=['GET', 'POST'])
def add_account():
    if request.method == 'POST':
        name = request.form['name']
        industry = request.form['industry']
        website = request.form['website']
        address = request.form['address']
        owner_id = request.form['owner_id']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO Accounts (name, industry, website, address, owner_id) VALUES (%s, %s, %s, %s, %s)",
                    (name, industry, website, address, owner_id))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('accounts'))

    return render_template('add_account.html')
@app.route('/accounts/edit/<int:id>', methods=['GET', 'POST'])
def edit_account(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        industry = request.form['industry']
        website = request.form['website']
        address = request.form['address']
        owner_id = request.form['owner_id']

        cur.execute("""
            UPDATE Accounts
            SET name = %s, industry = %s, website = %s, address = %s, owner_id = %s
            WHERE account_id = %s
        """, (name, industry, website, address, owner_id, id))

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('accounts'))

    cur.execute("SELECT * FROM Accounts WHERE account_id = %s", (id,))
    account = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit_account.html', account=account)
@app.route('/accounts/delete/<int:id>', methods=['POST'])
def delete_account(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Accounts WHERE account_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('accounts'))

@app.route('/contacts')
@login_required
def contacts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT contact_id, first_name, last_name, email, phone FROM Contacts")
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('contacts.html', contacts=contacts)

@app.route('/contacts/add', methods=['GET', 'POST'])
def add_contact():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        account_id = request.form['account_id']
        created_by = request.form['created_by']

        cur.execute("""
            INSERT INTO Contacts (first_name, last_name, email, phone, account_id, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, email, phone, account_id, created_by))

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('contacts'))

    # Pre-fill dropdowns from Accounts and Users
    cur.execute("SELECT account_id, name FROM Accounts")
    accounts = cur.fetchall()
    cur.execute("SELECT user_id, name FROM Users")
    users = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('add_contact.html', accounts=accounts, users=users)

@app.route('/contacts/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        account_id = request.form['account_id']
        created_by = request.form['created_by']

        cur.execute("""UPDATE Contacts
                       SET first_name = %s, last_name = %s, email = %s, phone = %s, account_id = %s, created_by = %s
                       WHERE contact_id = %s""",
                    (first_name, last_name, email, phone, account_id, created_by, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('contacts'))

    cur.execute("SELECT * FROM Contacts WHERE contact_id = %s", (id,))
    contact = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit_contact.html', contact=contact)

@app.route('/contacts/delete/<int:id>', methods=['POST'])
def delete_contact(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Contacts WHERE contact_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('contacts'))
@app.route('/leads')
@login_required
def leads():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT l.lead_id, l.name, l.email, l.company, l.status, u.name
        FROM Leads l
        LEFT JOIN Users u ON l.assigned_to = u.user_id
    """)
    leads = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('leads.html', leads=leads)

@app.route('/leads/add', methods=['GET', 'POST'])
@login_required
def add_lead():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        company = request.form['company']
        status = request.form['status']
        assigned_to = request.form['assigned_to']
        cur.execute("INSERT INTO Leads (name, email, company, status, assigned_to) VALUES (%s, %s, %s, %s, %s)",
                    (name, email, company, status, assigned_to))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('leads'))

    cur.execute("SELECT user_id, name FROM Users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('add_lead.html', users=users)

@app.route('/leads/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_lead(id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        company = request.form['company']
        status = request.form['status']
        assigned_to = request.form['assigned_to']
        cur.execute("""UPDATE Leads
                       SET name = %s, email = %s, company = %s, status = %s, assigned_to = %s
                       WHERE lead_id = %s""",
                    (name, email, company, status, assigned_to, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('leads'))

    cur.execute("SELECT * FROM Leads WHERE lead_id = %s", (id,))
    lead = cur.fetchone()
    cur.execute("SELECT user_id, name FROM Users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('edit_lead.html', lead=lead, users=users)

@app.route('/leads/delete/<int:id>', methods=['POST'])
@login_required
def delete_lead(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Leads WHERE lead_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('leads'))

@app.route('/leads/convert/<int:id>', methods=['POST'])
@login_required
def convert_lead(id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Get lead info
    cur.execute("SELECT name, email, company, assigned_to FROM Leads WHERE lead_id = %s", (id,))
    lead = cur.fetchone()
    if not lead:
        flash("Lead not found!", "danger")
        return redirect(url_for('leads'))

    # Insert as new Account
    name, email, company, owner_id = lead
    cur.execute("INSERT INTO Accounts (name, industry, address, website, owner_id) VALUES (%s, %s, %s, %s, %s)",
                (company, 'Unknown', '', '', owner_id))

    # Delete lead
    cur.execute("DELETE FROM Leads WHERE lead_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Lead converted to Account!", "success")
    return redirect(url_for('accounts'))


@app.route('/products')
@login_required
def products():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT product_id, name, description, price FROM Products")
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('products.html', products=products)
@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO Products (name, description, price) VALUES (%s, %s, %s)",
                    (name, description, price))
        conn.commit()
        cur.close()
        conn.close()
        flash("Product added!", "success")
        return redirect(url_for('products'))

    return render_template('add_product.html')

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        cur.execute("""
            UPDATE Products
            SET name = %s, description = %s, price = %s
            WHERE product_id = %s
        """, (name, description, price, id))

        conn.commit()
        cur.close()
        conn.close()
        flash("Product updated!", "info")
        return redirect(url_for('products'))

    cur.execute("SELECT * FROM Products WHERE product_id = %s", (id,))
    product = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Products WHERE product_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Product deleted!", "danger")
    return redirect(url_for('products'))

@app.route('/opportunities')
@login_required
def opportunities():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT opportunity_id, name, stage, expected_revenue, close_date FROM Opportunities")
    opportunities = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('opportunities.html', opportunities=opportunities)

# --- Create Opportunity ---
@app.route('/opportunities/add', methods=['GET', 'POST'])
@login_required
def add_opportunity():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        stage = request.form['stage']
        revenue = request.form['expected_revenue']
        close_date = request.form['close_date']
        account_id = request.form['account_id']
        owner_id = request.form['owner_id']

        cur.execute("""
            INSERT INTO Opportunities (name, stage, expected_revenue, close_date, account_id, owner_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, stage, revenue, close_date, account_id, owner_id))
        conn.commit()
        cur.close()
        conn.close()
        flash("Opportunity added!", "success")
        return redirect(url_for('opportunities'))

    cur.execute("SELECT account_id, name FROM Accounts")
    accounts = cur.fetchall()
    cur.execute("SELECT user_id, name FROM Users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('add_opportunity.html', accounts=accounts, users=users)

# --- Edit Opportunity ---
@app.route('/opportunities/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_opportunity(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        stage = request.form['stage']
        revenue = request.form['expected_revenue']
        close_date = request.form['close_date']
        account_id = request.form['account_id']
        owner_id = request.form['owner_id']

        cur.execute("""
            UPDATE Opportunities
            SET name = %s, stage = %s, expected_revenue = %s, close_date = %s, account_id = %s, owner_id = %s
            WHERE opportunity_id = %s
        """, (name, stage, revenue, close_date, account_id, owner_id, id))

        conn.commit()
        cur.close()
        conn.close()
        flash("Opportunity updated!", "info")
        return redirect(url_for('opportunities'))

    cur.execute("SELECT * FROM Opportunities WHERE opportunity_id = %s", (id,))
    opportunity = cur.fetchone()
    cur.execute("SELECT account_id, name FROM Accounts")
    accounts = cur.fetchall()
    cur.execute("SELECT user_id, name FROM Users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('edit_opportunity.html', opportunity=opportunity, accounts=accounts, users=users)

# --- Delete Opportunity ---
@app.route('/opportunities/delete/<int:id>', methods=['POST'])
@login_required
def delete_opportunity(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Opportunities WHERE opportunity_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Opportunity deleted!", "danger")
    return redirect(url_for('opportunities'))


@app.route('/quotes')
@login_required
def quotes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT q.quote_id, q.opportunity_id, q.total, q.status
        FROM Quotes q
        ORDER BY q.quote_id
    """)
    quotes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('quotes.html', quotes=quotes)


@app.route('/quotes/add', methods=['GET', 'POST'])
@login_required
def add_quote():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        opportunity_id = request.form['opportunity_id']
        status = request.form['status']
        product_ids = request.form.getlist('product_id')
        quantities = request.form.getlist('quantity')

        total = Decimal('0.0')
        for pid, qty in zip(product_ids, quantities):
            cur.execute("SELECT price FROM Products WHERE product_id = %s", (pid,))
            price = cur.fetchone()[0]
            total += price * int(qty)

        cur.execute("INSERT INTO Quotes (opportunity_id, total, status) VALUES (%s, %s, %s) RETURNING quote_id",
                    (opportunity_id, total, status))
        quote_id = cur.fetchone()[0]

        for pid, qty in zip(product_ids, quantities):
            cur.execute("INSERT INTO Quote_Items (quote_id, product_id, quantity) VALUES (%s, %s, %s)",
                        (quote_id, pid, qty))

        conn.commit()
        cur.close()
        conn.close()
        flash("Quote created successfully!", "success")
        return redirect(url_for('quotes'))

    cur.execute("SELECT opportunity_id, name FROM Opportunities")
    opportunities = cur.fetchall()
    cur.execute("SELECT product_id, name, price FROM Products")
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('add_quote.html', opportunities=opportunities, products=products)

# --- VIEW QUOTE ---
@app.route('/quotes/view/<int:id>')
@login_required
def view_quote(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT q.quote_id, o.name, q.total, q.status
        FROM Quotes q
        JOIN Opportunities o ON q.opportunity_id = o.opportunity_id
        WHERE q.quote_id = %s
    """, (id,))
    quote = cur.fetchone()

    cur.execute("""
        SELECT p.name, p.price, qi.quantity, (p.price * qi.quantity) as subtotal
        FROM Quote_Items qi
        JOIN Products p ON qi.product_id = p.product_id
        WHERE qi.quote_id = %s
    """, (id,))
    items = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('view_quote.html', quote=quote, items=items)

# --- EDIT QUOTE ---
@app.route('/quotes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_quote(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        status = request.form['status']
        product_ids = request.form.getlist('product_id')
        quantities = request.form.getlist('quantity')

        total = Decimal('0.0')
        for pid, qty in zip(product_ids, quantities):
            cur.execute("SELECT price FROM Products WHERE product_id = %s", (pid,))
            price = cur.fetchone()[0]
            total += price * int(qty)

        cur.execute("UPDATE Quotes SET total = %s, status = %s WHERE quote_id = %s",
                    (total, status, id))

        cur.execute("DELETE FROM Quote_Items WHERE quote_id = %s", (id,))
        for pid, qty in zip(product_ids, quantities):
            cur.execute("INSERT INTO Quote_Items (quote_id, product_id, quantity) VALUES (%s, %s, %s)",
                        (id, pid, qty))

        conn.commit()
        cur.close()
        conn.close()
        flash("Quote updated!", "info")
        return redirect(url_for('quotes'))

    cur.execute("SELECT status FROM Quotes WHERE quote_id = %s", (id,))
    quote_status = cur.fetchone()[0]
    cur.execute("SELECT product_id, quantity FROM Quote_Items WHERE quote_id = %s", (id,))
    selected_items = cur.fetchall()

    cur.execute("SELECT product_id, name, price FROM Products")
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('edit_quote.html', quote_id=id, status=quote_status, selected_items=selected_items, products=products)

# --- DELETE QUOTE ---
@app.route('/quotes/delete/<int:id>', methods=['POST'])
@login_required
def delete_quote(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Quote_Items WHERE quote_id = %s", (id,))
    cur.execute("DELETE FROM Quotes WHERE quote_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Quote deleted successfully.", "danger")
    return redirect(url_for('quotes'))

# --- View Tasks ---
@app.route('/tasks')
@login_required
def tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.task_id, t.title, t.due_date, t.status, u.name
        FROM Tasks t
        LEFT JOIN Users u ON t.assigned_to = u.user_id
        ORDER BY t.due_date
    """)
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('tasks.html', tasks=tasks)

# --- Add Task ---
@app.route('/tasks/add', methods=['GET', 'POST'])
@login_required
def add_task():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        due_date = request.form['due_date']
        status = request.form['status']
        assigned_to = request.form['assigned_to'] or None  # Can be null

        cur.execute("""
            INSERT INTO Tasks (title, due_date, status, assigned_to)
            VALUES (%s, %s, %s, %s)
        """, (title, due_date, status, assigned_to))

        conn.commit()
        cur.close()
        conn.close()
        flash("Task added successfully!", "success")
        return redirect(url_for('tasks'))

    cur.execute("SELECT user_id, name FROM Users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('add_task.html', users=users)

# --- Edit Task ---
@app.route('/tasks/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        due_date = request.form['due_date']
        status = request.form['status']
        assigned_to = request.form['assigned_to'] or None

        cur.execute("""
            UPDATE Tasks
            SET title = %s, due_date = %s, status = %s, assigned_to = %s
            WHERE task_id = %s
        """, (title, due_date, status, assigned_to, id))

        conn.commit()
        cur.close()
        conn.close()
        flash("Task updated successfully!", "info")
        return redirect(url_for('tasks'))

    cur.execute("SELECT * FROM Tasks WHERE task_id = %s", (id,))
    task = cur.fetchone()
    cur.execute("SELECT user_id, name FROM Users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('edit_task.html', task=task, users=users)

# --- Delete Task ---
@app.route('/tasks/delete/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Tasks WHERE task_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Task deleted successfully.", "danger")
    return redirect(url_for('tasks'))


# --- View Tickets ---
@app.route('/tickets')
@login_required
def tickets():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.ticket_id, c.first_name || ' ' || c.last_name AS contact_name, 
               t.subject, t.status
        FROM Tickets t
        JOIN Contacts c ON t.contact_id = c.contact_id
        ORDER BY t.ticket_id
    """)
    tickets = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('tickets.html', tickets=tickets)

# --- Add Ticket ---
@app.route('/tickets/add', methods=['GET', 'POST'])
@login_required
def add_ticket():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        contact_id = request.form['contact_id']
        subject = request.form['subject']
        description = request.form['description']
        status = request.form['status']

        cur.execute("""
            INSERT INTO Tickets (contact_id, subject, description, status)
            VALUES (%s, %s, %s, %s)
        """, (contact_id, subject, description, status))

        conn.commit()
        cur.close()
        conn.close()
        flash("Ticket added successfully!", "success")
        return redirect(url_for('tickets'))

    cur.execute("SELECT contact_id, first_name, last_name FROM Contacts")
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('add_ticket.html', contacts=contacts)

# --- Edit Ticket ---
@app.route('/tickets/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ticket(id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        contact_id = request.form['contact_id']
        subject = request.form['subject']
        description = request.form['description']
        status = request.form['status']

        cur.execute("""
            UPDATE Tickets
            SET contact_id = %s, subject = %s, description = %s, status = %s
            WHERE ticket_id = %s
        """, (contact_id, subject, description, status, id))

        conn.commit()
        cur.close()
        conn.close()
        flash("Ticket updated!", "info")
        return redirect(url_for('tickets'))

    cur.execute("SELECT * FROM Tickets WHERE ticket_id = %s", (id,))
    ticket = cur.fetchone()
    cur.execute("SELECT contact_id, first_name, last_name FROM Contacts")
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('edit_ticket.html', ticket=ticket, contacts=contacts)

# --- Delete Ticket ---
@app.route('/tickets/delete/<int:id>', methods=['POST'])
@login_required
def delete_ticket(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Tickets WHERE ticket_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Ticket deleted successfully.", "danger")
    return redirect(url_for('tickets'))

# --- Opportunities by Stage Chart Data ---
@app.route('/opportunities/summary.json')
@login_required
def opportunities_summary_json():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT stage, COUNT(*) 
        FROM Opportunities
        GROUP BY stage
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return {"labels": labels, "values": values}

# --- Leads by Status Chart Data ---
@app.route('/leads/summary.json')
@login_required
def leads_summary_json():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT status, COUNT(*)
        FROM Leads
        GROUP BY status
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return {"labels": labels, "values": values}

@app.route('/tickets/summary.json')
@login_required
def tickets_summary_json():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT status, COUNT(*)
        FROM Tickets
        GROUP BY status
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return {"labels": labels, "values": values}

@app.route('/tasks/summary.json')
@login_required
def tasks_summary_json():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT status, COUNT(*)
        FROM Tasks
        GROUP BY status
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return {"labels": labels, "values": values}

