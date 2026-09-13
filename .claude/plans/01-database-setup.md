# Plan: 01 — Database Setup

## Context

Spendly needs a working SQLite data layer before any other feature can be built. The stub in `database/db.py` must be replaced with three functions that create the schema, open connections correctly, and seed sample data. `app.py` must call these on startup.

Spec: `.claude/specs/01-database-setup.md`
Source root: `expense-tracker/expense-tracker/`

---

## Files to Modify

| File | Change |
|---|---|
| `expense-tracker/database/db.py` | Implement `get_db()`, `init_db()`, `seed_db()` |
| `expense-tracker/app.py` | Add DB imports + startup calls |

---

## Schema

### users
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | UNIQUE NOT NULL |
| password_hash | TEXT | NOT NULL |
| created_at | TEXT | DEFAULT datetime('now') |

### expenses
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| user_id | INTEGER | FK → users.id, NOT NULL |
| amount | REAL | NOT NULL |
| category | TEXT | NOT NULL |
| date | TEXT | NOT NULL (YYYY-MM-DD) |
| description | TEXT | Nullable |
| created_at | TEXT | DEFAULT datetime('now') |

---

## `database/db.py`

```python
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
```

**Key decisions:**
- `_DB_PATH` uses `__file__` → `spendly.db` lands at `expense-tracker/spendly.db` regardless of working directory
- `seed_db()` guards with `COUNT(*) > 0` — idempotent on repeated runs
- All 7 categories covered across 8 expenses (Food used twice)
- All SQL uses `?` parameterized placeholders — no string formatting

---

## `app.py` — Changes

Add after existing `from flask import Flask, render_template`:

```python
from database.db import get_db, init_db, seed_db
```

Add immediately after `app = Flask(__name__)`:

```python
with app.app_context():
    init_db()
    seed_db()
```

No existing routes are changed.

---

## Verification

```bash
# Start the app
cd expense-tracker
python app.py   # must start on port 5001 without errors

# Check DB contents
python -c "
from database.db import get_db, init_db, seed_db
init_db(); seed_db()
db = get_db()
print('users:', db.execute('SELECT COUNT(*) FROM users').fetchone()[0])
print('expenses:', db.execute('SELECT COUNT(*) FROM expenses').fetchone()[0])
db.close()
"
# Expected: users: 1, expenses: 8

# Check idempotency
python -c "
from database.db import seed_db, get_db
seed_db(); seed_db()
db = get_db()
print('users after 2x seed:', db.execute('SELECT COUNT(*) FROM users').fetchone()[0])
db.close()
"
# Expected: 1

# Check FK enforcement
python -c "
from database.db import get_db
db = get_db()
try:
    db.execute('INSERT INTO expenses (user_id, amount, category, date) VALUES (999, 1.0, \"Food\", \"2026-01-01\")')
    db.commit(); print('ERROR: FK not enforced')
except Exception as e:
    print('FK enforced OK:', type(e).__name__)
db.close()
"
```

---

## Definition of Done

- [ ] Database file created on app startup
- [ ] Both tables exist with correct schema and constraints
- [ ] Demo user exists with hashed password
- [ ] 8 sample expenses across all 7 categories
- [ ] No duplicate seed data on repeated runs
- [ ] App starts without errors on port 5001
- [ ] Foreign key enforcement works
- [ ] All queries use parameterized SQL
