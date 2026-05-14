import psycopg2
import os
import dotenv

dotenv.load_dotenv()
db = os.getenv('SUPABASE_DB_STRING')
conn = psycopg2.connect(db)
conn.autocommit = True
conn.cursor().execute("NOTIFY pgrst, 'reload schema';")
print('Reloaded schema cache')
