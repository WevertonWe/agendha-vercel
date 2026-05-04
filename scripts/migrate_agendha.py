import os
import sqlite3
import mimetypes
import unicodedata
import re
from pathlib import Path
from dotenv import load_dotenv

# Dependências necessárias: pip install psycopg2-binary supabase
import psycopg2
from psycopg2.extras import execute_values
from supabase import create_client, Client

load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_DB_STRING = os.getenv("SUPABASE_DB_STRING") # ex: postgresql://postgres:password@db.supabase.co:5432/postgres

# Altera a porta padrão 5432 para 6543 (Transaction Pooler) automaticamente se necessário
if SUPABASE_DB_STRING and ":5432/" in SUPABASE_DB_STRING:
    SUPABASE_DB_STRING = SUPABASE_DB_STRING.replace(":5432/", ":6543/")

BUCKET_NAME = "agendha-uploads"

if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_DB_STRING:
    print("ERRO: Variáveis SUPABASE_URL, SUPABASE_KEY ou SUPABASE_DB_STRING não encontradas no .env")
    exit(1)

# Inicializar cliente Supabase (para Storage)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurações do banco local
SQLITE_DB_PATH = "agendha.db"
UPLOADS_DIR = Path("app/uploads")

# Mapeamento de tabelas a serem migradas (em ordem de dependência)
TABLES_TO_MIGRATE = [
    "users",
    "user_project_roles",
    "pedreiros",
    "faturamentos",          # faturamentos depende de pedreiros
    "beneficiarios",         # beneficiarios depende de pedreiros e faturamentos
    "financeiro_entidades",
    "financeiro_projetos",
    "financeiro_metas",
    "financeiro_etapas",
    "financeiro_rubricas",
    "financeiro_lancamentos",
    "oficios",
    "logs_acesso",
    "mapa_pontos",
    "mapa_categorias",
    "historico_conferencias",
    "cronograma_execucao",
    "cronograma_beneficiarios", # depende de beneficiarios e pedreiros
    "fornecedores",
    "materiais",
    "cotacoes_master",
    "cotacao_itens",
    "teste_persistencia",
    "sugestoes_projetos"
]

def sanitize_path(path_str):
    """Sanitiza nomes de arquivos e pastas removendo acentos, espaços e caracteres especiais."""
    parts = path_str.split('/')
    sanitized_parts = []
    for part in parts:
        # Remove acentos
        nfkd = unicodedata.normalize('NFKD', part)
        part = "".join([c for c in nfkd if not unicodedata.combining(c)])
        # Substitui espaços e caracteres não permitidos por underscore
        part = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', part)
        # Remove múltiplos underscores consecutivos
        part = re.sub(r'_+', '_', part)
        sanitized_parts.append(part)
    return '/'.join(sanitized_parts)

