# Basic Auth — Design Notes / Pseudocode

Guidance for implementing the "Basic auth" item from FEATURES.md: require a
username + password before any commands work, hash passwords with `bcrypt`
(never store plaintext), and store users in a new `users` table.

This is intentionally pseudocode, not working code — fill in the real
implementation yourself.

## 1. New table

Add a `users` table in `init_db()`, alongside the existing `tasks` table:

```
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
)
```

`UNIQUE` on `username` means SQLite will reject a duplicate registration for
you — catch that instead of checking for it yourself first.

## 2. Registering a user

```
function create_user(username, password):
    if username is blank or password is blank:
        return False

    hash = bcrypt.hashpw(password, bcrypt.gensalt())

    try:
        INSERT INTO users (username, password_hash) VALUES (username, hash)
        return True
    except "duplicate username" error:
        return False
```

Things to watch for:
- `bcrypt.hashpw` needs `bytes`, not `str` — encode the password first
  (`password.encode("utf-8")`), and decode the hash back to `str` before
  storing it as TEXT.
- Never log or print the raw password.

## 3. Logging in

```
function authenticate_user(username, password):
    row = SELECT password_hash FROM users WHERE username = username

    if row does not exist:
        return False

    return bcrypt.checkpw(password, row.password_hash)
```

`bcrypt.checkpw` does the comparison safely (constant-time) — don't hash the
input password yourself and compare strings.

## 4. Helper checks

You'll want a couple of small helpers to drive the login/register flow:

```
function user_exists(username):
    return True if a row in users matches username, else False

function has_any_users():
    return True if the users table has at least one row, else False
```

`has_any_users()` is what decides whether to show a "register" prompt
(nobody's signed up yet) or a "login" prompt.

## 5. The login gate

Runs once, before the main command loop starts:

```
function login_prompt():
    loop forever:
        if has_any_users():
            ask "login or register?"
        else:
            action = "register"   # skip the question for the very first user

        if action == "register":
            ask for username, password
            if create_user(...) succeeds:
                return username
            else:
                print "username taken or blank, try again"

        elif action == "login":
            ask for username, password
            if authenticate_user(...) succeeds:
                return username
            else:
                print "wrong username or password, try again"
```

## 6. Wiring it into `main()`

Call it right after `init_db()`, before the command loop:

```
function main():
    init_db()
    login_prompt()          # <-- blocks here until someone logs in
    print "=== TaskFlow CLI ==="
    ... existing command loop unchanged ...
```

## Things to test

- Registering a brand-new user succeeds.
- Registering a duplicate username fails.
- Registering with a blank username or password fails.
- Logging in with the right password succeeds.
- Logging in with the wrong password fails.
- Logging in with a username that doesn't exist fails.
- The password hash stored in the DB never contains the plaintext password.
- `has_any_users()` / `user_exists()` reflect the current state correctly.

Look at how the existing tests in `test_app.py` are structured (clean DB per
test via the `clean_database` fixture) — auth tests should follow the same
pattern.
