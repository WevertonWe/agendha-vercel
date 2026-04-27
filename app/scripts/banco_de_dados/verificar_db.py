import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
db_path = os.path.join(BASE_DIR, "agendha.db")

if not os.path.exists(db_path):
    print(f"❌ ERRO: O arquivo {db_path} não foi encontrado na raiz!")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Lista todas as tabelas existentes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()
    
    print(f"📂 Conectado em: {os.path.abspath(db_path)}")
    print(f"📊 Tabelas encontradas: {[t[0] for t in tabelas]}")
    
    if len(tabelas) == 0:
        print("⚠️ ALERTA: O banco está vazio! Precisamos rodar a migração.")
    
    conn.close()
