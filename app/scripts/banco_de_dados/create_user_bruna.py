
import sys
import os
import sqlite3

# Add the project root to the python path
sys.path.append(os.getcwd())

from app.config import settings
from app.core.auth.utils import get_password_hash

def ensure_user_bruna():
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()

    username = "bruna"
    default_password = "123" # Simple password for initial setup/testing
    
    print(f"Checking for user '{username}'...")
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row:
        print(f"User '{username}' already exists.")
    else:
        print(f"User '{username}' does not exist. Creating...")
        hashed_pw = get_password_hash(default_password)
        try:
            # Assuming 'user' role is appropriate based on services.py exploration
            # and full_name as 'Bruna'
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, is_active, full_name) VALUES (?, ?, ?, 1, ?)",
                (username, hashed_pw, "user", "Bruna")
            )
            conn.commit()
            print(f"User '{username}' created successfully with password '{default_password}'.")
        except Exception as e:
            print(f"Error creating user: {e}")
            conn.rollback()
    
    conn.close()

if __name__ == "__main__":
    ensure_user_bruna()
