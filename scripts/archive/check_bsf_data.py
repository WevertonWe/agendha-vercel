
import sqlite3
import os

db_path = 'agendha.db'
if not os.path.exists(db_path):
    print(f"Banco de dados não encontrado: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM metas_ater_bsf")
    count = cursor.fetchone()[0]
    print(f"Total de metas na tabela metas_ater_bsf: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM metas_ater_bsf LIMIT 1")
        print("Exemplo de registro:", cursor.fetchone())
        
except Exception as e:
    print(f"Erro ao acessar banco: {e}")
finally:
    if 'conn' in locals():
        conn.close()
