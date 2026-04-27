import sys
import os

# Calculate root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from app.core.database import get_db_connection  # noqa: E402

def test_conn():
    print("Testing get_db_connection...")
    try:
        gen = get_db_connection(None)
        conn = next(gen)
        print("Got connection:", conn)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print("Query result:", cursor.fetchone()[0])
        conn.close() # or next(gen, None) to trigger finally?
        # Manually verify close
        try:
            next(gen)
        except StopIteration:
            pass
        print("Success.")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conn()
