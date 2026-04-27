import sqlite3
import os

# Calculate root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, 'agendha.db')

def create_audit_table():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {os.path.abspath(DB_PATH)}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create audit_logs table
    # Using TEXT for JSON columns as SQLite doesn't have a native JSON type but supports JSON functions on TEXT
    sql = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id TEXT,
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        tabela TEXT,
        registro_id INTEGER,
        operacao TEXT,
        valor_antigo TEXT,
        valor_novo TEXT,
        detalhes TEXT
    );
    """
    try:
        cursor.execute(sql)
        conn.commit()
        print("Table 'audit_logs' created successfully.")
        
        # Verify schema
        cursor.execute("PRAGMA table_info(audit_logs);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"Column: {col[1]}, Type: {col[2]}")
            
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_audit_table()
