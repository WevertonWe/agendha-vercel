import sqlite3
from app.config import settings

def migrate():
    print(f"Connecting to {settings.DB_PATH}...")
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE mapa_pontos ADD COLUMN cor TEXT")
        print("Column 'cor' added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Migration failed (maybe column exists?): {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
