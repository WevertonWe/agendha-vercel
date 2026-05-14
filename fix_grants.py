import psycopg2
import os
import dotenv

dotenv.load_dotenv()
db = os.getenv('SUPABASE_DB_STRING')
conn = psycopg2.connect(db)
conn.autocommit = True
cur = conn.cursor()
cur.execute('GRANT ALL ON bsf_atividades TO anon, authenticated, service_role;')
cur.execute('GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;')
cur.execute("NOTIFY pgrst, 'reload schema';")
print('Grants done and schema reloaded')
