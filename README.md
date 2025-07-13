# Progress Backend API

This is a standalone backend API application built with **Flask**, using **MySQL** as its database.  
It is dedicated to managing task progress data for internal systems.

---

## 🚀 Features

- Flask RESTful API
- SQLAlchemy ORM + Flask-Migrate
- MySQL support (migrated from SQLite)
- Scheduled tasks using APScheduler (optional)
- `.env` based configuration
- Modular project structure (blueprints)
- Export tasks as Excel or YAML

---

## 🧱 Tech Stack

- Python 3.10+
- Flask 3.x
- MySQL 8.x
- SQLAlchemy 2.x
- Flask-Migrate
- Gunicorn (for production)
- APScheduler (optional)
- Redis + Celery (optional)
- Pandas, OpenPyXL & PyYAML (export features)

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourname/progress-backend.git
cd progress-backend
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://user:password@localhost/progress_db
SECRET_KEY=your-secret-key
```

Or copy the template:

```bash
cp .env.example .env
```

---

## 🛠 Running the App

### Development Server

```bash
flask run
```

### With Gunicorn (Production)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

---

## 🔧 Database Migration

```bash
flask db init        # First time only
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 📚 API Documentation

Coming soon.

---

## 📂 Project Structure

```
progress-backend/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── schemas/
│   └── ...
├── migrations/
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```

---

## 🔐 Security Notes

- Never commit `.env` files to public repositories.
- Rotate your secret keys in production regularly.

---



