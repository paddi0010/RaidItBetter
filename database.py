import sqlite3

DB_FILE = "favorites.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            username TEXT PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

def get_favorites_db():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM favorites")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_favorite_db(username):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO favorites (username) VALUES (?)", (username,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def remove_favorite_db(username):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE username = ?", (username,))
    conn.commit()
    conn.close()