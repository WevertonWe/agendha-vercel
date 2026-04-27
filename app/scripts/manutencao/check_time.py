import sqlite3
from datetime import datetime
import os
import sys

# Calculate root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)
DB_PATH = os.path.join(BASE_DIR, "agendha.db")

from app.core.time_utils import get_bahia_datetime  # noqa: E402

def verify_time():
    print("Verifying Timezone Consistency...")
    print("Verifying Timezone Consistency...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data_hora FROM audit_logs WHERE operacao='ACESSO' ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print("No logs found.")
        return

    log_time_str = row[0]
    # Assuming DB stores YYYY-MM-DD HH:MM:SS
    log_time = datetime.strptime(log_time_str, '%Y-%m-%d %H:%M:%S')
    
    # Current Bahia Time
    now_bahia = get_bahia_datetime().replace(tzinfo=None) # naive for comparison
    
    diff = abs((now_bahia - log_time).total_seconds())
    
    print(f"Log Time (DB): {log_time_str}")
    print(f"Bahia Time (Now): {now_bahia.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Difference: {diff} seconds")
    
    if diff < 60:
        print("PASS: Time matches Bahia Timezone.")
    else:
        print("FAIL: Time discrepancy detected.")

if __name__ == "__main__":
    verify_time()