def upload_files_to_storage():
    """Faz upload de todos os arquivos do app/uploads para o Supabase Storage com resiliência e sanitização."""
    print(f"\\n--- Iniciando upload de arquivos para o bucket '{BUCKET_NAME}' ---")
    url_mapping = {}
    
    if not UPLOADS_DIR.exists():
        print(f"Diretório {UPLOADS_DIR} não encontrado. Pulando uploads.")
        return url_mapping

    try:
        supabase.storage.get_bucket(BUCKET_NAME)
    except Exception:
        print(f"Tentando criar o bucket '{BUCKET_NAME}' (se falhar, crie manualmente no painel e deixe como Público)...")
        try:
            supabase.storage.create_bucket(BUCKET_NAME, public=True)
        except Exception as e:
            print(f"Aviso ao criar bucket: {e}")

    # Cache para arquivos que já existem no Storage (por pasta) para evitar recarregamentos e listar mais rápido
    folder_cache = {}

    for file_path in UPLOADS_DIR.rglob("*"):
        if file_path.is_file():
            # Caminho relativo local original
            rel_path = file_path.relative_to(UPLOADS_DIR).as_posix()
            
            # Caminho sanitizado para o Storage
            sanitized_rel_path = sanitize_path(rel_path)
            
            # Pasta base e nome do arquivo para verificação de existência
            folder_name = os.path.dirname(sanitized_rel_path)
            file_name = os.path.basename(sanitized_rel_path)
            
            # Verifica se já listamos a pasta atual, se não, carrega os arquivos dela (cache)
            if folder_name not in folder_cache:
                try:
                    # Lista arquivos no diretório especificado
                    res = supabase.storage.from_(BUCKET_NAME).list(folder_name)
                    # res retorna uma lista de dicts [{'name': 'arquivo.pdf', ...}, ...]
                    folder_cache[folder_name] = {f['name'] for f in res} if res else set()
                except Exception:
                    folder_cache[folder_name] = set()

            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"

            # Se arquivo já existe no Supabase, pula o upload
            if file_name in folder_cache[folder_name]:
                print(f"Arquivo já existe, pulando upload: {sanitized_rel_path}")
            else:
                print(f"Fazendo upload: {sanitized_rel_path}...")
                try:
                    with open(file_path, "rb") as f:
                        supabase.storage.from_(BUCKET_NAME).upload(
                            path=sanitized_rel_path,
                            file=f,
                            file_options={"content-type": content_type}
                        )
                    # Adiciona ao cache local para evitar duplicação em re-execuções no mesmo processo
                    folder_cache[folder_name].add(file_name)
                except Exception as e:
                    print(f"ERRO ao fazer upload de '{rel_path}' -> '{sanitized_rel_path}': {e}")
                    # Registra o erro e continua para o próximo arquivo, sem quebrar o loop

            # Obter URL pública do arquivo sanitizado
            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(sanitized_rel_path)
            
            # Mapear caminhos locais ORIGINAIS para a nova URL pública (pois o banco possui o original)
            url_mapping[rel_path] = public_url
            url_mapping[f"uploads/{rel_path}"] = public_url
            url_mapping[f"app/uploads/{rel_path}"] = public_url

    print("--- Uploads concluídos ---\\n")
    return url_mapping

