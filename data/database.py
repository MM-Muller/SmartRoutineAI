import sqlite3
from datetime import datetime

DB_PATH = "data/user_data.db"

# Connect to the database
def connect():
    return sqlite3.connect(DB_PATH)

# Create tables if they don't exist
def create_tables():
    with connect() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT,
                time TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                description TEXT,
                classification TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT,
                response TEXT,
                timestamp TEXT
            )
        ''')

        conn.commit()

# Run this script to initialize the database
if __name__ == '__main__':
    create_tables()
    print("Tables created successfully.")
