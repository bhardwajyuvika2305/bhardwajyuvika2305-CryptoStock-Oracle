import os
import sqlite3

# Determine if a cloud PostgreSQL or local SQLite environment is required
# If you eventually use a cloud database, add DATABASE_URL to your deployment secrets.
DATABASE_URL = os.getenv("DATABASE_URL")
DB_FILE = "oracle_system.db"

def get_db_connection():
    """Generates an active thread-safe connection to the localized SQLite or external cloud instance."""
    if DATABASE_URL:
        try:
            import psycopg2
            return psycopg2.connect(DATABASE_URL, sslmode="require")
        except ImportError:
            raise ImportError("psycopg2-binary is missing from requirements.txt for cloud database support.")
    else:
        # Standard local standalone fallback
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        return conn

def init_db():
    """Initializes the relational grid structures if the database layer is clean/new."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check dialect for parameter placeholders (? for SQLite, %s for Postgres)
    placeholder = "%s" if DATABASE_URL else "?"
    id_autoincrement = "SERIAL PRIMARY KEY" if DATABASE_URL else "INTEGER PRIMARY KEY AUTOINCREMENT"
    text_type = "TEXT" if DATABASE_URL else "TEXT"
    ts_default = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP" if DATABASE_URL else "DATETIME DEFAULT CURRENT_TIMESTAMP"

    # 👥 Secure User Core Entity Matrix Table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id {id_autoincrement},
            username {text_type} UNIQUE,
            email {text_type},
            password {text_type},
            tier {text_type}
        )
    """)
    
    # 💬 User Experience Network Review Log Table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS feedback (
            id {id_autoincrement},
            username {text_type},
            satisfied {text_type},
            comment {text_type},
            timestamp {ts_default}
        )
    """)
    
    conn.commit()
    conn.close()

def get_user(username):
    """Fetches a singular user record matching a designated Node ID handle."""
    conn = get_db_connection()
    cursor = conn.cursor()
    p = "%s" if DATABASE_URL else "?"
    cursor.execute(f"SELECT id, username, email, password, tier FROM users WHERE username = {p}", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def insert_user(username, email, password, tier):
    """Provisions a new hardware node profile within the internal database state."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = "%s" if DATABASE_URL else "?"
        cursor.execute(f"INSERT INTO users (username, email, password, tier) VALUES ({p}, {p}, {p}, {p})", 
                       (username, email, password, tier))
        conn.commit()
        conn.close()
        return True, "Success"
    except Exception as e:
        error_str = str(e).lower()
        if "unique" in error_str or "integrity" in error_str:
            return False, "Node ID already registered."
        return False, str(e)

def insert_feedback(username, satisfied, comment):
    """Pushes a user feedback message directly into the analytical log tables."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        p = "%s" if DATABASE_URL else "?"
        cursor.execute(f"INSERT INTO feedback (username, satisfied, comment) VALUES ({p}, {p}, {p})", 
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
