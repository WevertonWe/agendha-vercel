import sqlite3
import requests  # noqa: F401

def test_backend_logic():
    try:
        conn = sqlite3.connect('d:/Cursos/agendha/agendha.db')
        cursor = conn.cursor()
        
        print("--- Test 1: List Tecnicos ---")
        cursor.execute("""
            SELECT DISTINCT tecnico_responsavel FROM bsf_metas WHERE tecnico_responsavel IS NOT NULL
            UNION
            SELECT DISTINCT tecnico_id FROM bsf_visitas WHERE tecnico_id IS NOT NULL
            ORDER BY 1
        """)
        tecnicos = [r[0] for r in cursor.fetchall() if r[0]]
        print(f"Tecnicos found: {tecnicos}")
        
        if not tecnicos:
            print("No technicians found.")
            return

        test_tec = tecnicos[0]
        print(f"\n--- Test 2: Filter Metas by Technician '{test_tec}' ---")
        
        # Simulate Global Status Query with Filter
        cursor.execute("SELECT * FROM bsf_metas_contrato WHERE ano = 2026")
        row = cursor.fetchone()
        if row:
            m = dict(zip([c[0] for c in cursor.description], row))
            query = "SELECT COUNT(*) FROM bsf_visitas WHERE atividade_id = ? AND strftime('%Y', data_visita) = '2026' AND tecnico_id = ?"
            cursor.execute(query, (m['atividade_id'], test_tec))
            count = cursor.fetchone()[0]
            print(f"Activity {m['atividade_id']}: Count for {test_tec} = {count}")
        else:
            print("No contract meta found for 2026.")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_backend_logic()
