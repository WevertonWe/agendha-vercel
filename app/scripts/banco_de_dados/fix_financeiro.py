import sqlite3
import os

# Força o caminho exato onde você está rodando o terminal
# Força o caminho exato onde você está rodando o terminal
# Assuming script is run from app/scripts/banco_de_dados
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "agendha.db")

print(f"🔧 Conectando ao banco de dados em: {DB_PATH}")

if not os.path.exists(DB_PATH):
    print("❌ ERRO: O arquivo agendha.db não foi encontrado na raiz!")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Cria Tabela PROJETOS
        print("🔨 Criando tabela: financeiro_projetos...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financeiro_projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            orcamento_total REAL DEFAULT 0.0,
            data_inicio TEXT,
            data_fim TEXT,
            status TEXT DEFAULT 'Ativo'
        )
        """)

        # 2. Cria Tabela RUBRICAS
        print("🔨 Criando tabela: financeiro_rubricas...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financeiro_rubricas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER NOT NULL,
            codigo TEXT,
            nome TEXT NOT NULL,
            tipo TEXT, 
            orcamento_previsto REAL DEFAULT 0.0,
            FOREIGN KEY (projeto_id) REFERENCES financeiro_projetos (id)
        )
        """)

        # 3. Cria Tabela LANÇAMENTOS
        print("🔨 Criando tabela: financeiro_lancamentos...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financeiro_lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER NOT NULL,
            rubrica_id INTEGER,
            data_lancamento TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL, 
            status TEXT DEFAULT 'Pendente',
            comprovante_url TEXT,
            FOREIGN KEY (projeto_id) REFERENCES financeiro_projetos (id),
            FOREIGN KEY (rubrica_id) REFERENCES financeiro_rubricas (id)
        )
        """)

        conn.commit()
        conn.close()
        print("\n✅ SUCESSO! As tabelas financeiras foram criadas.")
        print("🚀 Pode reiniciar o servidor agora.")
    
    except Exception as e:
        print(f"\n❌ Erro ao criar tabelas: {e}")

input("\nPressione ENTER para sair...")
