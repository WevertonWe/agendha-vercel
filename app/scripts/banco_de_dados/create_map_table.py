import sqlite3
from app.config import settings

def create_map_table():
    try:
        conn = sqlite3.connect(settings.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mapa_pontos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            descricao TEXT,
            projeto_id INTEGER
        )
        """)
        
        conn.commit()
        conn.close()
        print("Tabela mapa_pontos criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tabela mapa_pontos: {e}")

if __name__ == "__main__":
    create_map_table()
