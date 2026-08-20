# Learning Notes: Databases, Python Functions & Connecting Python to a Database

Hey Leroy — this covers three things, in the order you should read them:

1. Database basics (what a database is, tables, and SQL)
2. Python functions (how to write and use them properly)
3. How to connect to a database from Python and actually run queries

Each part has a short explanation, a runnable example, and a few exercises at the end. Try the exercises yourself before checking any answer — that's where the learning actually happens. We're using **SQLite** for all the database examples because it needs zero setup: it's built into Python, and the whole database is just a single file on disk.

---

## Part 1: Database Basics

### 1.1 What is a database?

A database is an organized collection of data that you can store, search, update, and delete reliably. Instead of keeping data in scattered text files or spreadsheets, a database gives you structure and a language (SQL) to work with that structure consistently.

A **DBMS** (Database Management System) is the software that manages the database — SQLite, PostgreSQL, MySQL, and Oracle are all examples. Most business systems use a **relational database** (RDBMS), which organizes data into **tables**.

### 1.2 Tables, rows, and columns

A table is like a spreadsheet:

| id | name    | department | salary |
|----|---------|------------|--------|
| 1  | Asha    | Engineering| 90000  |
| 2  | Ravi    | Sales      | 65000  |
| 3  | Meera   | Engineering| 95000  |

- Each **row** is one record (one employee).
- Each **column** is one attribute (name, department, salary).
- The **id** column here is the **primary key** — a value that uniquely identifies each row. No two rows can have the same primary key.

If another table (say, `projects`) needs to reference an employee, it stores that employee's `id` in a column like `employee_id`. That's called a **foreign key** — it links one table to another. This is how relational databases avoid duplicating data: employee details live in one place (`employees`), and anything that refers to an employee just points at their `id`.

### 1.3 SQL: the language you use to talk to a database

SQL (Structured Query Language) is how you create, read, update, and delete data. The four core operations are often called **CRUD**.

**Creating a table:**

```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT,
    salary REAL
);
```

**Inserting data:**

```sql
INSERT INTO employees (name, department, salary)
VALUES ('Asha', 'Engineering', 90000);
```

**Reading data:**

```sql
-- all columns, all rows
SELECT * FROM employees;

-- specific columns
SELECT name, salary FROM employees;

-- filtering with WHERE
SELECT * FROM employees WHERE department = 'Engineering';

-- sorting
SELECT * FROM employees ORDER BY salary DESC;

-- aggregating
SELECT department, AVG(salary) FROM employees GROUP BY department;
```

**Updating data:**

```sql
UPDATE employees SET salary = 98000 WHERE name = 'Asha';
```

**Deleting data:**

```sql
DELETE FROM employees WHERE name = 'Ravi';
```

**Joining tables** (combining rows from two related tables):

```sql
SELECT employees.name, projects.title
FROM employees
JOIN projects ON employees.id = projects.employee_id;
```

### 1.4 A word on normalization

"Normalization" just means organizing tables so each piece of information is stored once, not repeated everywhere. Example: instead of writing "Engineering" as a text string in every employee row (and risking typos like "Enginering" in some rows), some designs put departments in their own `departments` table and reference it by `department_id`. You don't need to master this now — just know the term, and know the underlying goal is "don't duplicate data you don't have to."

### Exercises — Part 1

1. Write the `CREATE TABLE` statement for a `books` table with columns: `id` (primary key), `title`, `author`, `year_published`, `price`.
2. Write a `SELECT` statement that returns all books published after 2015, sorted by price from lowest to highest.
3. Write an `UPDATE` statement that raises the price of every book by author `'J.K. Rowling'` by 10%. (Hint: `SET price = price * 1.10`)
4. In your own words: what's the difference between a primary key and a foreign key?

---

## Part 2: Python Functions

### 2.1 Why functions?

A function is a reusable block of code you can call by name instead of copy-pasting the same logic everywhere. It also gives you a clear boundary: inputs go in, one result comes out.

