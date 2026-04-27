
import sqlite3
import os

DB_PATH = r"c:\Wev Dev\projetos\agendha\agendha.db"

def clean_visitas():
    if not os.path.exists(DB_PATH):
        print(f"ERRO: Banco não encontrado em {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar contagem antes
        cursor.execute("SELECT COUNT(*) FROM bsf_visitas")
        count_before = cursor.fetchone()[0]
        print(f"Visitas ANTES da limpeza: {count_before}")
        
        if count_before == 0:
            print("Nenhuma visita para limpar.")
        else:
            # Executar Limpeza
            cursor.execute("DELETE FROM bsf_visitas")
            deleted = cursor.rowcount
            conn.commit()
            print(f"SUCESSO: {deleted} visitas excluídas.")
            
            # Verificar contagem depois
            cursor.execute("SELECT COUNT(*) FROM bsf_visitas")
            count_after = cursor.fetchone()[0]
            print(f"Visitas DEPOIS da limpeza: {count_after}")
            
    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    clean_visitas()
