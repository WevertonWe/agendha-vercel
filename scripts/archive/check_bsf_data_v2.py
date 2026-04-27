
import sqlite3
import os

db_path = 'agendha.db'
if not os.path.exists(db_path):
    print(f"Banco de dados não encontrado: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Usando o nome correto da tabela conforme visto em metas.py
    cursor.execute("SELECT count(*) FROM bsf_metas")
    count = cursor.fetchone()[0]
    print(f"Total de metas na tabela bsf_metas: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM bsf_metas LIMIT 1")
        print("Exemplo de registro:", cursor.fetchone())
    else:
        print("Tabela bsf_metas está vazia.")
        
except Exception as e:
    print(f"Erro ao acessar banco: {e}")
finally:
    if 'conn' in locals():
        conn.close()
