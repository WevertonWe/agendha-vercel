import sqlite3
con = sqlite3.connect('agendha.db')
cursor = con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for t in tables:
    print(f"Table: {t[0]}")
    c2 = con.cursor()
    c2.execute(f"PRAGMA table_info({t[0]})")
    cols = c2.fetchall()
    for c in cols:
        print(f"  {c[1]} - {c[2]}")
