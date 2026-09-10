import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_string = os.getenv("SUPABASE_DB_STRING")

if not db_string:
    print("Erro: SUPABASE_DB_STRING não encontrado nas variáveis de ambiente.")
    exit(1)

sql = """
-- 1. Adicionar codigo_plano na tabela beneficiarios
ALTER TABLE beneficiarios ADD COLUMN IF NOT EXISTS codigo_plano TEXT;

-- 2. Adicionar iniciativas_vinculadas na tabela bsf_atividades
ALTER TABLE bsf_atividades ADD COLUMN IF NOT EXISTS iniciativas_vinculadas JSONB DEFAULT '[]'::jsonb;

-- 3. Criar a tabela bsf_metas_plano
CREATE TABLE IF NOT EXISTS bsf_metas_plano (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    beneficiario_id BIGINT REFERENCES beneficiarios(id) ON DELETE CASCADE,
    codigo TEXT,
    tipo TEXT,
    descricao TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Garantir grants gerais para acesso sem bloqueio RLS na nova tabela
GRANT ALL ON TABLE bsf_metas_plano TO anon, authenticated, service_role;
"""

try:
    print("Conectando ao banco de dados Supabase...")
    conn = psycopg2.connect(db_string)
    cur = conn.cursor()
    print("Executando DDL de migração para o Plano Produtivo...")
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print("[SUCESSO] Migração aplicada com sucesso!")
except Exception as e:
    print(f"[ERRO] Falha ao aplicar migração: {e}")
    exit(1)
