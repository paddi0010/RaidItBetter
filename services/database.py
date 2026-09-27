import os
import sqlite3
from datetime import datetime
from core.settings import get_app_data_path

def get_db_path():
    return os.path.join(get_app_data_path(), "favorites.db")

DB_FILE = get_db_path()

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            name TEXT PRIMARY KEY,
            position INTEGER DEFAULT 0
        )
    """)
    
    try:
        cursor.execute("ALTER TABLE favorites ADD COLUMN position INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    cursor.execute("PRAGMA table_info(raid_history)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if not columns:
        cursor.execute("""
            CREATE TABLE raid_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                target_channel TEXT NOT NULL,
                viewer_count INTEGER,
                status TEXT
            )
        """)
    elif "target_channel" not in columns:
        cursor.execute("DROP TABLE raid_history")
        cursor.execute("""
            CREATE TABLE raid_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                target_channel TEXT NOT NULL,
                viewer_count INTEGER,
                status TEXT
            )
        """)
        
    conn.commit()
    conn.close()

def get_favorites_db():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM favorites ORDER BY position ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def update_favorites_order(new_names_order):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    for index, name in enumerate(new_names_order):
        cursor.execute("UPDATE favorites SET position = ? WHERE LOWER(name) = ?", (index, name.lower()))
    conn.commit()
    conn.close()

def add_favorite_db(name):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(position) FROM favorites")
        max_pos = cursor.fetchone()[0]
        next_pos = 0 if max_pos is None else max_pos + 1

        cursor.execute("INSERT INTO favorites (name, position) VALUES (?, ?)", (name.lower(), next_pos))
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

def add_raid_history_db(target_channel, viewer_count=0, status="Success"):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO raid_history (timestamp, target_channel, viewer_count, status) VALUES (?, ?, ?, ?)", (timestamp, target_channel, viewer_count, status))
    conn.commit()
    conn.close()

def get_raid_history_db():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, target_channel, viewer_count, status FROM raid_history ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_last_raid_for_channel(channel_name):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp FROM raid_history WHERE LOWER(target_channel) = LOWER(?) ORDER BY id DESC LIMIT 1",
        (channel_name,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def clear_raid_history_db():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM raid_history")
    conn.commit()
    conn.close()