
import sqlite3
import sys  # noqa: F401

print("--- DB SCHEMA CHECK ---")
try:
    conn = sqlite3.connect('c:/Wev Dev/projetos/agendha/agendha.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print(f"Users Table Columns: {len(columns)}")
    for col in columns:
        print(col)
        
    print("\n--- BCRYPT CHECK ---")
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hash = pwd_context.hash("test")
        print("Bcrypt Hash Success:", hash[:10] + "...")
    except Exception as e:
        print("Bcrypt Failed:", e)
        
    conn.close()
except Exception as e:
    print("DB Check Failed:", e)
