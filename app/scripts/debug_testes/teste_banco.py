import sqlite3
import os

# Caminho do banco na raiz
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
caminho = os.path.join(BASE_DIR, "agendha.db")

print(f"--- VERIFICANDO BANCO DE DADOS: {caminho} ---")

if not os.path.exists(caminho):
    print("❌ ERRO: O arquivo agendha.db NÃO existe na pasta raiz!")
else:
    tamanho = os.path.getsize(caminho)
    print(f"📂 Arquivo encontrado. Tamanho: {tamanho / 1024:.2f} KB")
    
    if tamanho == 0:
        print("❌ ERRO CRÍTICO: O arquivo está vazio (0 KB). Copie o banco da pasta app/ novamente!")
    else:
        try:
            conn = sqlite3.connect(caminho)
            cursor = conn.cursor()
            
            # Tenta listar as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas = cursor.fetchall()
            print(f"📋 Tabelas encontradas: {[t[0] for t in tabelas]}")
            
            if 'users' in [t[0] for t in tabelas]:
                cursor.execute("SELECT username, password_hash FROM users")
                usuarios = cursor.fetchall()
                print("\n👤 USUÁRIOS ENCONTRADOS:")
                for u in usuarios:
                    print(f" - {u[0]} (Hash começa com: {u[1][:10]}...)")
            else:
                print("❌ ERRO: A tabela 'users' não existe neste arquivo!")
                
            conn.close()
        except Exception as e:
            print(f"❌ Erro ao ler o banco: {e}")

input("\nPressione ENTER para sair...")
