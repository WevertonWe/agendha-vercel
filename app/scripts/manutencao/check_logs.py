import sqlite3
import time

import os
import sys

# Calculate root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)
DB_PATH = os.path.join(BASE_DIR, "agendha.db")

def check_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE operacao='ACESSO'")
    count = cursor.fetchone()[0]
    print(f"Total ACESSO logs: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM audit_logs WHERE operacao='ACESSO' ORDER BY id DESC LIMIT 1")
        print("Last Log:", cursor.fetchone())
    conn.close()

if __name__ == "__main__":
    time.sleep(2) # Wait for stress test to likely finish writing
    check_logs()
