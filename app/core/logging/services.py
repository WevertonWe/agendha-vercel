import sqlite3
from app.config import settings

def insert_log(usuario: str, rota: str, metodo: str, ip_origem: str):
    """
    Insere um registro de log de acesso no banco de dados.
    """
    try:
        conn = sqlite3.connect(settings.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO logs_acesso (usuario, rota, metodo, ip_origem)
            VALUES (?, ?, ?, ?)
        """, (usuario, rota, metodo, ip_origem))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao inserir log de acesso: {e}")
