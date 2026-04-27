import sqlite3
import os

BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, "agendha.db")

print(f"Executando migração no DB: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS faturamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedreiro_id INTEGER NOT NULL,
    valor_total REAL DEFAULT 0.0,
    valor_dam REAL DEFAULT 0.0,
    status_dam TEXT DEFAULT 'Pendente',
    arquivo_nf TEXT,
    arquivo_dam TEXT,
    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pedreiro_id) REFERENCES pedreiros(id)
)
""")
print("Tabela faturamentos garantida.")

try:
    cursor.execute("ALTER TABLE beneficiarios ADD COLUMN faturamento_id INTEGER REFERENCES faturamentos(id)")
    print("Coluna faturamento_id adicionada em beneficiarios.")
except sqlite3.OperationalError as e:
    print(f"Ignorando add column: {e}")

conn.commit()
conn.close()
print("Migração concluída.")
