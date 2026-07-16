import sqlite3
import os

DB_FILE = "oracle_system.db"

def get_db_connection():
    """Generates an active thread-safe connection to the localized SQLite file."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

def init_db():
    """Initializes the relational grid structures if the database file is clean/new."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 👥 Secure User Core Entity Matrix Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT,
            tier TEXT
        )
    """)
    
    # 💬 User Experience Network Review Log Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            satisfied TEXT,
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def get_user(username):
    """Fetches a singular user record matching a designated Node ID handle."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, password, tier FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def insert_user(username, email, password, tier):
    """Provisions a new hardware node profile within the internal database state."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password, tier) VALUES (?, ?, ?, ?)", 
                       (username, email, password, tier))
        conn.commit()
        conn.close()
        return True, "Success"
    except sqlite3.IntegrityError:
        return False, "Node ID already registered."
    except Exception as e:
        return False, str(e)

def insert_feedback(username, satisfied, comment):
    """Pushes a user feedback message directly into the analytical log tables."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (username, satisfied, comment) VALUES (?, ?, ?)", 
                       (username, satisfied, comment))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def get_feedback():
    """Retrieves all feedback records chronologically ordered by entry."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, satisfied, comment, timestamp FROM feedback ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def get_all_users():
    """
    🔐 ROOT ACCESS EXTRACTION MODULE
    Queries and returns all rows from the users matrix for target dashboard auditing.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password, tier FROM users ORDER BY id ASC")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Database extraction failure: {e}")
        return []

# Execute relational table builds immediately upon environment structural import
init_db()
