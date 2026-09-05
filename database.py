import os
import sqlite3
from settings import get_desktop_folder_path

def get_db_path():
    folder = get_desktop_folder_path()
    return os.path.join(folder, "favorites.db")

DB_FILE = get_db_path()

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_favorites_db():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM favorites")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_favorite_db(name):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO favorites (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def remove_favorite_db(name):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE name = ?", (name,))
    conn.commit()
    conn.close()