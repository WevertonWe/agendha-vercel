
import sys
import os
import sqlite3

# Add the project root to the python path
sys.path.append(os.getcwd())

from app.config import settings

def fix_map_owners():
    print("Iniciando correção de donos de pontos no mapa...")
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check count of orphans
        cursor.execute("SELECT COUNT(*) FROM mapa_pontos WHERE responsavel IS NULL OR responsavel = ''")
        count = cursor.fetchone()[0]
        print(f"Encontrados {count} pontos órfãos (sem responsável).")
        
        if count > 0:
            cursor.execute("UPDATE mapa_pontos SET responsavel = 'fgermino' WHERE responsavel IS NULL OR responsavel = ''")
            conn.commit()
            print(f"Sucesso! {cursor.rowcount} pontos foram atualizados para 'fgermino'.")
        else:
            print("Nenhuma correção necessária.")
            
    except Exception as e:
        print(f"Erro ao executar script: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_map_owners()
