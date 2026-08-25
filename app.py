"""
TaskFlow CLI — a foundation task manager.

This is your starting point, not the finished product. Read through every
function before you touch anything — understand what exists before you
extend it. Then follow FEATURES.md to build on top of this.
"""

import sqlite3
from datetime import datetime

DB_NAME = "taskflow.db"


def get_connection():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create the tasks table if it doesn't already exist."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'todo',
            priority TEXT NOT NULL DEFAULT 'medium',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


PRIORITIES = ("low", "medium", "high")


def add_task(title, priority="medium"):
    """Add a new task with the given title. Status starts as 'todo'.
    Priority must be one of 'low', 'medium', 'high' — defaults to 'medium'."""
    if priority not in PRIORITIES:
        priority = "medium"
    conn = get_connection()
    conn.execute(
        "INSERT INTO tasks (title, status, priority, created_at) VALUES (?, ?, ?, ?)",
        (title, "todo", priority, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def list_tasks():
    """Return all tasks, most recently created first."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return rows


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
    """Delete a task by id. Returns True if a task was deleted."""
    conn = get_connection()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def print_tasks():
    """Print all tasks in a readable format."""
    tasks = list_tasks()
    if not tasks:
        print("No tasks yet. Add one!")
        return
    for task in tasks:
        marker = "[x]" if task["status"] == "done" else "[ ]"
        print(f"{marker} #{task['id']}  ({task['priority']})  {task['title']}")


def main():
    """Simple menu-driven loop. This is intentionally basic — improve it
    as you go."""
    init_db()
    print("=== TaskFlow CLI ===")
    print("Commands: add, list, done, delete, quit")

    while True:
        command = input("\n> ").strip().lower()

        if command == "add":
            title = input("Task title: ").strip()
            if title:
                priority = input("Priority (low/medium/high) [medium]: ").strip().lower()
                if priority:
                    add_task(title, priority)
                else:
                    add_task(title)
                print("Added.")
            else:
                print("Title can't be empty.")

        elif command == "list":
            print_tasks()

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

        elif command == "quit":
            print("Bye!")
            break

        else:
            print("Unknown command. Try: add, list, done, delete, quit")


if __name__ == "__main__":
    main()
