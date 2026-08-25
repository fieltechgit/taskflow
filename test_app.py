"""
Example tests for TaskFlow. Run with: pytest

This file shows the PATTERN — you're expected to add more tests as you
add features. Notice how each test sets up a clean database first, so
tests don't interfere with each other or with your real data.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as taskflow


@pytest.fixture(autouse=True)
def clean_database():
    """Runs before AND after every test — ensures a fresh database each time."""
    if os.path.exists(taskflow.DB_NAME):
        os.remove(taskflow.DB_NAME)
    taskflow.init_db()
    yield
    if os.path.exists(taskflow.DB_NAME):
        os.remove(taskflow.DB_NAME)


def test_add_task_creates_a_task():
    taskflow.add_task("Buy groceries")
    tasks = taskflow.list_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Buy groceries"
    assert tasks[0]["status"] == "todo"


def test_new_task_starts_as_todo_not_done():
    taskflow.add_task("Write report")
    tasks = taskflow.list_tasks()
    assert tasks[0]["status"] == "todo"


def test_complete_task_marks_it_done():
    taskflow.add_task("Read a book")
    task_id = taskflow.list_tasks()[0]["id"]
    result = taskflow.complete_task(task_id)
    assert result is True
    assert taskflow.list_tasks()[0]["status"] == "done"


def test_complete_task_returns_false_for_unknown_id():
    result = taskflow.complete_task(9999)
    assert result is False


def test_delete_task_removes_it():
    taskflow.add_task("Temporary task")
    task_id = taskflow.list_tasks()[0]["id"]
    taskflow.delete_task(task_id)
    assert len(taskflow.list_tasks()) == 0


def test_new_task_defaults_to_medium_priority():
    taskflow.add_task("Unspecified priority")
    assert taskflow.list_tasks()[0]["priority"] == "medium"


def test_add_task_with_explicit_priority():
    taskflow.add_task("Urgent fix", priority="high")
    assert taskflow.list_tasks()[0]["priority"] == "high"


def test_invalid_priority_falls_back_to_medium():
    taskflow.add_task("Typo'd priority", priority="urgent")
    assert taskflow.list_tasks()[0]["priority"] == "medium"


# ---------------------------------------------------------------------
# Your turn: as you add features (priority, due dates, tags...), add
# tests here that follow this same pattern. A good test:
#   1. Sets up specific data
#   2. Does ONE thing
#   3. Checks the result is exactly what you expect
# ---------------------------------------------------------------------
