import sqlite3
from app.config import settings

def update_map_schema():
    try:
        conn = sqlite3.connect(settings.DB_PATH)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(mapa_pontos)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'poligono' not in columns:
            print("Adicionando coluna 'poligono'...")
            cursor.execute("ALTER TABLE mapa_pontos ADD COLUMN poligono TEXT")
            conn.commit()
            print("Coluna adicionada com sucesso.")
        else:
            print("Coluna 'poligono' já existe.")
            
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar schema: {e}")

if __name__ == "__main__":
    update_map_schema()
