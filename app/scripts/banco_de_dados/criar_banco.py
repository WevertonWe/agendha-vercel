import sqlite3

# --- CONFIGURAÇÕES ---
# MUDANÇA: Especificamos a pasta 'app/' para garantir que o ficheiro certo seja sempre usado.
NOME_BANCO_DE_DADOS = "app/agendha.db"


def criar_estruturas_db():
    """
    Verifica e cria as tabelas necessárias no banco de dados
    sem apagar os dados existentes.
    """
    conexao = None
    try:
        print(f"Conectando ao banco de dados '{NOME_BANCO_DE_DADOS}'...")
        conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
        cursor = conexao.cursor()
        print("Conexão bem-sucedida.")

        # --- Tabela de Beneficiários (JÁ ATUALIZADA POR VOCÊ, ÓTIMO!) ---
        print("Verificando a tabela 'beneficiarios'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS beneficiarios (
                codigo INTEGER PRIMARY KEY,
                nome_tecnico TEXT,
                cpf_tecnico TEXT,
                municipio TEXT,
                comunidade TEXT,
                latitude REAL,
                longitude REAL,
                data_atividade TEXT,
                nome_familiar TEXT,
                cpf_familiar TEXT,
                nis TEXT,
                renda_media REAL,
                status TEXT,
                tecnico_agua_que_alimenta TEXT,
                doc_status TEXT,
                grh TEXT,
                verificado_bsf TEXT,
                sexo TEXT,
                data_nascimento TEXT,
                escolaridade TEXT,
                ref_localizacao TEXT,
                estado_uf TEXT
            );
        """)
        print("Tabela 'beneficiarios' verificada/criada com sucesso!")

        # --- Outras Tabelas (sem alterações) ---
        print("Verificando a tabela 'eventos_grh'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eventos_grh (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                municipio_comunidade TEXT NOT NULL,
                dia_previsto TEXT NOT NULL,
                realizado BOOLEAN NOT NULL DEFAULT 0,
                observacao TEXT,
                link_formulario TEXT
            );
        """)
        print("Tabela 'eventos_grh' verificada/criada com sucesso!")

        print("Verificando a tabela 'cotacoes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cotacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_fornecedor TEXT NOT NULL, tipo_fornecedor TEXT,
                data_contrato TEXT, valor REAL, status TEXT,
                caminho_arquivo TEXT, observacao TEXT
            );
        """)
        print("Tabela 'cotacoes' verificada/criada com sucesso!")

        print("Verificando a tabela 'documentos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_documento TEXT NOT NULL,
                descricao TEXT,
                nome_arquivo TEXT NOT NULL,
                caminho_arquivo TEXT NOT NULL,
                data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Tabela 'documentos' verificada/criada com sucesso!")

        print("Verificando a tabela 'cronograma'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cronograma (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarefa TEXT NOT NULL,
                data_prevista TEXT NOT NULL,
                data_realizada TEXT,
                status TEXT NOT NULL DEFAULT 'Pendente',
                responsavel TEXT,
                observacao TEXT
            );
        """)
        print("Tabela 'cronograma' verificada/criada com sucesso!")

        conexao.commit()
        print("\n✅ Estrutura do banco de dados verificada e atualizada.")

    except sqlite3.Error as e:
        print(f"❌ Ocorreu um erro ao interagir com o banco de dados: {e}")
    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")


if __name__ == "__main__":
    criar_estruturas_db()
