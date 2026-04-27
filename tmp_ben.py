import sqlite3

conn = sqlite3.connect('agendha.db')
cur = conn.cursor()
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='beneficiarios'")
row = cur.fetchone()
if row:
    print(row[0])
else:
    print("Tabela beneficiarios não encontrada.")
