import pandas as pd
import sqlite3
import re

# --- CONFIGURAÇÕES ---
URL_PLANILHA_CSV = (
    'https://docs.google.com/spreadsheets/d/e/2PACX-1vSiQIEwGylO5gmBzjWkorP6q'
    'OmUi5aRDssw9e18DCDA_UD3nurXqwcKGn9g5b4BAGr87_sY6vj04Zc7/pub?gid=12094'
    '02383&single=true&output=csv'
)
# MUDANÇA: Especificamos a pasta 'app/' para garantir que o ficheiro certo seja usado.
NOME_BANCO_DE_DADOS = "app/agendha.db"
NOME_TABELA = "beneficiarios"


def limpar_cpf(cpf_bruto):
    """Remove todos os caracteres não numéricos de um CPF."""
    if not cpf_bruto:
        return ""
    return re.sub(r'\D', '', str(cpf_bruto))


def migrar_dados():
    """Lê a planilha, limpa os dados e insere no banco de dados SQLite."""
    conexao = None
    try:
        # 1. Ler a planilha com o pandas
        print("Lendo dados da planilha...")
        df = pd.read_csv(URL_PLANILHA_CSV)
        print("Leitura da planilha concluída.")

        # 2. Limpeza e Preparação dos Dados
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

        # 3. Inserir os dados no Banco de Dados SQLite (LÓGICA CORRIGIDA)
        print(f"Conectando ao banco de dados '{NOME_BANCO_DE_DADOS}'...")
        conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
        cursor = conexao.cursor()
        print("Conexão bem-sucedida. Limpando dados antigos da tabela...")

        # Primeiro, apaga os dados existentes sem destruir a tabela
        cursor.execute(f"DELETE FROM {NOME_TABELA}")  # nosec
        conexao.commit()
        print(f"Tabela '{NOME_TABELA}' limpa.")

        # Depois, adiciona os novos dados da planilha
        print("Iniciando inserção de novos dados...")
        df.to_sql(NOME_TABELA, conexao, if_exists='append', index=False)

        print("\n" + "="*40)
        print(
            f"✅ SUCESSO! {len(df)} registros foram migrados para a tabela '{NOME_TABELA}'.")
        print("="*40)

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")


if __name__ == "__main__":
    migrar_dados()
