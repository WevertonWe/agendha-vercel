
import sqlite3
import uuid

import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'agendha.db')

def reproduce():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create a test user
    test_username = f"test_tech_{uuid.uuid4().hex[:8]}"
    print(f"Creating test user: {test_username}")
    cursor.execute("""
        INSERT INTO users (username, password_hash, role, is_active, full_name)
        VALUES (?, 'hash_dummy', 'user', 1, 'Test Technician')
    """, (test_username,))
    conn.commit()
    
    # 2. Create a test visit
    print(f"Creating test visit for: {test_username}")
    cursor.execute("""
        INSERT INTO bsf_visitas (tecnico_id, beneficiario_id, municipio, data_visita, status)
        VALUES (?, 'benef_test', 'TestCity', '2025-01-01', 'Realizada')
    """, (test_username,))
    visit_id = cursor.lastrowid
    conn.commit()
    
    print(f"Visit created with ID: {visit_id}")
    
    # 3. Delete the user
    print(f"Deleting user: {test_username}")
    cursor.execute("DELETE FROM users WHERE username = ?", (test_username,))
    conn.commit()
    
    # 4. Check if visit exists
    cursor.execute("SELECT id FROM bsf_visitas WHERE id = ?", (visit_id,))
    row = cursor.fetchone()
    
    if row:
        print("FAIL: Visit STILL EXISTS after user deletion. Cascade not working (as expected).")
    else:
        print("SUCCESS: Visit was DELETED automatically. Cascade is working.")
        
    # Cleanup if still exists
    if row:
        cursor.execute("DELETE FROM bsf_visitas WHERE id = ?", (visit_id,))
        conn.commit()
        print("Cleanup: Deleted test visit.")
        
    conn.close()

if __name__ == "__main__":
    reproduce()
