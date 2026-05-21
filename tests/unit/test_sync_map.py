
import sys
import sqlite3
import os  # noqa: F401

# Adapt path to project root
sys.path.append('d:/Cursos/agendha')

from app.dependencies import get_db_connection

def _test_sync():
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- 1. Checking Beneficiaries for ABARE/IMPORTADO ---")
    cursor.execute("SELECT count(*) as total FROM beneficiarios WHERE municipio='ABARE' AND status='IMPORTADO' AND latitude IS NOT NULL")
    res = cursor.fetchone()
    total_ben = res['total']
    print(f"Beneficiaries to sync: {total_ben}")
    
    if total_ben == 0:
        print("⚠️ No beneficiaries found to test. Validation limited.")
    
    print("--- 2. Checking Current Map Points (Pre-Sync) ---")
    cursor.execute("SELECT count(*) as total FROM mapa_pontos WHERE tipo='Beneficiário' AND descricao LIKE '%CPF:%'")
    pre_count = cursor.fetchone()['total']
    print(f"Existing Beneficiary Points: {pre_count}")

    # Simulate Sync - We can't call the API function directly easily because of Request object, 
    # so we will replicate the logic OR call it if we can mock Request.
    # Replicating logic is easier for quick verification of the SQL logic.
    
    print("--- 3. Running Sync Logic (Simulation) ---")
    # Query Identical to Routes
    municipio = 'ABARE'
    status = 'IMPORTADO'
    
    cursor.execute("""
            SELECT nome_completo, cpf, comunidade, latitude, longitude 
            FROM beneficiarios 
            WHERE 1=1
            AND UPPER(municipio) = ?
            AND UPPER(status) = ?
            AND latitude IS NOT NULL AND longitude IS NOT NULL
            AND (latitude != 0 OR longitude != 0)
    """, (municipio, status))
    
    beneficiarios = cursor.fetchall()
    synced = 0  # noqa: F841
    duplicates = 0
    
    for b in beneficiarios:
        cpf = b['cpf']
        # Check
        cursor.execute("SELECT id FROM mapa_pontos WHERE tipo = 'Beneficiário' AND descricao LIKE ?", (f"%{cpf}%",))
        if cursor.fetchone():
            duplicates += 1
        else:
            # We won't actually insert in this TEST script to not mess up data if not desired, 
            # BUT the user asked to POPULATE. So I WILL insert if I were the API.
            # Here I just want to see if logic holds. 
            pass # Not inserting in test script to avoid double insertion if I run the UI later. 
                 # Or I should insert one to prove it works?
                 
    print(f"Simulation Result: Would Sync {len(beneficiarios) - duplicates}, Would Skip {duplicates}")

    # Testing Duplication Check specifically
    # Insert a fake point
    TEST_CPF = "999.999.999-99"
    cursor.execute("INSERT INTO mapa_pontos (nome, tipo, cor, descricao, latitude, longitude) VALUES ('TESTE DUPLICIDADE', 'Beneficiário', '#007bff', ?, -8.0, -39.0)", (f"CPF: {TEST_CPF} - Fake",))
    conn.commit()
    point_id = cursor.lastrowid
    print(f"Inserted Test Point ID: {point_id}")  # nosec
    
    # Check if logic finds it
    cursor.execute("SELECT id FROM mapa_pontos WHERE tipo = 'Beneficiário' AND descricao LIKE ?", (f"%{TEST_CPF}%",))
    found = cursor.fetchone()
    
    if found:
        print("✅ Duplication Check Logic: PASSED (Found existing point)")
    else:
        print("❌ Duplication Check Logic: FAILED")
        
    # Cleanup
    cursor.execute("DELETE FROM mapa_pontos WHERE id = ?", (point_id,))
    conn.commit()
    print("Test Point Cleaned Up.")

if __name__ == "__main__":
    _test_sync()
