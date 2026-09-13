# Plan: Step 1 — Database Setup

## Goal

Implement the data layer in `database/db.py` and wire it into `app.py` so that
the SQLite database is created and seeded on every app startup.

---

## Current State

- `database/db.py` — stub file with comments only; no functions implemented.
- `app.py` — imports only Flask; no DB wiring; placeholder routes in place.
- `spendly.db` — file exists on disk but contains no tables.

---

## Files to Change

| File | Change |
|---|---|
| `database/db.py` | Implement `get_db()`, `init_db()`, `seed_db()` |
| `app.py` | Import helpers, call `init_db()` + `seed_db()` in app context at startup |

---

## Implementation Steps

### Step 1 — Implement `get_db()` in `database/db.py`

- Use `sqlite3.connect()` pointing to `spendly.db` in the project root.
- Set `conn.row_factory = sqlite3.Row` for dict-like row access.
- Execute `PRAGMA foreign_keys = ON` immediately after opening.
- Return the connection.

```python
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "spendly.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
```

---

### Step 2 — Implement `init_db()` in `database/db.py`

- Call `get_db()` to open a connection.
- Create `users` table with `CREATE TABLE IF NOT EXISTS`.
- Create `expenses` table with `CREATE TABLE IF NOT EXISTS`, including FK to `users.id`.
- Commit and close.

**users schema:**

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | UNIQUE NOT NULL |
| password_hash | TEXT | NOT NULL |
| created_at | TEXT | DEFAULT datetime('now') |

**expenses schema:**

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| user_id | INTEGER | NOT NULL, FK → users.id |
| amount | REAL | NOT NULL |
| category | TEXT | NOT NULL |
| date | TEXT | NOT NULL (YYYY-MM-DD) |
| description | TEXT | nullable |
| created_at | TEXT | DEFAULT datetime('now') |

---

### Step 3 — Implement `seed_db()` in `database/db.py`

- Call `get_db()`.
- Check `SELECT COUNT(*) FROM users` — if > 0, return early (idempotent).
- Insert one demo user:
  - name: `Demo User`
  - email: `demo@spendly.com`
  - password hashed with `werkzeug.security.generate_password_hash("demo123")`
- Retrieve the inserted `user_id` via `lastrowid`.
- Insert 8 sample expenses covering all 7 categories (`Food`, `Transport`, `Bills`,
  `Health`, `Entertainment`, `Shopping`, `Other`) with dates in YYYY-MM-DD format
  spread across the current month.
- Commit and close.

**Allowed categories:** Food, Transport, Bills, Health, Entertainment, Shopping, Other

---

### Step 4 — Wire DB into `app.py`

- Add import at the top:
  ```python
  from database.db import get_db, init_db, seed_db
  ```
- After `app = Flask(__name__)`, add:
  ```python
  with app.app_context():
      init_db()
      seed_db()
  ```
- No routes change.

---

## Rules to Follow

- Parameterized queries only — never f-strings in SQL.
- `PRAGMA foreign_keys = ON` on every connection (inside `get_db()`).
- `amount` stored as REAL, not INTEGER.
- Passwords hashed with `werkzeug.security.generate_password_hash`.
- `seed_db()` must be idempotent — check before inserting.
- Dates in YYYY-MM-DD format.
- No new pip packages — only `sqlite3` (stdlib) and `werkzeug` (already installed).

---

## Definition of Done

- [ ] `spendly.db` is created on app startup with both tables present.
- [ ] `users` table has correct columns, types, and constraints (UNIQUE email, NOT NULL fields).
- [ ] `expenses` table has correct columns and FK constraint enforced.
- [ ] Demo user exists with a `werkzeug`-hashed password.
- [ ] 8 sample expenses exist, all linked to demo user, covering multiple categories.
- [ ] Running `init_db()` + `seed_db()` a second time produces no duplicates and no errors.
- [ ] App starts on port 5001 without errors.
- [ ] All queries use `?` placeholders — no string formatting in SQL.