```python
def greet(name):
    return f"Hello, {name}!"

message = greet("Leroy")
print(message)   # Hello, Leroy!
```

- `def` starts a function definition.
- `name` is a **parameter** — a placeholder for whatever value is passed in.
- `"Leroy"` is the **argument** — the actual value passed when calling the function.
- `return` sends a value back to whoever called the function. If you don't `return` anything, the function returns `None`.

### 2.2 Default arguments

You can give a parameter a default value, so the caller doesn't have to supply it every time:

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Leroy"))              # Hello, Leroy!
print(greet("Leroy", "Welcome"))   # Welcome, Leroy!
```

### 2.3 `*args` and `**kwargs`

Sometimes you don't know in advance how many arguments will be passed.

```python
def total(*numbers):
    return sum(numbers)

print(total(1, 2, 3))       # 6
print(total(10, 20))        # 30
```

`*numbers` collects any number of positional arguments into a tuple. `**kwargs` does the same for keyword arguments, collecting them into a dictionary:

```python
def describe(**details):
    for key, value in details.items():
        print(f"{key}: {value}")

describe(name="Asha", role="Engineer")
# name: Asha
# role: Engineer
```

### 2.4 Scope — local vs. global

A variable created inside a function only exists inside that function (**local scope**). It doesn't leak out.

```python
def set_score():
    score = 100   # local to this function
    return score

set_score()
print(score)   # NameError: score is not defined
```

If you need a function to read a variable defined outside it, that's fine — but modifying a variable from outer/global scope inside a function requires the `global` keyword, and in general it's better to avoid relying on that and just pass values in and return them out.

### 2.5 Lambda (small anonymous functions)

For short, throwaway functions, Python has `lambda`:

```python
square = lambda x: x * x
print(square(5))   # 25
```

This is equivalent to:

```python
def square(x):
    return x * x
```

You'll mostly see `lambda` used inline, e.g. as a sort key: `sorted(people, key=lambda p: p["age"])`.

### 2.6 Docstrings

Good practice: document what a function does.

```python
def calculate_bonus(salary, rate=0.10):
    """Return the bonus amount for a given salary and bonus rate."""
    return salary * rate
```

### Exercises — Part 2

1. Write a function `is_even(n)` that returns `True` if `n` is even, `False` otherwise.
2. Write a function `average(*numbers)` that accepts any number of arguments and returns their average. Handle the case of zero arguments without crashing.
3. Write a function `apply_discount(price, discount=0.0)` that returns the discounted price. Call it once with just a price, and once with both a price and a discount.
4. What will this print, and why?
   ```python
   def add_item(item, items=[]):
       items.append(item)
       return items

   print(add_item("apple"))
   print(add_item("banana"))
   ```
   (This is a well-known Python gotcha — look up "mutable default arguments" if you get stuck.)

---

## Part 3: Connecting to a Database from Python

Python's standard library ships with the `sqlite3` module — no installation needed. This is the most common way to get started working with databases from code.

### 3.1 The basic pattern

Every database interaction in Python follows roughly the same shape: **connect → get a cursor → execute SQL → commit (if writing) → close**.

```python
import sqlite3

# Connect to a database file. If it doesn't exist, SQLite creates it.
connection = sqlite3.connect("company.db")

# A cursor is what you use to run SQL commands
cursor = connection.cursor()

# Create a table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT,
        salary REAL
    )
