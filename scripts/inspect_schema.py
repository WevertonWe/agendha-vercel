
import sqlite3
import os  # noqa: F401

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'agendha.db')
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open('schema_output.txt', 'w', encoding='utf-8') as f:
        # Get bsf_visitas
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='bsf_visitas'")
        row = cursor.fetchone()
        f.write(f"--- bsf_visitas ---\n{row[0] if row else 'NOT FOUND'}\n\n")
        
        # Get users
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
        row = cursor.fetchone()
        f.write(f"--- users ---\n{row[0] if row else 'NOT FOUND'}\n\n")

    print("Schema dumped to schema_output.txt")
except Exception as e:
    with open('schema_output.txt', 'w', encoding='utf-8') as f:
        f.write(f"ERROR: {e}")
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
