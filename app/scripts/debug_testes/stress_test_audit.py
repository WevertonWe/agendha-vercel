import sqlite3
import time
import json
import os
import random
import logging
import sys

# Calculate root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from app.services.backup_service import create_snapshot  # noqa: E402
from app.services.audit_service import log_change  # noqa: E402

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(BASE_DIR, 'agendha.db')
NUM_RECORDS = 500

def get_db():
    return sqlite3.connect(DB_PATH)

def setup_data(conn):
    """Creates 500 dummy beneficiaries."""
    logger.info(f"Creating {NUM_RECORDS} dummy beneficiaries...")
    cursor = conn.cursor()
    
    # Ensure table exists (simplified schema for test if not exists, but likely exists)
    # in a real scenario we assume table exists.
    
    ids = []
    for i in range(NUM_RECORDS):
        nome = f"Test User {i} {random.randint(1000, 9999)}"
        cpf = f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"
        cursor.execute("INSERT INTO beneficiarios (nome_familiar, cpf_familiar, grh) VALUES (?, ?, ?)", (nome, cpf, "OLD_GRH"))
        ids.append(cursor.lastrowid)
    
    conn.commit()
    logger.info("Data creation complete.")
    return ids

def simulate_grh_update(conn, ids, new_grh_term):
    """Simulates the bulk update with snapshot and audit."""
    logger.info("Starting Bulk Update Simulation...")
    
    # 1. Measure Snapshot Time
    start_snap = time.time()
    try:
        snap_path = create_snapshot(reason=f"stress_test_{new_grh_term}")
        snap_duration = time.time() - start_snap
        logger.info(f"Snapshot created in {snap_duration:.4f}s at {snap_path}")
    except Exception as e:
        logger.error(f"Snapshot failed: {e}")
        return False

    # 2. Perform Updates
    cursor = conn.cursor()
    updates_count = 0
    start_update = time.time()
    
    try:
        conn.execute("BEGIN TRANSACTION")
        
        for p_id in ids:
            # Fetch old
            cursor.execute("SELECT id, grh FROM beneficiarios WHERE id = ?", (p_id,))
            row = cursor.fetchone()
            if row:
                old_val = {"grh": row[1]} # index 1 is grh
                
                # Update
                cursor.execute("UPDATE beneficiarios SET grh = ? WHERE id = ?", (new_grh_term, p_id))
                
                # Log
                new_val = {"grh": new_grh_term}
                log_change(
                    db=conn,
                    tabela="beneficiarios",
                    registro_id=p_id,
                    operacao="UPDATE",
                    valor_antigo=old_val,
                    valor_novo=new_val,
                    detalhes=f"Stress Test GRH: {new_grh_term}"
                )
                updates_count += 1
        
        conn.commit()
        update_duration = time.time() - start_update
        logger.info(f"Updates completed in {update_duration:.4f}s directly. Avg: {update_duration/len(ids):.4f}s/record")  # nosec
        
    except sqlite3.OperationalError as e:
        logger.error(f"Database Locked Error: {e}")
        conn.rollback()
        return False
    except Exception as e:
        logger.error(f"Update failed: {e}")  # nosec
        conn.rollback()
        return False
        
    return True

