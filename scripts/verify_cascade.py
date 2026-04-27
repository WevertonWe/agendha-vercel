
import sqlite3
import uuid
import logging
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def verify():
    db_path = settings.DB_PATH
    logging.info(f"Connecting to database at {db_path}...")
    
    conn = sqlite3.connect(db_path)
    # CRITICAL: Enable foreign keys support for the test
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    try:
        # 1. Create a test user
        test_username = f"test_cascade_{uuid.uuid4().hex[:8]}"
        logging.info(f"Creating test user: {test_username}")
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, is_active, full_name)
            VALUES (?, 'hash_dummy', 'user', 1, 'Cascade Tester')
        """, (test_username,))
        conn.commit()
        
        # 2. Create a test visit
        logging.info(f"Creating test visit for: {test_username}")
        cursor.execute("""
            INSERT INTO bsf_visitas (tecnico_id, beneficiario_id, municipio, data_visita, status)
            VALUES (?, 'benef_test_cascade', 'TestCity', '2025-01-01', 'Realizada')
        """, (test_username,))
        visit_id = cursor.lastrowid
        conn.commit()
        
        logging.info(f"Visit created with ID: {visit_id}")
        
        # 3. Delete the user
        logging.info(f"Deleting user: {test_username}")
        cursor.execute("DELETE FROM users WHERE username = ?", (test_username,))
        conn.commit()
        
        # 4. Check if visit exists
        # We need to query simply.
        cursor.execute("SELECT id FROM bsf_visitas WHERE id = ?", (visit_id,))
        row = cursor.fetchone()
        
        if row:
            logging.error("FAIL: Visit STILL EXISTS after user deletion. Cascade NOT working.")
            # Cleanup
            cursor.execute("DELETE FROM bsf_visitas WHERE id = ?", (visit_id,))
            conn.commit()
            exit(1)
        else:
            logging.info("SUCCESS: Visit was DELETED automatically. Cascade IS working.")
            
    except Exception as e:
        logging.error(f"Test failed with error: {e}")
        conn.rollback()
        exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    verify()
