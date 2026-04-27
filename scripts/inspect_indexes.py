
import sqlite3

import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'agendha.db')
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open('indexes_output.txt', 'w', encoding='utf-8') as f:
        # Get indexes for bsf_visitas
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='bsf_visitas'")
        rows = cursor.fetchall()
        f.write("--- Indexes for bsf_visitas ---\n")
        if rows:
            for row in rows:
                f.write(f"{row[0]}\n")
        else:
            f.write("No indexes found\n")

    print("Indexes dumped to indexes_output.txt")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
