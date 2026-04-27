import sqlite3
import logging
from app.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", truncate_error=True)

def init_db():
    """
    Inicializa o banco de dados, criando as tabelas necessárias se não existirem.
    """
    logging.info(f"Inicializando banco de dados em: {settings.DB_PATH}")
    
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        is_active BOOLEAN NOT NULL DEFAULT 1,
        full_name TEXT
    )
    """)
    
    # Verifica se existe o usuário admin padrão
    cursor.execute("SELECT * FROM users WHERE username = ?", (settings.ADMIN_USERNAME,))
    if not cursor.fetchone():
        logging.info("Criando usuário admin padrão...")
        password_hash = pwd_context.hash(settings.ADMIN_PASSWORD)
        cursor.execute("""
        INSERT INTO users (username, password_hash, role, is_active, full_name)
        VALUES (?, ?, 'admin', 1, 'Administrador do Sistema')
        """, (settings.ADMIN_USERNAME, password_hash))
        conn.commit()
        
    conn.close()
    logging.info("Banco de dados inicializado com sucesso.")

if __name__ == "__main__":
    # Configuração básica de log para quando rodar como script
    logging.basicConfig(level=logging.INFO)
    init_db()
