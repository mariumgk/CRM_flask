
# 🧠 CRM System – CS232 Semester Project (Spring 2025)

This is a beginner-level Customer Relationship Management (CRM) system developed using **Flask** (Python) and **PostgreSQL** (or SQLite for local testing), as part of the DBMS course sem project. The project is inspired by Salesforce and follows best practices in database design, user interaction, and query handling.

---

## 🚀 Features Implemented

- Full CRUD for:
  - Accounts
  - Contacts
  - Leads
  - Opportunities
  - Users
  - Tasks/Notes
- User Authentication (Register, Login, Logout)
- Sample Data inserted manually in database
- Dashboard with Summary & KPIs
- Responsive UI with Flask & Jinja templates

---

## 🛠 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/mariumgk/CRM_flask.git
cd CRM_flask
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv .venv

# Activate:
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Setup the Database
If using **SQLite**:
```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

If using **PostgreSQL**, update your `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'
```

### 5. Populate Sample Data (Optional)
```bash
python populate_data.py
```

### 6. Run the Application
```bash
# Windows PowerShell
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
flask run

# Mac/Linux
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Then open your browser and go to:
```
http://127.0.0.1:5000
```

---

## 📁 Project Structure
```
│
├── app.py                 # Main Flask app
├── populate_data.py       # Optional data seeder
├── requirements.txt
├── templates/             # HTML templates
├── static/                # Images, CSS, etc.
├── .venv/                 # Virtual environment
└── README.md
```
> Developed w <3
