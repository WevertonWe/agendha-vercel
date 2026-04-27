import sqlite3
import logging
from pathlib import Path

# Define DB_PATH directly to avoid dependency on app.config/dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "app" / "agendha.db"

def create_tables():
    """
    Cria as tabelas do módulo Financeiro no banco de dados.
    """
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Conectando ao banco de dados em: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Tabela 'financeiro_entidades'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro_entidades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_pessoa TEXT, -- 'PF' ou 'PJ'
        nome_razao_social TEXT NOT NULL,
        cpf_cnpj TEXT,
        funcao TEXT, -- Ex: Fornecedor, Coordenador
        municipio_atuacao TEXT,
        endereco_rua TEXT,
        endereco_numero TEXT,
        endereco_bairro TEXT,
        endereco_cidade TEXT,
        endereco_cep TEXT,
        contato_telefone TEXT,
        contato_email TEXT,
        dados_bancarios_banco TEXT,
        dados_bancarios_agencia TEXT,
        dados_bancarios_conta TEXT
    )
    """)
    
    # 2. Tabela 'financeiro_projetos'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro_projetos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        numero_contrato TEXT,
        data_inicio TEXT,
        data_fim TEXT,
        valor_total REAL
    )
    """)
    
    # 3. Tabela 'financeiro_metas'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro_metas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projeto_id INTEGER,
        numero_meta TEXT,
        descricao TEXT,
        FOREIGN KEY (projeto_id) REFERENCES financeiro_projetos(id)
    )
    """)
    
    # 4. Tabela 'financeiro_etapas'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro_etapas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meta_id INTEGER,
        numero_etapa TEXT,
        descricao TEXT,
        FOREIGN KEY (meta_id) REFERENCES financeiro_metas(id)
    )
    """)
    
    # 5. Tabela 'financeiro_rubricas'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro_rubricas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etapa_id INTEGER,
        codigo TEXT,
        descricao TEXT,
        unidade TEXT,
        quantidade_programada REAL,
        valor_unitario_programado REAL,
        valor_total_programado REAL,
        FOREIGN KEY (etapa_id) REFERENCES financeiro_etapas(id)
    )
    """)
    
    # 6. Tabela 'financeiro_lancamentos'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro_lancamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projeto_id INTEGER,
        rubrica_id INTEGER,
        entidade_id INTEGER,
        data_lancamento TEXT,
        numero_processo TEXT,
        numero_nota_fiscal TEXT,
        historico TEXT,
        quantidade_executada REAL,
        valor_total_executado REAL,
        FOREIGN KEY (projeto_id) REFERENCES financeiro_projetos(id),
        FOREIGN KEY (rubrica_id) REFERENCES financeiro_rubricas(id),
        FOREIGN KEY (entidade_id) REFERENCES financeiro_entidades(id)
    )
    """)
    
    conn.commit()
    conn.close()
    logging.info("Tabelas do módulo Financeiro criadas com sucesso.")

if __name__ == "__main__":
    create_tables()
