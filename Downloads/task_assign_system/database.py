import sqlite3
from datetime import datetime

conn = sqlite3.connect("task_system.db", check_same_thread=False)
cursor = conn.cursor()

# -------------------------------
# TABLES
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    priority TEXT,
    status TEXT,
    assigned_to TEXT,
    start_time TEXT,
    end_time TEXT
)
""")

conn.commit()

# -------------------------------
# MEMBER FUNCTIONS
# -------------------------------
def add_member(name):
    try:
        cursor.execute("INSERT INTO members (name) VALUES (?)", (name,))
        conn.commit()
    except:
        pass

def get_members():
    return cursor.execute("SELECT * FROM members").fetchall()

# -------------------------------
# TASK FUNCTIONS
# -------------------------------
def add_task(name, priority):
    cursor.execute("""
    INSERT INTO tasks (name, priority, status, assigned_to, start_time, end_time)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (name, priority, "waiting", None, None, None))
    conn.commit()

def get_tasks():
    return cursor.execute("SELECT * FROM tasks").fetchall()

def assign_task(task_id, member_name):
    cursor.execute("""
    UPDATE tasks 
    SET status=?, assigned_to=?, start_time=?
    WHERE id=?
    """, ("assigned", member_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id))
    conn.commit()

def complete_task(task_id):
    cursor.execute("""
    UPDATE tasks 
    SET status=?, end_time=?
    WHERE id=?
    """, ("completed", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_id))
    conn.commit()