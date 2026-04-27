import sqlite3
import os
import sys
from passlib.context import CryptContext

# Ajusta o path para reconhecer a pasta 'app'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from app.config import settings  # noqa: E402

# Configuração de segurança igual ao seu db_init.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", truncate_error=True)

def testar_login():
    print("--- Iniciando Teste de Acesso ---")
    print(f"Alvo: {settings.DB_PATH}")
    
    if not os.path.exists(settings.DB_PATH):
        print("❌ ERRO: Banco de dados não encontrado na raiz!")
        return

    try:
        conn = sqlite3.connect(settings.DB_PATH)
        conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome
        cursor = conn.cursor()
        
        # 1. Busca o usuário
        username_alvo = "admin" 
        cursor.execute("SELECT * FROM users WHERE username = ?", (username_alvo,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Usuário '{username_alvo}' não existe na tabela 'users'.")
            return

        print(f"✅ Usuário '{user['username']}' localizado.")
        print(f"Hash no banco: {user['password_hash'][:20]}...")

        # 2. Verifica a senha
        # Tente a senha que você definiu no config ou .env
        senha_para_testar = "segredo123" # Tente a senha padrão do seu config.py
        
        try:
            print(f"Testando senha: {senha_para_testar}")
            valido = pwd_context.verify(senha_para_testar, user['password_hash'])
            if valido:
                print("✨ SUCESSO: Senha validada com sucesso!")
            else:
                print("🚫 SENHA INCORRETA: O hash não corresponde a essa senha.")
        except Exception as e:
            print(f"💥 Erro ao processar Bcrypt: {e}")

    except Exception as e:
        print(f"💥 Erro de SQL: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    testar_login()