def migrate_database(url_mapping):
    """Lê do SQLite, substitui URLs e insere no PostgreSQL."""
    print("--- Iniciando migração do banco de dados ---")
    
    conn_sqlite = sqlite3.connect(SQLITE_DB_PATH)
    conn_sqlite.row_factory = sqlite3.Row
    cur_sqlite = conn_sqlite.cursor()

    try:
        print("Conectando ao PostgreSQL na porta 6543...")
        conn_pg = psycopg2.connect(SUPABASE_DB_STRING)
        cur_pg = conn_pg.cursor()
        print("Conexão bem sucedida com o PostgreSQL!")
        
        print("\nLimpando dados parciais das tabelas (ordem reversa)...")
        for table in reversed(TABLES_TO_MIGRATE):
            try:
                cur_pg.execute(f"DELETE FROM {table}")
            except Exception:
                # Pode falhar se a tabela não existir ou outro erro, ignora e continua
                conn_pg.rollback()
        conn_pg.commit()
        print("Limpeza concluída.\n")
    except psycopg2.OperationalError as e:
        print("\\n[FALHA CRÍTICA] Erro operacional de conexão com o banco de dados:")
        print(f"{e}")
        print("Possíveis causas:")
        print("- Sua senha contém caracteres especiais que precisam de URL encode (ex: @ vira %40).")
        print("- A porta 6543 não está ativa no seu painel ou bloqueada por firewall.")
        print("- 'Connection timed out' = O banco demorou muito para responder (verifique IP e Firewall).")
        print("- 'InvalidKey' / 'Invalid password' = Verifique a senha do banco em Configurações > Database no Supabase.\\n")
        return
    except Exception as e:
        print("\\n[FALHA CRÍTICA] Erro inesperado ao conectar ao PostgreSQL:")
        print(f"{e}\\n")
        return

    for table in TABLES_TO_MIGRATE:
        print(f"Migrando tabela: {table}...")
        try:
            cur_sqlite.execute(f"SELECT * FROM {table}")
            rows = cur_sqlite.fetchall()
            
            if not rows:
                print(f"  Tabela {table} vazia. Pulando.")
                continue

            columns = rows[0].keys()
            col_names = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            
            # Preparar dados e substituir caminhos locais por URLs do Supabase
            data_to_insert = []
            
            # Colunas sensíveis onde string vazia '' deve virar NULL (None)
            null_cols = ['latitude', 'longitude', 'valor_total', 'valor_dam', 'quantidade']
            
            for row in rows:
                values = list(row)
                for i, col in enumerate(columns):
                    val = values[i]
                    
                    # 1. TRATAMENTO DE DATAS, NÚMEROS E FKS VAZIOS E FORMATOS DE DATA
                    if val == "":
                        if col in null_cols or col.startswith('data_') or col.endswith('_id') or col == 'timestamp':
                            values[i] = None
                    elif isinstance(val, str):
                        val_stripped = val.strip()
                        
                        # 1.1 TRATAMENTO ROBUSTO DE DATA
                        is_date_col = 'data' in col.lower() or col == 'nascimento'
                        has_question_mark_date = re.match(r'^[\?\d]{1,2}/[\?\d]{1,2}/[\?\d]{2,4}', val_stripped)
                        
                        if '?' in val_stripped and (is_date_col or has_question_mark_date):
                            print(f"  [LIMPEZA] Data inválida '{val}' no ID {values[0]} convertida para NULL")
                            values[i] = None
                        else:
                            match_date = re.match(r'^(\d{2})/(\d{2})/(\d{4})(.*)$', val_stripped)
                            if match_date:
                                d, m, y, rest = match_date.groups()
                                values[i] = f"{y}-{m}-{d}{rest}"
                            elif is_date_col and val_stripped != '':
                                # Se é um campo de data mas o formato não é reconhecido, converte para NULL
                                if not re.match(r'^\d{4}-\d{2}-\d{2}', val_stripped):
                                    print(f"  [LIMPEZA] Data de formato não reconhecido '{val}' no ID {values[0]} convertida para NULL")
                                    values[i] = None
                            
                    # 2. TRATAMENTO DE BOOLEANOS
                    if col in ('verificacao_bsf', 'is_active'):
                        v = values[i]
                        if v in (1, '1', True, 'true', 'True'): 
                            values[i] = True
                        elif v in (0, '0', False, 'false', 'False', None, ''): 
                            values[i] = False
                            
                    # Atualiza a referência de val após possíveis modificações
                    val = values[i]
                    
                    if isinstance(val, str):
                        if val in url_mapping:
                            values[i] = url_mapping[val]
                        elif val.startswith("app/uploads/") or val.startswith("uploads/"):
                            print(f"  [AVISO] Arquivo não encontrado no disco para a coluna '{col}': {val}")
                data_to_insert.append(tuple(values))

            insert_query = f"INSERT INTO {table} ({col_names}) VALUES %s ON CONFLICT (id) DO NOTHING"
            insert_query_single = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING"
            
            try:
                execute_values(cur_pg, insert_query, data_to_insert)
                
                # Atualizar a sequence do SERIAL para o maior ID inserido
                cur_pg.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(max(id), 1), max(id) IS NOT NULL) FROM {table};")
                conn_pg.commit()
                print(f"  {len(data_to_insert)} registros inseridos em {table}.")
            except Exception:
                conn_pg.rollback()
                print(f"  [ALERTA] Falha no insert em lote para {table}. Tentando linha a linha para isolar o erro...")
                
                success_count = 0
                for idx, row_val in enumerate(data_to_insert):
                    try:
                        cur_pg.execute(insert_query_single, row_val)
                        success_count += 1
                    except Exception as single_err:
                        conn_pg.rollback()
                        print(f"  --> [ERRO NA LINHA {idx + 1}] Falha ao inserir registro (ID: {row_val[0] if row_val else '?'}).")
                        print(f"      Dados da linha: {row_val}")
                        print(f"      Detalhe do erro: {single_err}")
                        # Interrompe a tabela no primeiro erro detalhado para feedback
                        break
                
                # Atualizar sequence para o que conseguiu inserir
                cur_pg.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(max(id), 1), max(id) IS NOT NULL) FROM {table};")
                conn_pg.commit()
                print(f"  {success_count} registros recuperados/inseridos em {table} antes do erro.")
            
        except Exception as e:
            print(f"Erro geral ao migrar tabela {table}: {e}")
            conn_pg.rollback()

    conn_sqlite.close()
    cur_pg.close()
    conn_pg.close()
    print("--- Migração do banco concluída ---")

if __name__ == "__main__":
    print("Iniciando processo de migração para o Supabase...")
    url_mapping = upload_files_to_storage()
    migrate_database(url_mapping)
    print("Migração finalizada com sucesso!")
