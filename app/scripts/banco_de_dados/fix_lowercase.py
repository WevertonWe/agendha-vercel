
import sys
import os
import sqlite3

# Add the project root to the python path
sys.path.append(os.getcwd())

from app.config import settings

def fix_lowercase_responsavel():
    print("Normalizando 'responsavel' para minúsculas...")
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE mapa_pontos SET responsavel = LOWER(responsavel) WHERE responsavel IS NOT NULL")
        row_count = cursor.rowcount
        conn.commit()
        print(f"Sucesso! {row_count} registros atualizados.")
            
    except Exception as e:
        print(f"Erro ao executar script: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_lowercase_responsavel()
