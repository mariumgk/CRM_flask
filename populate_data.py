import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="CRM",
    user="postgres",
    password="admin",
    host="localhost"
)
cur = conn.cursor()

# RESET all data first
cur.execute("""
TRUNCATE Quote_Items, Quotes, Opportunities, Contacts, Accounts, Users, Products, Leads, Tasks, Tickets, Notes, Audit_Log 
RESTART IDENTITY CASCADE;
""")

# Insert Users
user_ids = []
for _ in range(5):
    name = fake.name()
    email = fake.email()
    role = random.choice(['Sales Rep', 'Manager', 'Support Agent'])
    password_hash = fake.sha256()
    cur.execute("INSERT INTO Users (name, email, role, password_hash) VALUES (%s, %s, %s, %s)",
                (name, email, role, password_hash))
    cur.execute("SELECT LASTVAL()")
    user_ids.append(cur.fetchone()[0])

# Insert Accounts
account_ids = []
for _ in range(5):
    name = fake.company()
    industry = fake.job()
    website = fake.url()
    address = fake.address()
    owner_id = random.choice(user_ids)
    cur.execute("INSERT INTO Accounts (name, industry, website, address, owner_id) VALUES (%s, %s, %s, %s, %s)",
                (name, industry, website, address, owner_id))
    cur.execute("SELECT LASTVAL()")
    account_ids.append(cur.fetchone()[0])

# Insert Contacts
contact_ids = []
for _ in range(10):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    phone = fake.phone_number()
    account_id = random.choice(account_ids)
    created_by = random.choice(user_ids)
    cur.execute("""INSERT INTO Contacts (first_name, last_name, email, phone, account_id, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (first_name, last_name, email, phone, account_id, created_by))
    cur.execute("SELECT LASTVAL()")
    contact_ids.append(cur.fetchone()[0])

# Insert Opportunities
opportunity_ids = []
for _ in range(5):
    name = fake.bs().title()
    account_id = random.choice(account_ids)
    contact_id = random.choice(contact_ids)
    stage = random.choice(['Prospecting', 'Proposal Sent', 'Negotiation', 'Closed Won', 'Closed Lost'])
    revenue = round(random.uniform(5000, 50000), 2)
    close_date = fake.future_date()
    owner_id = random.choice(user_ids)
    cur.execute("""INSERT INTO Opportunities (name, account_id, contact_id, stage, expected_revenue, close_date, owner_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (name, account_id, contact_id, stage, revenue, close_date, owner_id))
    cur.execute("SELECT LASTVAL()")
    opportunity_ids.append(cur.fetchone()[0])

# Insert Products
product_ids = []
for _ in range(8):
    name = fake.catch_phrase()
    description = fake.text()
    price = round(random.uniform(100, 10000), 2)
    cur.execute("INSERT INTO Products (name, description, price) VALUES (%s, %s, %s)",
                (name, description, price))
    cur.execute("SELECT LASTVAL()")
    product_ids.append(cur.fetchone()[0])

# Insert Quotes
quote_ids = []
for opp_id in opportunity_ids:
    total = round(random.uniform(1000, 10000), 2)
    status = random.choice(['Draft', 'Sent', 'Accepted', 'Rejected'])
    cur.execute("INSERT INTO Quotes (opportunity_id, total, status) VALUES (%s, %s, %s)",
                (opp_id, total, status))
    cur.execute("SELECT LASTVAL()")
    quote_ids.append(cur.fetchone()[0])

# Insert Quote_Items (with product uniqueness per quote)
for quote_id in quote_ids:
    used_products = set()
    for _ in range(random.randint(1, 3)):
        available_products = list(set(product_ids) - used_products)
        if not available_products:
            break
        product_id = random.choice(available_products)
        used_products.add(product_id)
        quantity = random.randint(1, 5)
        unit_price = round(random.uniform(100, 1000), 2)
        cur.execute("""INSERT INTO Quote_Items (quote_id, product_id, quantity, unit_price)
                       VALUES (%s, %s, %s, %s)""",
                    (quote_id, product_id, quantity, unit_price))

# Insert Leads (bonus)
for _ in range(5):
    name = fake.name()
    email = fake.email()
    phone = fake.phone_number()
    company = fake.company()
    source = random.choice(['Web', 'Referral', 'Email', 'Phone'])
    status = random.choice(['New', 'Contacted', 'Converted'])
    assigned_to = random.choice(user_ids)
    cur.execute("""INSERT INTO Leads (name, email, phone, company, source, status, assigned_to)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (name, email, phone, company, source, status, assigned_to))

# Commit and close
conn.commit()
cur.close()
conn.close()

print("✅ CRM sample data inserted successfully into all tables.")
