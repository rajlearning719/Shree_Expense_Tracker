# Spec: Registration

## Overview
Implement user registration so new visitors can create a Spendly account.
The `POST /register` route receives a name, email, and password, validates
the input, hashes the password, and inserts a new row into the `users` table.
On success the user is redirected to the login page; on failure the
registration form is re-rendered with a clear error message. This is the
first step that writes user data and unlocks all authenticated features that
follow.

## Depends on
- Step 1 — Database Setup (`get_db()`, `init_db()`, `seed_db()`, `users` table)

## Routes
- `GET /register` — render the registration form — public (already exists, no change needed)
- `POST /register` — process the submitted form, insert user, redirect — public

## Database changes
No new tables or columns. Uses the existing `users` table:
- `name` TEXT NOT NULL
- `email` TEXT UNIQUE NOT NULL
- `password_hash` TEXT NOT NULL
- `created_at` TEXT DEFAULT (datetime('now'))

## Templates
- **Modify:** `templates/register.html`
  - Form `action="/register"` and `method="POST"` are already in place
  - Add `{{ error }}` display block (already present as `{% if error %}`) — no change needed
  - Ensure `name` input field is present (already present)

## Files to change
- `app.py` — convert `GET /register` stub into a dual-method route (`GET, POST`), add registration logic
- `database/db.py` — add `create_user(name, email, password)` helper function

## Files to create
None.

## New dependencies
No new dependencies. Uses `werkzeug.security.generate_password_hash` (already installed).

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only
- Parameterised queries only — never use f-strings or `%` formatting in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash` — never store plaintext
- Use CSS variables — never hardcode hex values in templates
- All templates extend `base.html`
- DB logic lives in `database/db.py` only — route function must not contain raw SQL
- Use `abort()` for unexpected server errors, not bare string returns
- Validate all three fields (name, email, password) server-side before touching the DB
- Minimum password length: 8 characters
- On duplicate email, catch the `sqlite3.IntegrityError` and re-render the form with an error message — do not crash
- On success, redirect to `/login` using `redirect(url_for('login'))`
- Import `redirect`, `request` from flask in `app.py`

## Definition of done
- [ ] `GET /register` still renders `register.html` with no errors
- [ ] Submitting the form with valid data inserts a new row in `users` with a hashed password
- [ ] Submitting with a duplicate email re-renders the form with the error "An account with that email already exists."
- [ ] Submitting with an empty name, email, or password re-renders the form with the error "All fields are required."
- [ ] Submitting with a password shorter than 8 characters re-renders the form with the error "Password must be at least 8 characters."
- [ ] Successful registration redirects to `/login`
- [ ] Password is never stored in plaintext — `password_hash` column always contains a werkzeug hash
- [ ] Running `init_db()` + `seed_db()` after registration does not affect the new user's record