def verify_audit_integrity(conn, ids, expected_grh):
    """Verifies if audit logs exist and data is correct."""
    logger.info("Verifying Data and Audit integrity...")
    cursor = conn.cursor()
    
    # Check current data
    cursor.execute(f"SELECT COUNT(*) FROM beneficiarios WHERE grh = ? AND id IN ({','.join(['?']*len(ids))})", (expected_grh, *ids))  # nosec
    count_data = cursor.fetchone()[0]
    if count_data != len(ids):
        logger.error(f"Data Mismatch! Expected {len(ids)} records with GRH {expected_grh}, found {count_data}")
    else:
        logger.info(f"Data verification PASS: All {count_data} records updated.")

    # Check Audit Logs
    # We fetch the latest logs for these IDs
    placeholders = ','.join(['?']*len(ids))
    cursor.execute(f"SELECT COUNT(*) FROM audit_logs WHERE registro_id IN ({placeholders}) AND valor_novo LIKE ?", (*ids, f'%{expected_grh}%'))  # nosec
    # Note: 'novo_valor' column name in schema might be 'valor_novo'. Checking create_audit_table.py... it is 'valor_novo'.
    # And we need to match the json string.
    
    # Let's fix the query to be looser on JSON or precise if we know the structure
    # We'll just count logs created in the last minute matching the operation
    cursor.execute(f"""
        SELECT COUNT(*) FROM audit_logs 
        WHERE tabela='beneficiarios' 
        AND operacao='UPDATE' 
        AND detalhes LIKE 'Stress Test GRH%'
        AND registro_id IN ({placeholders})
    """, ids)
    
    count_logs = cursor.fetchone()[0]
    if count_logs != len(ids):
        logger.error(f"Audit Log Mismatch! Expected {len(ids)} logs, found {count_logs}")
    else:
        logger.info(f"Audit verification PASS: Found {count_logs} log entries.")

def test_rollback(conn, ids):
    """Simulates a rollback using audit logs."""
    logger.info("Testing Manual Rollback via Audit Logs...")
    cursor = conn.cursor()
    start_rollback = time.time()
    
    try:
        conn.execute("BEGIN TRANSACTION")
        restored_count = 0
        
        for p_id in ids:
            # Find the last log for this ID
            cursor.execute("""
                SELECT valor_antigo FROM audit_logs 
                WHERE registro_id = ? AND tabela = 'beneficiarios' AND operacao = 'UPDATE'
                ORDER BY id DESC LIMIT 1
            """, (p_id,))
            row = cursor.fetchone()
            
            if row:
                val_antigo = json.loads(row[0])
                prev_grh = val_antigo.get('grh')
                
                cursor.execute("UPDATE beneficiarios SET grh = ? WHERE id = ?", (prev_grh, p_id))
                restored_count += 1
        
        conn.commit()
        rollback_duration = time.time() - start_rollback
        
        logger.info(f"Rollback finished in {rollback_duration:.4f}s. Restored {restored_count}/{len(ids)} records.")
        
        # Verify restoration
        cursor.execute(f"SELECT COUNT(*) FROM beneficiarios WHERE grh = 'OLD_GRH' AND id IN ({','.join(['?']*len(ids))})", ids)  # nosec
        cnt = cursor.fetchone()[0]
        if cnt == len(ids):
            logger.info("Rollback Validation PASS: All records restored to 'OLD_GRH'.")
        else:
            logger.error(f"Rollback Validation FAIL: Only {cnt} records restored.")
            
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        conn.rollback()

def cleanup(conn, ids):
    logger.info("Cleaning up test data...")
    placeholders = ','.join(['?']*len(ids))
    conn.execute(f"DELETE FROM beneficiarios WHERE id IN ({placeholders})", ids)  # nosec
    # Optionally clean logs too
    conn.execute(f"DELETE FROM audit_logs WHERE registro_id IN ({placeholders})", ids)  # nosec
    conn.commit()
    logger.info("Cleanup complete.")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        logger.error(f"Database {DB_PATH} not found.")
        exit(1)
        
    conn = get_db()
    
    try:
        # 1. Create Data
        test_ids = setup_data(conn)
        
        # 2. Simulate Update
        NEW_GRH = "STRESS_TEST_2024"
        success = simulate_grh_update(conn, test_ids, NEW_GRH)
        
        if success:
            # 3. Verify
            verify_audit_integrity(conn, test_ids, NEW_GRH)
            
            # 4. Rollback
            test_rollback(conn, test_ids)
            
    except Exception as e:
        logger.error(f"Critical Test Failure: {e}")
    finally:
        cleanup(conn, test_ids)
        conn.close()
