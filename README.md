
# 🧠 CRM System (Flask + PostgreSQL)

A role-based Customer Relationship Management (CRM) system built with Flask, PostgreSQL, Bootstrap, and Chart.js. This app supports user authentication, accounts, leads, contacts, tasks, products, quotes, opportunities, and dashboard insights.

---

## 🚀 Features

- 🔐 Role-based login (Admin, Manager, Staff)
- 👥 Full CRUD for Users, Leads, Accounts, Contacts, etc.
- 📊 Dashboard with real-time KPIs and charts
- 🧾 Dynamic quote generation with line items
- 📅 Task tracking and upcoming deadlines
- 🛠 Ticket system for customer support

---

## 🛠 Technologies Used

- **Backend**: Flask, Python, psycopg2
- **Database**: PostgreSQL
- **Frontend**: HTML, Bootstrap, Chart.js
- **Security**: Session handling, hashed passwords, role-based decorators
- **Deployment-Ready**: Uses `.env` for secure config management

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone 
cd crm-system
````

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:
```
DB_NAME=CRM
DB_USER=your_postgres_user
DB_PASSWORD=your_password
DB_HOST=localhost
SECRET_KEY=your_secret_key
```
### 4. Initialize the Database

Create a PostgreSQL database manually or using:

```sql
CREATE DATABASE CRM;
```

Run your schema setup if applicable (`schema.sql` or migrations).

### 5. Run the App

```bash
python app.py
```
---

## 📂 Project Structure

```
.
├── app.py
├── templates/
├── static/
├── .env
├── .gitignore
└── README.md

## 👩‍💻 Author

Built by [MariumImran](https://github.com/yourusername)
Contact: marium.imranrauf@gmail.com

