import os
import sqlite3
import sys

# Calculate root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from app.services.backup_service import create_snapshot, DB_PATH  # noqa: E402

def test_backup_service():
    print("Starting Backup Service Verification...")
    
    # Ensure source DB exists
    if not os.path.exists(DB_PATH):
        print(f"Creating dummy {DB_PATH} for testing...")
        conn = sqlite3.connect(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO test (name) VALUES ('Test Item')")
        conn.commit()
        conn.close()

    try:
        # 1. Trigger Snapshot
        print("1. Triggering create_snapshot('verification')...")
        backup_path = create_snapshot("verification")
        print(f"   Returned Path: {backup_path}")

        # 2. Verify File Existence
        print("2. Verifying file existence...")
        if os.path.exists(backup_path):
            print("   PASS: File exists.")
        else:
            print("   FAIL: File does not exist.")
            return

        # 3. Verify Integrity (Connect to backup)
        print("3. Verifying backup integrity...")
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"   PASS: Successfully connected. Found tables: {len(tables)}")
            conn.close()
        except sqlite3.Error as e:
            print(f"   FAIL: Database corruption detected: {e}")
            return

        # Cleanup
        print("4. Cleaning up test artifact...")
        os.remove(backup_path)
        print("   Cleanup complete.")
        
        print("\nAll checks passed successfully.")

    except Exception as e:
        print(f"Test FAILED with exception: {e}")

if __name__ == "__main__":
    test_backup_service()
