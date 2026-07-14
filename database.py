import sqlite3
import pandas as pd

DB_FILE = "oracle_storage.db"

def init_database():
    """Initializes unified local relational storage safely."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT,
            password TEXT,
            tier TEXT
        )
    """)
    
    # 2. Query Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ticker TEXT,
            lookback INTEGER,
            last_close REAL
        )
    """)
    
    # 3. Feedback Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user TEXT,
            satisfied TEXT,
            comment TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def log_terminal_query(ticker, lookback, last_close):
    """Safely logs market queries using parameterized queries to prevent SQL Injection."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO query_logs (ticker, lookback, last_close)
        VALUES (?, ?, ?)
    """, (ticker, lookback, last_close))
    conn.commit()
    conn.close()

def insert_user(username, email, hashed_password, tier):
    """Safely registers a new user node."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Username already exists!"
        
        cursor.execute("""
            INSERT INTO users (username, email, password, tier) 
            VALUES (?, ?, ?, ?)
        """, (username, email, hashed_password, tier))
        conn.commit()
        return True, "Success"
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        conn.close()

def insert_feedback(user, satisfied, comment):
    """Safely inserts trader reviews."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO feedback (user, satisfied, comment)
            VALUES (?, ?, ?)
        """, (user, satisfied, comment))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def get_feedback_records():
    """Retrieves all feedback records."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user, satisfied, comment, timestamp FROM feedback ORDER BY id DESC")
        return cursor.fetchall()
    except sqlite3.Error:
        return []
    finally:
        conn.close()