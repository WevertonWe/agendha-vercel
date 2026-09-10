import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_string = os.getenv("SUPABASE_DB_STRING")

if not db_string:
    print("Erro: SUPABASE_DB_STRING não encontrado.")
    exit(1)

sql = """
CREATE TABLE IF NOT EXISTS bsf_atividades (
    id SERIAL PRIMARY KEY,
    beneficiario_id INTEGER REFERENCES beneficiarios(id) ON DELETE CASCADE,
    tipo_atividade VARCHAR(255) NOT NULL,
    data DATE NOT NULL,
    link_sigater JSONB DEFAULT '[]'::jsonb,
    link_colletum JSONB DEFAULT '[]'::jsonb,
    link_ateste JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

try:
    conn = psycopg2.connect(db_string)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print("Tabela bsf_atividades criada ou já existente.")
except Exception as e:
    print(f"Erro ao criar tabela: {e}")
