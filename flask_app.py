"""
TaskFlow web UI — the "stretch" feature from FEATURES.md.

A tiny Flask front-end over the same data layer used by the CLI (app.py):
add / list / done / delete, exposed as a small web page instead of a
terminal menu. Deliberately minimal — no auth, no tags/due-date UI — this
is meant to prove the CLI's functions work behind a web interface, not to
duplicate every CLI feature.

Run with: python flask_app.py
"""

from flask import Flask, redirect, render_template_string, request, url_for

import app as taskflow

flask_app = Flask(__name__)

# Single inline template (kept in one file for a "tiny" stretch app).
# Uses a plain, readable-on-narrow-screens layout: a form up top, a list
# below, and an explicit confirmation message after each action.
PAGE_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TaskFlow</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 2rem auto; padding: 0 1rem; }
    form { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
    input[type=text] { flex: 1; padding: 0.4rem; min-width: 10rem; }
    select, button { padding: 0.4rem; }
    ul { list-style: none; padding: 0; }
    li { padding: 0.5rem 0; border-bottom: 1px solid #ddd; display: flex; align-items: center; gap: 0.5rem; }
    .done { text-decoration: line-through; color: #888; }
    .priority { font-size: 0.8em; color: #555; }
    .message { background: #eef; padding: 0.5rem; border-radius: 4px; margin-bottom: 1rem; }
    .actions { margin-left: auto; display: flex; gap: 0.4rem; }
  </style>
</head>
<body>
  <h1>TaskFlow</h1>

  {% if message %}
  <div class="message">{{ message }}</div>
  {% endif %}

  <form method="post" action="{{ url_for('add') }}">
    <input type="text" name="title" placeholder="New task title" required>
    <select name="priority">
      <option value="low">low</option>
      <option value="medium" selected>medium</option>
      <option value="high">high</option>
    </select>
    <button type="submit">Add</button>
  </form>

  <ul>
    {% for task in tasks %}
    <li>
      <span class="{{ 'done' if task['status'] == 'done' else '' }}">
        #{{ task['id'] }} {{ task['title'] }}
      </span>
      <span class="priority">({{ task['priority'] }})</span>
      <span class="actions">
        {% if task['status'] != 'done' %}
        <form method="post" action="{{ url_for('done', task_id=task['id']) }}">
          <button type="submit">Mark done</button>
        </form>
        {% endif %}
        <form method="post" action="{{ url_for('delete', task_id=task['id']) }}">
          <button type="submit">Delete</button>
        </form>
      </span>
    </li>
    {% else %}
    <li>No tasks yet. Add one above!</li>
    {% endfor %}
  </ul>
</body>
</html>
"""


@flask_app.route("/")
def index():
    """Show all tasks, plus a one-off confirmation message via ?message=."""
    message = request.args.get("message")
    tasks = taskflow.list_tasks()
    return render_template_string(PAGE_TEMPLATE, tasks=tasks, message=message)


@flask_app.route("/add", methods=["POST"])
def add():
    """Handle the 'add task' form submission."""
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "medium")
    if title:
        taskflow.add_task(title, priority)
        message = f"Added '{title}'."
    else:
        message = "Title can't be empty."
    return redirect(url_for("index", message=message))


@flask_app.route("/done/<int:task_id>", methods=["POST"])
def done(task_id):
    """Handle the 'mark done' button for a single task."""
    if taskflow.complete_task(task_id):
        message = f"Marked task #{task_id} done."
    else:
        message = f"Couldn't find task #{task_id}."
    return redirect(url_for("index", message=message))


@flask_app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    """Handle the 'delete' button for a single task."""
    if taskflow.delete_task(task_id):
        message = f"Deleted task #{task_id}."
    else:
        message = f"Couldn't find task #{task_id}."
    return redirect(url_for("index", message=message))


if __name__ == "__main__":
    taskflow.init_db()
    flask_app.run(debug=True)
