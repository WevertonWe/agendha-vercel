import sqlite3

DB_PATH = "agendha.db"

def list_abare_no_grh():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, nome_familiar 
            FROM beneficiarios 
            WHERE municipio LIKE '%ABAR%' 
              AND (grh IS NULL OR grh = '')
            LIMIT 5
        """)
        rows = cursor.fetchall()
        
        print("--- Lista de Teste: Beneficiários de Abaré Sem GRH ---")
        for r in rows:
            print(f"ID: {r[0]} | Nome: {r[1]}")
            
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_abare_no_grh()
