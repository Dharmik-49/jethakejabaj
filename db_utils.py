# db_utils.py
import sqlite3
from passlib.context import CryptContext
import json

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
    except sqlite3.IntegrityError:
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
    return [{"role": row['role'], "parts": [row['parts']]} for row in history]

# --- NEW: Functions for Prediction History ---
def save_prediction(user_id, inputs_dict, recommended_crop):
    """Saves a new prediction and ensures only the last 5 are kept."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all prediction IDs for the user, ordered from oldest to newest
    cursor.execute("SELECT id FROM prediction_history WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
    history_ids = [row['id'] for row in cursor.fetchall()]
    
    # If there are 5 or more, delete the oldest one
    if len(history_ids) >= 5:
        oldest_id = history_ids[0]
        cursor.execute("DELETE FROM prediction_history WHERE id = ?", (oldest_id,))
    
    # Insert the new prediction
    inputs_json = json.dumps(inputs_dict)
    cursor.execute(
        "INSERT INTO prediction_history (user_id, inputs, recommended_crop) VALUES (?, ?, ?)",
        (user_id, inputs_json, recommended_crop)
    )
    conn.commit()
    conn.close()

def load_prediction_history(user_id):
    """Loads the last 5 predictions for a user, ordered by most recent."""
    conn = get_db_connection()
    history = conn.execute(
        "SELECT inputs, recommended_crop, timestamp FROM prediction_history WHERE user_id = ? ORDER BY timestamp DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    # Parse the JSON string back into a dictionary for each row
    return [{"inputs": json.loads(row['inputs']), "recommended_crop": row['recommended_crop'], "timestamp": row['timestamp']} for row in history]
