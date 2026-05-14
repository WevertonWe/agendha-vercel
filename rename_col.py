import psycopg2
import os
import dotenv

dotenv.load_dotenv()
db = os.getenv('SUPABASE_DB_STRING')
conn = psycopg2.connect(db)
conn.autocommit = True
cur = conn.cursor()
cur.execute('ALTER TABLE bsf_atividades RENAME COLUMN data TO data_atividade;')
cur.execute("NOTIFY pgrst, 'reload schema';")
print('Renamed and reloaded')
