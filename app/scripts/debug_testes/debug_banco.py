import sqlite3
import os

# Caminho absoluto da raiz baseado neste arquivo
# Caminho absoluto da raiz baseado neste arquivo (scripts está em app/scripts/debug_testes, então subir 3 niveis)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "agendha.db")

print(f"\n📍 O script está rodando em: {BASE_DIR}")
print(f"🎯 O banco alvo é: {DB_PATH}")

if os.path.exists(DB_PATH):
    print(f"✅ Arquivo encontrado! Tamanho: {os.path.getsize(DB_PATH)/1024:.2f} KB")
else:
    print("❌ ARQUIVO NÃO ENCONTRADO! Criando um novo agora...")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # FORÇA A CRIAÇÃO DAS TABELAS FINANCEIRAS AQUI E AGORA
    print("🔨 Verificando/Criando tabelas financeiras...")
    
    tab_projetos = """
    CREATE TABLE IF NOT EXISTS financeiro_projetos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        orcamento_total REAL DEFAULT 0.0,
        data_inicio TEXT,
        data_fim TEXT,
        status TEXT DEFAULT 'Ativo'
    )
    """
    cursor.execute(tab_projetos)
    
    # Check
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='financeiro_projetos';")
    if cursor.fetchone():
        print("✅ Tabela 'financeiro_projetos' EXISTE.")
    else:
        print("❌ FALHA AO CRIAR 'financeiro_projetos'.")

    # Lista todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print("\n📋 Lista Final de Tabelas no Banco:")
    print(tables)
    
    conn.commit()
    conn.close()

except Exception as e:
    print(f"\n💥 ERRO CRÍTICO: {e}")

input("\nPressione ENTER para sair...")
