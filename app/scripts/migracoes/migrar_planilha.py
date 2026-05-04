import pandas as pd
import sqlite3
import re

# --- CONFIGURAções ---
URL_PLANILHA_CSV = (
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vSiQIEwGylO5gmBzjWkorP6q'
    'OmUi5aRDssw9e18DCDA_UD3nurXqwcKGn9g5b4BAGr87_sY6vj04Zc7/pub?gid=12094'
    '02383&single=true&output=csv'
)
NOME_BANCO_DE_DADOS = "app/agendha.db"
NOME_TABELA = "beneficiarios"

def criar_tabela_beneficiarios(cursor):
    """Cria a tabela de beneficiários com a chave primária 'id' e todas as outras colunas."""
    print(f"A verificar e a criar a tabela '{NOME_TABELA}' com a estrutura correta...")
    cursor.execute(f"DROP TABLE IF EXISTS {NOME_TABELA}")
    cursor.execute(f"""
    CREATE TABLE {NOME_TABELA} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT, nome_tecnico TEXT, cpf_tecnico TEXT, municipio TEXT,
        comunidade TEXT, latitude TEXT, longitude TEXT, data_atividade TEXT,
        nome_familiar TEXT, cpf_familiar TEXT, nis TEXT, renda_media TEXT,
        status TEXT, tecnico_agua_que_alimenta TEXT, doc_status TEXT, grh TEXT,
        verificado_bsf TEXT, nome_completo TEXT, sexo TEXT, data_nascimento TEXT,
        cpf TEXT, escolaridade TEXT, ref_localizacao TEXT
    );
    """)
    print(f"✅ Tabela '{NOME_TABELA}' criada com sucesso com a coluna 'id'.")

def limpar_cpf(cpf_bruto):
    """Remove todos os caracteres não numéricos de um CPF."""
    if not cpf_bruto or pd.isna(cpf_bruto):
        return None
    return re.sub(r'\D', '', str(cpf_bruto))

def migrar_dados():
    """Lê a planilha, cria a tabela, limpa os dados e insere no banco de dados SQLite."""
    conexao = None
    try:
        print(f"Conectando ao banco de dados '{NOME_BANCO_DE_DADOS}'...")
        conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
        cursor = conexao.cursor()
        criar_tabela_beneficiarios(cursor)
        conexao.commit()
        
        print("\nLendo dados da planilha...")
        df = pd.read_csv(URL_PLANILHA_CSV, dtype=str).fillna('')
        print("Leitura da planilha concluída.")

        print("Iniciando limpeza e preparação dos dados...")
        mapeamento_colunas = {
            'Código': 'codigo', 'Nome Técnico': 'nome_tecnico',
            'CPF Técnico': 'cpf_tecnico', 'Município': 'municipio',
            'Comunidade': 'comunidade', 'Latitude': 'latitude',
            'Longitude': 'longitude', 'Data Atividade': 'data_atividade',
            'Nome Familiar': 'nome_familiar', 'CPF Familiar': 'cpf_familiar',
            'NIS': 'nis', 'Renda Média': 'renda_media', 'Status': 'status',
            'Técnico Água que Alimenta': 'tecnico_agua_que_alimenta',
            'Doc. Status': 'doc_status', 'GRH': 'grh',
            'Verificado no BSF?': 'verificado_bsf'
        }
        df.rename(columns=mapeamento_colunas, inplace=True)
        df['cpf_tecnico'] = df['cpf_tecnico'].apply(limpar_cpf)
        df['cpf_familiar'] = df['cpf_familiar'].apply(limpar_cpf)
        print("Limpeza dos dados concluída.")

        # ======================================================================
        # == NOVA ETAPA: FILTRAR APENAS AS COLUNAS QUE QUEREMOS SALVAR ==
        # Isto garante que colunas extras da planilha (como 'Coluna 1') sejam ignoradas.
        colunas_a_manter = list(mapeamento_colunas.values())
        df_final = df[colunas_a_manter]
        print("Colunas extras da planilha foram filtradas.")
        # ======================================================================

        print("Iniciando inserção de novos dados...")
        # Usamos o df_final, que só tem as colunas corretas
        df_final.to_sql(NOME_TABELA, conexao, if_exists='append', index=False)

        print("\n" + "="*40)
        print(f"✅ SUCESSO! {len(df_final)} registros foram migrados para a tabela '{NOME_TABELA}'.")
        print("="*40)

    except Exception as e:
        print(f"\n❌ Ocorreu um erro inesperado: {e}")
    finally:
        if conexao:
            conexao.close()
            print("\nConexão com o banco de dados fechada.")


if __name__ == "__main__":
    migrar_dados()
