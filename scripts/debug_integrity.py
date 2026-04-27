
import sqlite3
from app.config import settings

def check_integrity():
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    
    print("--- Checking Integrity ---")
    
    # 1. Check Orphan Tecnicos
    print("\nChecking for orphan Visit records (Invalid tecnico_id)...")
    cursor.execute("""
        SELECT v.id, v.tecnico_id 
        FROM bsf_visitas v 
        LEFT JOIN users u ON v.tecnico_id = u.username 
        WHERE u.username IS NULL
    """)
    orphans_tech = cursor.fetchall()
    if orphans_tech:
        print(f"FOUND {len(orphans_tech)} visits with invalid tecnico_id:")
        for row in orphans_tech:
            print(f"  Visit ID: {row[0]}, Tecnico: {row[1]}")
    else:
        print("OK: No orphan visits regarding tecnico_id.")

    # 2. Check Orphan Atividades
    print("\nChecking for orphan Visit records (Invalid atividade_id)...")
    # First check if bsf_atividades exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bsf_atividades'")
    if not cursor.fetchone():
        print("WARNING: Table 'bsf_atividades' does not exist! FK validation will fail if strictly enforced against it.")
    else:
        cursor.execute("""
            SELECT v.id, v.atividade_id 
            FROM bsf_visitas v 
            LEFT JOIN bsf_atividades a ON v.atividade_id = a.id 
            WHERE v.atividade_id IS NOT NULL AND a.id IS NULL
        """)
        orphans_activity = cursor.fetchall()
        if orphans_activity:
            print(f"FOUND {len(orphans_activity)} visits with invalid atividade_id:")
            for row in orphans_activity:
                print(f"  Visit ID: {row[0]}, Atividade ID: {row[1]}")
        else:
            print("OK: No orphan visits regarding atividade_id.")

    conn.close()

if __name__ == "__main__":
    check_integrity()
