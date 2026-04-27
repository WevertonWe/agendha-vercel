import sqlite3
import logging

# Configuração para vermos mensagens claras no terminal
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Aponta para a base de dados correta
NOME_BANCO_DE_DADOS = "app/agendha.db"


def criar_tabela_validacao_pendente():
    """Cria a tabela 'validacao_pendente' se ela não existir."""
    conexao = None
    try:
        logging.info(
            f"Conectando ao banco de dados '{NOME_BANCO_DE_DADOS}'...")
        conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
        cursor = conexao.cursor()

        logging.info(
            "Verificando a existência da tabela 'validacao_pendente'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validacao_pendente (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_drive_file_id TEXT UNIQUE NOT NULL,
                nome_arquivo TEXT,
                caminho_arquivo_local TEXT,
                dados_extraidos_json TEXT,
                status TEXT NOT NULL DEFAULT 'PENDENTE',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conexao.commit()
        logging.info(
            "✅ Tabela 'validacao_pendente' verificada/criada com sucesso!")

    except sqlite3.Error as e:
        logging.error(
            f"❌ Ocorreu um erro ao interagir com a base de dados: {e}")
    finally:
        if conexao:
            conexao.close()
            logging.info("Conexão com o banco de dados fechada.")


if __name__ == "__main__":
    criar_tabela_validacao_pendente()
