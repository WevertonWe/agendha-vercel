import os
import sys
import psycopg2
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

db_string = os.getenv("SUPABASE_DB_STRING")
if not db_string:
    print("SUPABASE_DB_STRING not found in .env")
    sys.exit(1)

# Gerar o hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", truncate_error=True)
password = "agendha2024"
hashed_password = pwd_context.hash(password)

print(f"Generated hash length: {len(hashed_password)}")

try:
    conn = psycopg2.connect(db_string)
    cursor = conn.cursor()
    
    # Check if admin exists
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    admin_row = cursor.fetchone()
    
    if admin_row:
        print("Usuário 'admin' já existe. Atualizando senha...")
        cursor.execute("UPDATE users SET password_hash = %s WHERE username = 'admin'", (hashed_password,))
    else:
        print("Usuário 'admin' não existe. Criando...")
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, is_active, full_name)
            VALUES (%s, %s, %s, %s, %s)
        """, ('admin', hashed_password, 'admin', True, 'Administrador do Sistema'))
        
    conn.commit()
    print("Sucesso! O usuário admin foi atualizado diretamente no PostgreSQL, ignorando RLS.")
    
except Exception as e:
    print(f"Erro ao conectar ou executar no PostgreSQL: {e}")
finally:
    if 'conn' in locals() and conn:
        cursor.close()
        conn.close()
