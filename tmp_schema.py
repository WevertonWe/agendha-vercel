import sqlite3

conn = sqlite3.connect('agendha.db')
cur = conn.cursor()
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'bsf_%'")
tables = cur.fetchall()

print("## Tabelas Encontradas\\n")
for name, sql in tables:
    print(f"### {name}")
    print("```sql")
    print(f"{sql}")
    print("```\\n")
