import psycopg2
import os
import dotenv

dotenv.load_dotenv()
db = os.getenv('SUPABASE_DB_STRING')
conn = psycopg2.connect(db)
conn.autocommit = True
cur = conn.cursor()

sql = """
CREATE TABLE bsf_atividades (
    id SERIAL PRIMARY KEY,
    beneficiario_id INTEGER REFERENCES beneficiarios(id) ON DELETE CASCADE,
    tipo_atividade VARCHAR(255) NOT NULL,
    data_atividade DATE NOT NULL,
    link_sigater JSONB DEFAULT '[]'::jsonb,
    link_colletum JSONB DEFAULT '[]'::jsonb,
    link_ateste JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""
cur.execute(sql)
cur.execute('GRANT ALL ON bsf_atividades TO anon, authenticated, service_role;')
cur.execute('GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;')
cur.execute("NOTIFY pgrst, 'reload schema';")
print('Table created, grants applied, schema reloaded')
