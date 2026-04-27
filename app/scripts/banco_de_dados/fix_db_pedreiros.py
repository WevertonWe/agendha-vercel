import sqlite3
# Conecta no banco
import os

# Calculate root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, 'agendha.db')

# Conecta no banco
conn = sqlite3.connect(DB_PATH) 
cursor = conn.cursor()

try:
    print("Tentando adicionar coluna pedreiro_id na tabela beneficiarios...")
    cursor.execute("ALTER TABLE beneficiarios ADD COLUMN pedreiro_id INTEGER REFERENCES pedreiros(id)")
    conn.commit()
    print("✅ SUCESSO! Coluna criada.")
except Exception as e:
    print(f"⚠️ Aviso: {e}")
    print("Provavelmente a coluna já existe ou houve outro erro.")

conn.close()
