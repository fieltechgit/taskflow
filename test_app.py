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
# Edit a task's title
# ---------------------------------------------------------------------

def test_edit_task_changes_title():
    taskflow.add_task("Old title")
    task_id = taskflow.list_tasks()[0]["id"]
    result = taskflow.edit_task(task_id, "New title")
    assert result is True
    assert taskflow.list_tasks()[0]["title"] == "New title"


def test_edit_task_returns_false_for_unknown_id():
    assert taskflow.edit_task(9999, "Whatever") is False


def test_edit_task_rejects_blank_title():
    taskflow.add_task("Keep me")
    task_id = taskflow.list_tasks()[0]["id"]
    assert taskflow.edit_task(task_id, "   ") is False
    assert taskflow.list_tasks()[0]["title"] == "Keep me"


# ---------------------------------------------------------------------
# Filter by status
# ---------------------------------------------------------------------

def test_list_tasks_filters_by_todo_status():
    taskflow.add_task("Not done")
    taskflow.add_task("Done already")
    done_id = taskflow.list_tasks()[0]["id"]
    taskflow.complete_task(done_id)

    todo_tasks = taskflow.list_tasks(status="todo")
    assert len(todo_tasks) == 1
    assert todo_tasks[0]["title"] == "Not done"


def test_list_tasks_filters_by_done_status():
    taskflow.add_task("Not done")
    taskflow.add_task("Done already")
    done_id = taskflow.list_tasks()[0]["id"]
    taskflow.complete_task(done_id)

    done_tasks = taskflow.list_tasks(status="done")
    assert len(done_tasks) == 1
    assert done_tasks[0]["title"] == "Done already"


def test_list_tasks_with_no_filter_returns_everything():
    taskflow.add_task("A")
    taskflow.add_task("B")
    assert len(taskflow.list_tasks()) == 2


# ---------------------------------------------------------------------
# Due dates
# ---------------------------------------------------------------------

def test_add_task_stores_due_date():
    taskflow.add_task("Pay rent", due_date="2026-09-01")
    assert taskflow.list_tasks()[0]["due_date"] == "2026-09-01"


def test_add_task_without_due_date_stores_none():
    taskflow.add_task("No deadline")
    assert taskflow.list_tasks()[0]["due_date"] is None


def test_list_tasks_sorts_by_due_date_soonest_first():
    taskflow.add_task("Later", due_date="2026-12-01")
    taskflow.add_task("Sooner", due_date="2026-09-01")
    taskflow.add_task("No date")

    titles = [t["title"] for t in taskflow.list_tasks()]
    assert titles == ["Sooner", "Later", "No date"]


# ---------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------

def test_parse_tags_splits_and_cleans_input():
    assert taskflow.parse_tags(" work, Personal ,,urgent") == ["work", "personal", "urgent"]


def test_parse_tags_handles_blank_input():
    assert taskflow.parse_tags("") == []
    assert taskflow.parse_tags(None) == []


def test_set_and_get_tags_for_task():
    taskflow.add_task("Tagged task")
    task_id = taskflow.list_tasks()[0]["id"]
    taskflow.set_tags_for_task(task_id, ["work", "urgent"])
    assert taskflow.get_tags_for_task(task_id) == ["urgent", "work"]


def test_set_tags_replaces_previous_tags():
    taskflow.add_task("Retagged task")
    task_id = taskflow.list_tasks()[0]["id"]
    taskflow.set_tags_for_task(task_id, ["old"])
    taskflow.set_tags_for_task(task_id, ["new"])
    assert taskflow.get_tags_for_task(task_id) == ["new"]


def test_list_tasks_filters_by_tag():
    taskflow.add_task("Work task")
    work_id = taskflow.list_tasks()[0]["id"]
    taskflow.set_tags_for_task(work_id, ["work"])

    taskflow.add_task("Personal task")
    personal_id = taskflow.list_tasks(status="todo")[0]["id"]
    taskflow.set_tags_for_task(personal_id, ["personal"])

    work_tasks = taskflow.list_tasks(tag="work")
    assert len(work_tasks) == 1
    assert work_tasks[0]["title"] == "Work task"


def test_delete_task_also_removes_its_tags():
    taskflow.add_task("Tagged task")
    task_id = taskflow.list_tasks()[0]["id"]
    taskflow.set_tags_for_task(task_id, ["work"])
    taskflow.delete_task(task_id)
    # No task_tags row should be left dangling for a deleted task.
    assert taskflow.get_tags_for_task(task_id) == []


# ---------------------------------------------------------------------
# Export to CSV
# ---------------------------------------------------------------------

def test_export_tasks_csv_writes_all_tasks(tmp_path):
    taskflow.add_task("Exportable", priority="high", due_date="2026-10-01")
    task_id = taskflow.list_tasks()[0]["id"]
    taskflow.set_tags_for_task(task_id, ["work"])

    out_file = tmp_path / "tasks.csv"
    count = taskflow.export_tasks_csv(str(out_file))

    assert count == 1
    content = out_file.read_text()
    assert "Exportable" in content
    assert "high" in content
    assert "2026-10-01" in content
    assert "work" in content


def test_export_tasks_csv_returns_zero_for_no_tasks(tmp_path):
    out_file = tmp_path / "empty.csv"
    count = taskflow.export_tasks_csv(str(out_file))
    assert count == 0


# ---------------------------------------------------------------------
# Basic auth
# ---------------------------------------------------------------------

