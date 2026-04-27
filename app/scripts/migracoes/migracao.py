import sqlite3
import logging

# Configuração para vermos mensagens claras no terminal
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Aponta para a base de dados correta, dentro da pasta 'app'
NOME_BANCO_DE_DADOS = "app/agendha.db"


def adicionar_coluna_se_nao_existir(cursor, nome_tabela, nome_coluna, tipo_coluna):
    """Verifica se uma coluna existe e, se não, a adiciona."""
    try:
        # Tenta adicionar a coluna
        cursor.execute(
            f"ALTER TABLE {nome_tabela} ADD COLUMN {nome_coluna} {tipo_coluna}")
        logging.info(
            f"Coluna '{nome_coluna}' adicionada à tabela '{nome_tabela}'.")
    except sqlite3.OperationalError as e:
        # Se o erro for "duplicate column name", significa que já fizemos o nosso trabalho.
        if "duplicate column name" in str(e).lower():
            logging.warning(
                f"Coluna '{nome_coluna}' já existe. Nenhuma ação foi tomada.")
        else:
            # Se for outro erro, mostra-o
            raise e


def executar_migracao():
    """Adiciona as novas colunas necessárias à tabela de beneficiarios."""
    conexao = None
    try:
        logging.info(
            f"Conectando ao banco de dados '{NOME_BANCO_DE_DADOS}' para migração...")
        conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
        cursor = conexao.cursor()

        logging.info(
            "Iniciando a adição de novas colunas à tabela 'beneficiarios'...")

        adicionar_coluna_se_nao_existir(
            cursor, "beneficiarios", "sexo", "TEXT")
        adicionar_coluna_se_nao_existir(
            cursor, "beneficiarios", "data_nascimento", "TEXT")
        adicionar_coluna_se_nao_existir(
            cursor, "beneficiarios", "escolaridade", "TEXT")
        adicionar_coluna_se_nao_existir(
            cursor, "beneficiarios", "ref_localizacao", "TEXT")
        adicionar_coluna_se_nao_existir(
            cursor, "beneficiarios", "estado_uf", "TEXT")

        conexao.commit()
        logging.info("✅ Migração concluída com sucesso!")

    except sqlite3.Error as e:
        logging.error(f"❌ Ocorreu um erro durante a migração: {e}")
    finally:
        if conexao:
            conexao.close()
            logging.info("Conexão com o banco de dados fechada.")


if __name__ == "__main__":
    executar_migracao()
