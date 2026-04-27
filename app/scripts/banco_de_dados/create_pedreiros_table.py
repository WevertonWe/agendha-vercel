import sqlite3
import os

# Define database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app", "agendha.db")

def create_table():
    print(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create pedreiros table
    print("Creating 'pedreiros' table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedreiros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_completo TEXT NOT NULL,
        cpf TEXT UNIQUE NOT NULL,
        telefone TEXT,
        endereco TEXT,
        status TEXT DEFAULT 'Ativo'
    )
    """)
    
    conn.commit()
    print("Table 'pedreiros' created successfully (if it didn't exist).")
    
    # Verify
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pedreiros'")
    if cursor.fetchone():
        print("Verification: Table 'pedreiros' exists.")
    else:
        print("Verification: Table 'pedreiros' NOT found!")

    conn.close()

if __name__ == "__main__":
    create_table()