def test_create_user_succeeds_with_valid_input():
    assert taskflow.create_user("alice", "hunter2") is True


def test_create_user_rejects_duplicate_username():
    taskflow.create_user("bob", "password1")
    assert taskflow.create_user("bob", "password2") is False


def test_create_user_rejects_blank_username_or_password():
    assert taskflow.create_user("", "password") is False
    assert taskflow.create_user("charlie", "") is False


def test_authenticate_user_succeeds_with_correct_password():
    taskflow.create_user("dave", "correct-horse")
    assert taskflow.authenticate_user("dave", "correct-horse") is True


def test_authenticate_user_fails_with_wrong_password():
    taskflow.create_user("erin", "correct-horse")
    assert taskflow.authenticate_user("erin", "wrong-password") is False


def test_authenticate_user_fails_for_unknown_username():
    assert taskflow.authenticate_user("nobody", "whatever") is False


def test_password_is_not_stored_in_plaintext():
    taskflow.create_user("frank", "supersecret")
    conn = taskflow.get_connection()
    row = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?", ("frank",)
    ).fetchone()
    conn.close()
    assert "supersecret" not in row["password_hash"]


def test_user_exists_reflects_registered_users():
    assert taskflow.user_exists("gina") is False
    taskflow.create_user("gina", "password")
    assert taskflow.user_exists("gina") is True


def test_has_any_users_reflects_registration_state():
    assert taskflow.has_any_users() is False
    taskflow.create_user("hank", "password")
    assert taskflow.has_any_users() is True


# ---------------------------------------------------------------------
# Flask web UI (stretch feature)
# ---------------------------------------------------------------------

def test_flask_index_lists_tasks():
    import flask_app

    taskflow.add_task("Web task")
    client = flask_app.flask_app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Web task" in response.data


def test_flask_add_creates_a_task():
    import flask_app

    client = flask_app.flask_app.test_client()
    response = client.post("/add", data={"title": "Added via web", "priority": "high"})
    assert response.status_code == 302
    titles = [t["title"] for t in taskflow.list_tasks()]
    assert "Added via web" in titles


def test_flask_done_marks_task_complete():
    import flask_app

    taskflow.add_task("Finish me")
    task_id = taskflow.list_tasks()[0]["id"]
    client = flask_app.flask_app.test_client()
    client.post(f"/done/{task_id}")
    assert taskflow.list_tasks()[0]["status"] == "done"


def test_flask_delete_removes_task():
    import flask_app

    taskflow.add_task("Remove me")
    task_id = taskflow.list_tasks()[0]["id"]
    client = flask_app.flask_app.test_client()
    client.post(f"/delete/{task_id}")
    assert taskflow.list_tasks() == []


# ---------------------------------------------------------------------
# print_tasks (presentation helper)
# ---------------------------------------------------------------------

def test_print_tasks_shows_placeholder_when_empty(capsys):
    taskflow.print_tasks([])
    assert "No tasks yet" in capsys.readouterr().out


def test_print_tasks_shows_due_date_and_tags(capsys):
    taskflow.add_task("Full task", priority="high", due_date="2026-09-01")
    task_id = taskflow.list_tasks()[0]["id"]
    taskflow.set_tags_for_task(task_id, ["work"])
    taskflow.print_tasks()
    output = capsys.readouterr().out
    assert "Full task" in output
    assert "due:2026-09-01" in output
    assert "tags:work" in output


# ---------------------------------------------------------------------
# login_prompt (interactive auth gate) — inputs simulated via monkeypatch
# ---------------------------------------------------------------------

def test_login_prompt_registers_first_user(monkeypatch):
    # No users exist yet, so login_prompt should go straight to registration.
    inputs = iter(["newuser", "newpass"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))
    username = taskflow.login_prompt()
    assert username == "newuser"
    assert taskflow.user_exists("newuser")


def test_login_prompt_logs_in_existing_user(monkeypatch):
    taskflow.create_user("existing", "correct-pw")
    inputs = iter(["login", "existing", "correct-pw"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))
    username = taskflow.login_prompt()
    assert username == "existing"


def test_login_prompt_retries_after_wrong_password(monkeypatch):
    taskflow.create_user("existing", "correct-pw")
    inputs = iter(["login", "existing", "wrong-pw", "login", "existing", "correct-pw"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))
    username = taskflow.login_prompt()
    assert username == "existing"


# ---------------------------------------------------------------------
# main() — the full CLI loop, driven end-to-end via simulated input
# ---------------------------------------------------------------------

def test_main_runs_full_command_cycle(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    inputs = iter(
        [
            "register",           # login_prompt: choose register
            "cliuser", "clipass",  # login_prompt: credentials
            "add",                 # add a task
            "Buy milk", "high", "2026-09-01", "errand",
            "list", "",            # list all tasks
            "list todo",           # filter by status
            "edit",                # edit the task's title
            "1", "Buy oat milk",
            "export",              # export to CSV
            "done",                # mark it done
            "1",
            "delete",               # delete it
            "1",
            "bogus-command",        # unknown command branch
            "quit",                 # exit the loop
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))
    taskflow.main()
    output = capsys.readouterr().out
    assert "Added." in output
    assert "Updated." in output
    assert "Exported" in output
    assert "Marked done." in output
    assert "Deleted." in output
    assert "Unknown command" in output
    assert "Bye!" in output
