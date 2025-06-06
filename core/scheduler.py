from data.database import connect
from datetime import datetime

def add_task(title, date_time=None):
    """
    Adds a new task to the database.
    date_time must be in ISO format: 'YYYY-MM-DDTHH:MM:SS'
    """
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, datetime) VALUES (?, ?)",
            (title, date_time)
        )
        conn.commit()

def list_tasks():
    """
    Retrieves all pending tasks.
    """
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, datetime, status FROM tasks WHERE status = 'pending'")
        return cursor.fetchall()

def mark_task_done(task_id):
    """
    Marks a task as completed.
    """
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = 'done' WHERE id = ?", (task_id,))
        conn.commit()

def delete_task(task_id):
    """
    Deletes a task from the database.
    """
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
