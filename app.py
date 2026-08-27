"""
TaskFlow CLI — a foundation task manager.

This started as a foundation; it now implements the full feature roadmap
from FEATURES.md: priority, editing, status/tag filters, due dates, tags,
CSV export, and basic (bcrypt-hashed) auth.
"""

import csv
import sqlite3
from datetime import datetime

import bcrypt

DB_NAME = "taskflow.db"


def get_connection():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    # Needed so that deleting a task also deletes its task_tags rows
    # (see the ON DELETE CASCADE foreign key on task_tags below).
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't already exist.

    Tables:
      tasks     - the core to-do items (title/status/priority/due_date)
      tags      - unique tag names (e.g. "work", "personal")
      task_tags - join table linking tasks <-> tags (many-to-many)
      users     - login accounts for the basic-auth feature
    """
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'todo',
            priority TEXT NOT NULL DEFAULT 'medium',
            due_date TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS task_tags (
            task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (task_id, tag_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


PRIORITIES = ("low", "medium", "high")


# ---------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------

def add_task(title, priority="medium", due_date=None):
    """Add a new task with the given title. Status starts as 'todo'.
    Priority must be one of 'low', 'medium', 'high' — defaults to 'medium'.
    due_date is an optional 'YYYY-MM-DD' string; leave it None/blank to
    skip it. Returns the new task's id.
    """
    if priority not in PRIORITIES:
        priority = "medium"
    if due_date is not None and due_date.strip() == "":
        due_date = None
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tasks (title, status, priority, due_date, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (title, "todo", priority, due_date, datetime.now().isoformat()),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def list_tasks(status=None, tag=None):
    """Return tasks, optionally filtered by status ('todo'/'done') and/or
    by tag name. Sorted with the soonest due date first; tasks with no due
    date sort to the end. Ties break by newest-first (highest id).
    """
    conn = get_connection()

    query = "SELECT DISTINCT tasks.* FROM tasks"
    conditions = []
    params = []

    if tag is not None:
        # Join through task_tags/tags only when filtering by tag, so tasks
        # without any tags are still included when no tag filter is given.
        query += (
            " JOIN task_tags ON task_tags.task_id = tasks.id"
            " JOIN tags ON tags.id = task_tags.tag_id"
        )
        conditions.append("tags.name = ?")
        params.append(tag)

    if status is not None:
        conditions.append("tasks.status = ?")
        params.append(status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # (due_date IS NULL) evaluates to 0 for tasks that have a due date and
    # 1 for tasks that don't, so real dates always sort before NULLs.
    query += " ORDER BY (tasks.due_date IS NULL), tasks.due_date ASC, tasks.id DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def edit_task(task_id, new_title):
    """Change an existing task's title by id. Returns True if a task was
    updated, False if no task with that id exists or the title is blank.
    """
    if not new_title or not new_title.strip():
        return False
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE tasks SET title = ? WHERE id = ?", (new_title.strip(), task_id)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def complete_task(task_id):
    """Mark a task as done, by id. Returns True if a task was updated."""
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE tasks SET status = 'done' WHERE id = ?", (task_id,)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_task(task_id):
    """Delete a task by id. Returns True if a task was deleted.
    Its task_tags rows are removed automatically via ON DELETE CASCADE.
    """
    conn = get_connection()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ---------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------

def parse_tags(raw):
    """Turn a raw comma-separated string like 'work, urgent' into a clean
    list of lowercase tag names, dropping empty entries."""
    if not raw:
        return []
    return [t.strip().lower() for t in raw.split(",") if t.strip()]


def _get_or_create_tag(conn, name):
    """Look up a tag by name, inserting it first if it doesn't exist yet.
    Returns the tag's id. Must be called with an open connection so the
    insert-then-select happens atomically within the caller's transaction.
    """
    row = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
    if row:
        return row["id"]
    cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (name,))
    return cursor.lastrowid


def set_tags_for_task(task_id, tag_names):
    """Replace a task's tags with the given list of tag names (creating
    any tags that don't already exist). Passing an empty list clears tags.
    """
    conn = get_connection()
    conn.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))
    for name in tag_names:
        tag_id = _get_or_create_tag(conn, name)
        conn.execute(
            "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
            (task_id, tag_id),
        )
    conn.commit()
    conn.close()


def get_tags_for_task(task_id):
    """Return the list of tag names attached to a task, alphabetically."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT tags.name FROM tags
        JOIN task_tags ON task_tags.tag_id = tags.id
        WHERE task_tags.task_id = ?
        ORDER BY tags.name ASC
        """,
        (task_id,),
    ).fetchall()
    conn.close()
    return [row["name"] for row in rows]


# ---------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------

def export_tasks_csv(filename="tasks.csv"):
    """Write every task to a CSV file, one row per task, including its
    tags (semicolon-joined, since CSV cells can't hold a list). Returns
    the number of tasks written.
    """
    tasks = list_tasks()
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["id", "title", "status", "priority", "due_date", "tags", "created_at"]
        )
        for task in tasks:
            tags = ";".join(get_tags_for_task(task["id"]))
            writer.writerow(
                [
                    task["id"],
                    task["title"],
                    task["status"],
                    task["priority"],
                    task["due_date"] or "",
                    tags,
                    task["created_at"],
                ]
            )
    return len(tasks)


# ---------------------------------------------------------------------
# Auth (basic username/password, bcrypt-hashed)
# ---------------------------------------------------------------------

def create_user(username, password):
    """Register a new user with a bcrypt-hashed password. Returns True on
    success, False if the username is already taken or inputs are blank.
    """
    if not username or not username.strip() or not password:
        return False
    username = username.strip()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash.decode("utf-8")),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Username already exists (UNIQUE constraint).
        return False
    finally:
        conn.close()


def authenticate_user(username, password):
    """Check a username/password pair against stored (hashed) credentials.
    Returns True if they match, False otherwise — never compares plaintext.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row is None:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8"))


def user_exists(username):
    """Return True if a user with this username is already registered."""
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row is not None


def has_any_users():
    """Return True if at least one user has been registered — used to
    decide whether to show a 'login' or 'register' prompt first."""
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
    conn.close()
    return row is not None


# ---------------------------------------------------------------------
# Presentation helpers
# ---------------------------------------------------------------------

def print_tasks(tasks=None):
    """Print tasks in a readable format, including due date and tags when
    present. Accepts a pre-filtered list, or fetches all tasks if omitted.
    """
    if tasks is None:
        tasks = list_tasks()
    if not tasks:
        print("No tasks yet. Add one!")
        return
    for task in tasks:
        marker = "[x]" if task["status"] == "done" else "[ ]"
        due = f"  due:{task['due_date']}" if task["due_date"] else ""
        tags = get_tags_for_task(task["id"])
        tag_str = f"  tags:{','.join(tags)}" if tags else ""
        print(f"{marker} #{task['id']}  ({task['priority']})  {task['title']}{due}{tag_str}")


def login_prompt():
    """Interactive login/register gate run once at CLI startup.
    Returns once a user has successfully authenticated (or registered).
    """
    print("=== TaskFlow Login ===")
    while True:
        if has_any_users():
            action = input("Login or register? [login/register]: ").strip().lower()
        else:
            print("No users yet — let's create one.")
            action = "register"

        if action == "register":
            username = input("Choose a username: ").strip()
            password = input("Choose a password: ").strip()
            if create_user(username, password):
                print(f"Account created. Welcome, {username}!")
                return username
            else:
                print("That username is taken (or inputs were blank). Try again.")
        elif action == "login":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            if authenticate_user(username, password):
                print(f"Welcome back, {username}!")
                return username
            else:
                print("Incorrect username or password.")
        else:
            print("Please type 'login' or 'register'.")


def main():
    """Menu-driven CLI loop, gated behind a login/register prompt."""
    init_db()
    login_prompt()

    print("\n=== TaskFlow CLI ===")
    print("Commands: add, list [todo|done|<tag>], edit, done, delete, export, quit")

    while True:
        raw_command = input("\n> ").strip()
        parts = raw_command.split(maxsplit=1)
        command = parts[0].lower() if parts else ""
        argument = parts[1].strip() if len(parts) > 1 else ""

        if command == "add":
            title = input("Task title: ").strip()
            if title:
                priority = input("Priority (low/medium/high) [medium]: ").strip().lower()
                due_date = input("Due date (YYYY-MM-DD) [skip]: ").strip()
                tags_raw = input("Tags (comma-separated) [skip]: ").strip()
                task_id = add_task(
                    title,
                    priority if priority else "medium",
                    due_date if due_date else None,
                )
                tags = parse_tags(tags_raw)
                if tags:
                    set_tags_for_task(task_id, tags)
                print("Added.")
            else:
                print("Title can't be empty.")

        elif command == "list":
            if argument in ("todo", "done"):
                print_tasks(list_tasks(status=argument))
            elif argument:
                print_tasks(list_tasks(tag=argument))
            else:
                print_tasks(list_tasks())

        elif command == "edit":
            task_id = input("Task id to edit: ").strip()
            new_title = input("New title: ").strip()
            if task_id.isdigit() and edit_task(int(task_id), new_title):
                print("Updated.")
            else:
                print("Couldn't update that task (bad id or empty title).")

        elif command == "done":
            task_id = input("Task id to mark done: ").strip()
            if task_id.isdigit() and complete_task(int(task_id)):
                print("Marked done.")
            else:
                print("Couldn't find that task.")

        elif command == "delete":
            task_id = input("Task id to delete: ").strip()
            if task_id.isdigit() and delete_task(int(task_id)):
                print("Deleted.")
            else:
                print("Couldn't find that task.")

        elif command == "export":
            count = export_tasks_csv()
            print(f"Exported {count} task(s) to tasks.csv.")

        elif command == "quit":
            print("Bye!")
            break

        else:
            print("Unknown command. Try: add, list, edit, done, delete, export, quit")


if __name__ == "__main__":
    main()
