# TaskFlow CLI

A small command-line task manager, backed by SQLite. This is a **foundation**
— your job is to extend it. See `FEATURES.md` for what to build next.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## Commands (as of the foundation)

| Command | What it does |
|---|---|
| `add` | Add a new task, with an optional priority (`low`/`medium`/`high`, defaults to `medium`) |
| `list` | Show all tasks, with their priority |
| `done` | Mark a task as complete, by id |
| `delete` | Delete a task, by id |
| `quit` | Exit |

## Running tests

```bash
pytest
```

---

*As you add features, update this README to describe them — treat it as a
living document, not something you write once at the end.*
