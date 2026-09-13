# Spec: Login and Logout

## Overview
Implement session-based login and logout so registered users can authenticate
with Spendly. `POST /login` verifies the submitted email and password against
the database, starts a Flask session on success, and redirects to the profile
page (Step 4 stub). `GET /logout` clears the session and redirects to the
landing page. This step gates all future authenticated features — without a
working session, the profile, expense list, add, edit, and delete routes
cannot enforce access control.

## Depends on
- Step 1 — Database Setup (`get_db()`, `users` table with `email` and `password_hash`)
- Step 2 — Registration (users exist in the database to log in with)

## Routes
- `GET  /login`  — render login form — public (already exists, no change to GET)
- `POST /login`  — verify credentials, start session, redirect — public
- `GET  /logout` — clear session, redirect to landing — logged-in (currently a stub)

## Database changes
No database changes. Uses the existing `users` table:
- Lookup by `email` → fetch `id`, `name`, `password_hash`
- Verify password with `werkzeug.security.check_password_hash`

## Templates
- **Modify:** `templates/login.html`
  - `{% if error %}` block already present — no change needed
  - Form `method="POST" action="/login"` already correct — no change needed
  - No template changes required
- **Modify:** `templates/base.html`
  - Navbar currently always shows "Sign in" and "Get started"
  - When logged in (`session.user_id` exists), show "My profile" and "Sign out" links instead
  - Use `{% if session.get('user_id') %}` to branch the nav links

## Files to change
- `app.py` — add `secret_key`, expand `POST /login` logic, implement `GET /logout`
- `database/db.py` — add `get_user_by_email(email)` helper
- `templates/base.html` — update navbar to reflect logged-in state

## Files to create
None.

## New dependencies
No new pip packages. Uses:
- `flask.session` (built into Flask)
- `werkzeug.security.check_password_hash` (already installed)

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only
- Parameterised queries only — never use f-strings or `%` in SQL
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plaintext
- Use CSS variables — never hardcode hex values in templates
- All templates extend `base.html`
- DB logic in `database/db.py` only — route must not contain raw SQL
- `app.secret_key` must be set before any session usage — use a fixed dev key (e.g. `"spendly-dev-secret"`) in `app.py`; note in a comment that this must be changed for production
- Store only `user_id` and `user_name` in the session — never store `password_hash`
- On failed login (wrong email or wrong password), show the same generic error: `"Invalid email or password."` — do not reveal which field was wrong
- On successful login, redirect to `url_for('profile')`
- On logout, use `session.clear()` then redirect to `url_for('landing')`
- Import `session` from `flask` in `app.py`

## Definition of done
- [ ] `GET /login` renders the login form with no errors
- [ ] Submitting correct email + password starts a session and redirects to `/profile`
- [ ] Submitting wrong email shows "Invalid email or password." (form re-renders, no crash)
- [ ] Submitting correct email but wrong password shows "Invalid email or password."
- [ ] Submitting empty fields re-renders the form with "All fields are required."
- [ ] `GET /logout` clears the session and redirects to `/`
- [ ] After logout, visiting `/logout` again redirects cleanly (session already empty — no error)
- [ ] Navbar shows "Sign in" / "Get started" when logged out
- [ ] Navbar shows "My profile" / "Sign out" links when logged in
- [ ] `session['user_id']` is set to the correct integer id after login
- [ ] `session['user_name']` is set to the user's name after login
- [ ] Password hash is never stored in the session
