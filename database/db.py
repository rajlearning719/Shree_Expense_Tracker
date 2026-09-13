import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'spendly.db')


def get_db():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    if conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] > 0:
        conn.close()
        return

    conn.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        ('Demo User', 'demo@spendly.com', generate_password_hash('demo123'))
    )
    user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

    today = date.today()
    expenses = [
        (user_id, 45.50,  'Food',          (today - timedelta(days=1)).isoformat(),  'Grocery shopping'),
        (user_id, 18.50,  'Food',          (today - timedelta(days=3)).isoformat(),  'Restaurant lunch'),
        (user_id, 25.00,  'Transport',     (today - timedelta(days=2)).isoformat(),  'Uber ride'),
        (user_id, 120.00, 'Bills',         (today - timedelta(days=5)).isoformat(),  'Electricity bill'),
        (user_id, 60.00,  'Health',        (today - timedelta(days=7)).isoformat(),  'Pharmacy'),
        (user_id, 35.00,  'Entertainment', (today - timedelta(days=10)).isoformat(), 'Movie tickets'),
        (user_id, 89.99,  'Shopping',      (today - timedelta(days=12)).isoformat(), 'Clothing'),
        (user_id, 15.00,  'Other',         (today - timedelta(days=14)).isoformat(), 'Miscellaneous'),
    ]
    conn.executemany(
        'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
        expenses
    )
    conn.commit()
    conn.close()
