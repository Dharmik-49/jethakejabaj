# db_utils.py
import sqlite3
from passlib.context import CryptContext

DB_NAME = "user_data.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def add_user(name, email, password):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (name, email, hashed_password) VALUES (?, ?, ?)",
            (name, email, hash_password(password)),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError: # This error occurs if the email is already registered
        return False
    finally:
        conn.close()

def check_user(email, password):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if user and verify_password(password, user['hashed_password']):
        return True
    return False

def get_user_id(email):
    conn = get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user['id'] if user else None

def save_chat_message(user_id, role, parts):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO chat_history (user_id, role, parts) VALUES (?, ?, ?)",
        (user_id, role, parts),
    )
    conn.commit()
    conn.close()

def load_chat_history(user_id):
    conn = get_db_connection()
    history = conn.execute(
        "SELECT role, parts FROM chat_history WHERE user_id = ? ORDER BY id ASC",
        (user_id,)
    ).fetchall()
    conn.close()
    # Convert from list of sqlite3.Row to list of dict
    return [{"role": row['role'], "parts": [row['parts']]} for row in history]