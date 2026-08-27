# TaskFlow — Your Feature Roadmap

This is your foundation to build on, not a finished app. Work through the
tiers below roughly in order. Each feature you add should come with:

1. **The feature itself** (in `app.py`)
2. **A test for it** (in `tests/test_app.py`, following the existing pattern)
3. **A line in the README** explaining how to use it

That loop — build, test, document — is the actual habit this exercise is
training, not just the Python.

---

## Easy

- [ ] **Priority field** — add a `priority` column (`low` / `medium` / `high`).
  New tasks default to `medium`. Let `list` show priority next to each task.
- [ ] **Edit a task's title** — a new `edit` command that lets you change an
  existing task's title by id.
- [ ] **Filter by status** — `list todo` shows only incomplete tasks,
  `list done` shows only completed ones, `list` alone shows everything.

## Medium

- [ ] **Due dates** — add a `due_date` column. When adding a task, optionally
  ask for a due date (skip if left blank). Sort `list` by due date, soonest
  first, with tasks that have no due date at the end.
- [ ] **Tags** — allow a task to have one or more tags (e.g. `work`, `personal`).
  This needs a second table and a join — this is where "a bit of database"
  becomes "actually using a relational database." Add a `list <tag>` filter.
- [ ] **Export to CSV** — a new `export` command that writes all tasks to a
  `tasks.csv` file, one row per task.

## Hard

- [ ] **Basic auth** — before any commands work, require a username + password
  (hashed with `bcrypt`, not stored in plaintext — same rule as the real
  assessment). Store users in a new `users` table.
- [ ] **Full pytest coverage** — by this point you should have tests for every
  feature above. Run `pytest --cov` and get meaningful coverage, not just
  passing tests.
- [ ] **Stretch: turn it into a tiny web app** — using Flask, expose the same
  functionality (`add`, `list`, `done`, `delete`) as a small web UI instead
  of a CLI. This is optional and a genuine jump in complexity — only attempt
  it once everything above is solid.

---

## Documentation checkpoint

Once you've done a few features, write a proper `README.md` covering:
- What TaskFlow does
- How to install and run it (`pip install -r requirements.txt`, `python app.py`)
- How to run the tests (`pytest`)
- A list of commands and what they do

Write it for someone who has never seen this project — same rule as
the testing/docs track.

## Design checkpoint (if you build the Flask stretch)

If you get to the web UI, review it against the dashboard checklist from
the Concepts Library before calling it done — consistency, confirmation
messages, readable on a narrow screen, clear labels.

---

## A note on how to work

Don't try to do all of Easy, then all of Medium, then all of Hard in one
sitting. Pick one feature, build it, test it, document it, then move to the
next. Small complete loops beat one giant unfinished push.