""")

# Save the changes
connection.commit()

# Always close the connection when you're done
connection.close()
```

### 3.2 Inserting data safely (parameterized queries)

**Never** build SQL by concatenating strings with `+` or f-strings when the values come from user input — that opens the door to SQL injection. Always use `?` placeholders and pass the values separately:

```python
import sqlite3

connection = sqlite3.connect("company.db")
cursor = connection.cursor()

# Insert one row — note the (value,) tuple, and the trailing comma for a single value
cursor.execute(
    "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)",
    ("Asha", "Engineering", 90000)
)

# Insert many rows at once
new_employees = [
    ("Ravi", "Sales", 65000),
    ("Meera", "Engineering", 95000),
]
cursor.executemany(
    "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)",
    new_employees
)

connection.commit()
connection.close()
```

### 3.3 Reading data back

```python
import sqlite3

connection = sqlite3.connect("company.db")
cursor = connection.cursor()

cursor.execute("SELECT * FROM employees WHERE department = ?", ("Engineering",))

# fetchall() gets every matching row as a list of tuples
rows = cursor.fetchall()
for row in rows:
    print(row)   # e.g. (1, 'Asha', 'Engineering', 90000.0)

# fetchone() gets just the next single row (useful when you expect one result)
cursor.execute("SELECT * FROM employees WHERE id = ?", (1,))
one_row = cursor.fetchone()
print(one_row)

connection.close()
```

### 3.4 The cleaner way: using `with`

Manually calling `connection.close()` every time is easy to forget, especially if an error happens partway through. Python's `with` statement (a **context manager**) handles cleanup for you:

```python
import sqlite3

with sqlite3.connect("company.db") as connection:
    cursor = connection.cursor()
    cursor.execute("SELECT name, salary FROM employees ORDER BY salary DESC")
    for name, salary in cursor.fetchall():
        print(f"{name}: {salary}")
# connection is automatically committed/closed when the block ends
```

Note: for `sqlite3` specifically, `with connection` auto-commits or rolls back the transaction on exit, but it does **not** auto-close the connection — closing it explicitly (or letting it go out of scope) is still good practice.

### 3.5 Putting it together: functions + database

This is where Part 2 and Part 3 meet — in real code, you wrap your database logic in functions instead of writing raw SQL everywhere:

```python
import sqlite3

DB_NAME = "company.db"

def add_employee(name, department, salary):
    """Insert a new employee and return their new id."""
    with sqlite3.connect(DB_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)",
            (name, department, salary)
        )
        return cursor.lastrowid

def get_employees_by_department(department):
    """Return a list of (name, salary) tuples for a given department."""
    with sqlite3.connect(DB_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name, salary FROM employees WHERE department = ?",
            (department,)
        )
        return cursor.fetchall()

def give_raise(employee_id, percent):
    """Increase an employee's salary by a percentage."""
    with sqlite3.connect(DB_NAME) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE employees SET salary = salary * (1 + ?) WHERE id = ?",
            (percent / 100, employee_id)
        )

# Example usage
new_id = add_employee("Priya", "Engineering", 88000)
give_raise(new_id, 5)
print(get_employees_by_department("Engineering"))
```

This pattern — small functions, each with one clear job, each opening and closing its own connection — is exactly what you'll see in real production code, just with more error handling and usually a proper server-based database (PostgreSQL/MySQL) instead of a local SQLite file.

### Exercises — Part 3

1. Write a function `delete_employee(employee_id)` that deletes an employee by id.
2. Write a function `total_payroll()` that returns the sum of all salaries in the `employees` table. (Hint: `SELECT SUM(salary) FROM employees`)
3. Write a function `find_employee(name)` that returns the full row for an employee with a given name, or `None` if no such employee exists.
4. Deliberately try inserting a name that contains a single quote, like `O'Brien`, using the `?` placeholder method. Confirm it works. Then explain in your own words why building the SQL string manually (e.g. `f"...VALUES ('{name}', ...)"`) would have broken on that same input.

---

## What's next

Once you're comfortable with all three parts, a good next step is a small self-contained project: build a tiny command-line "employee manager" that lets you add, list, update, and delete employees, using the functions pattern from section 3.5. That combines everything here into one working program.

If anything above doesn't make sense, or a term gets used before it's explained, flag it — better to ask early than get stuck on later sections that build on it.
