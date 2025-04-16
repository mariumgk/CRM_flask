from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        dbname="CRM",
        user="postgres",
        password="admin",
        host="localhost"
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    # Count summary stats
    cur.execute("SELECT COUNT(*) FROM Users")
    user_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM Accounts")
    account_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM Quotes")
    quote_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM Tickets")
    ticket_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM Leads")
    lead_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM Tasks")
    task_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template('index.html', 
        user_count=user_count, 
        account_count=account_count,
        quote_count=quote_count,
        ticket_count=ticket_count,
        lead_count=lead_count,
        task_count=task_count
    )
@app.route('/contacts/summary.json')
def contacts_summary_json():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.name, COUNT(c.contact_id)
        FROM Accounts a
        LEFT JOIN Contacts c ON a.account_id = c.account_id
        GROUP BY a.name
        ORDER BY COUNT(c.contact_id) DESC;
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return {"labels": labels, "values": values}


@app.route('/users')
def users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, email, role FROM Users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('users.html', users=users)
from flask import request, redirect, flash, url_for

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        password_hash = request.form['password']  # You can hash it if needed

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO Users (name, email, role, password_hash) VALUES (%s, %s, %s, %s)",
                    (name, email, role, password_hash))
        conn.commit()
        cur.close()
        conn.close()

        flash("User added successfully!", "success")
        return redirect(url_for('users'))

    return render_template('add_user.html')

@app.route('/accounts')
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


@app.route('/products')
def products():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT product_id, name, description, price FROM Products")
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/opportunities')
def opportunities():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT opportunity_id, name, stage, expected_revenue, close_date FROM Opportunities")
    opportunities = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('opportunities.html', opportunities=opportunities)

@app.route('/quotes')
def quotes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT quote_id, opportunity_id, total, status FROM Quotes")
    quotes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('quotes.html', quotes=quotes)

@app.route('/tasks')
def tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT task_id, title, due_date, status FROM Tasks")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('tasks.html', tasks=tasks)

@app.route('/tickets')
def tickets():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT ticket_id, subject, description, status FROM Tickets")
    tickets = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('tickets.html', tickets=tickets)

if __name__ == '__main__':
    app.run(debug=True)
