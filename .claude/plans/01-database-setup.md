# Plan: 01 — Database Setup

## Context

Spendly currently has no data layer. `database/db.py` is a stub (comments only) and `app.py` has no database imports or startup calls. This step implements the SQLite foundation that all future features (auth, profile, expenses) will depend on.

Source spec: `.claude/01-database-setup.md`

**Actual source root** (nested layout): `expense-tracker/expense-tracker/`

---

## Files Modified

| File | Change |
|---|---|
| `expense-tracker/database/db.py` | Full implementation — 3 functions |
| `expense-tracker/app.py` | Added imports + startup calls |

---

## Implementation Summary

### `database/db.py`

- `_DB_PATH` computed from `__file__` → places `spendly.db` at `expense-tracker/spendly.db`
- `get_db()` — opens connection, sets `row_factory = sqlite3.Row`, enables `PRAGMA foreign_keys = ON`
- `init_db()` — creates `users` and `expenses` tables with `CREATE TABLE IF NOT EXISTS`
- `seed_db()` — guards with `COUNT(*) > 0`, inserts 1 demo user + 8 expenses across all 7 categories using parameterized queries

### `app.py`

- Added `from database.db import get_db, init_db, seed_db`
- Added `with app.app_context(): init_db(); seed_db()` after `app = Flask(__name__)`

---

## Verification

```bash
# Start the app
cd expense-tracker
python app.py

# Confirm DB contents
python -c "
from database.db import get_db
db = get_db()
print('users:', db.execute('SELECT COUNT(*) FROM users').fetchone()[0])
print('expenses:', db.execute('SELECT COUNT(*) FROM expenses').fetchone()[0])
db.close()
"
# Expected: users: 1, expenses: 8
```
