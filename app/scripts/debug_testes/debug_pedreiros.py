import sqlite3
import os

DB_PATH = os.path.join("app", "agendha.db")

def check_pedreiros():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pedreiros'")
        table = cursor.fetchone()
        
        if not table:
            print("Table 'pedreiros' DOES NOT EXIST.")
        else:
            print("Table 'pedreiros' exists.")
            
            # Check columns
            cursor.execute("PRAGMA table_info(pedreiros)")
            columns = cursor.fetchall()
            print("Columns:", [col[1] for col in columns])
            
            # Check data
            cursor.execute("SELECT * FROM pedreiros")
            rows = cursor.fetchall()
            print(f"Total rows: {len(rows)}")
            for row in rows:
                print(row)
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_pedreiros()
