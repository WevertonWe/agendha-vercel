import sqlite3
from app.config import settings

def create_logs_table():
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_acesso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        usuario TEXT,
        rota TEXT,
        metodo TEXT,
        ip_origem TEXT
    )
    """)
    
    conn.commit()
    conn.close()
    print("Tabela logs_acesso criada com sucesso.")

if __name__ == "__main__":
    create_logs_table()
