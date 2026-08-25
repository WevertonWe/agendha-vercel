import logging
import os
from passlib.context import CryptContext
from app.config import settings

# --- DEBUG AUDIT (Handshake 2025) ---
print(f"DEBUG: VERCEL_ENV_VAR: {os.getenv('VERCEL')}")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_connection(request=None): 
    """Conexão por requisição (Hard-Locked for Production)"""
    
    # Force use of SUPABASE_DB_STRING in production
    if os.getenv("VERCEL") or os.getenv("SUPABASE_DB_STRING"):
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            db_string = os.getenv("SUPABASE_DB_STRING")
            if not db_string:
                raise RuntimeError("CRITICAL: SUPABASE_DB_STRING is missing in production!")
            conexao = psycopg2.connect(db_string, cursor_factory=RealDictCursor)
            
            try:
                yield conexao
            finally:
                if not conexao.closed:
                    conexao.close()
            return
        except Exception as e:
            logging.error(f"PostgreSQL connection failed: {e}")
            if os.getenv("VERCEL"):
                raise RuntimeError(f"Database connection failed in production: {e}")
            
    # Fallback apenas para DEV LOCAL
    import sqlite3
    try:
        from app.database.wrapper import AuditConnection
        conexao = AuditConnection(os.path.join(os.getcwd(), "agendha.db"), check_same_thread=False)
        conexao.execute("PRAGMA foreign_keys = ON")
        conexao.row_factory = sqlite3.Row
    except Exception as e:
        # Se SQLite falhar, tenta SUPABASE_DB_STRING como última chance
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            db_string = os.getenv("SUPABASE_DB_STRING")
            if db_string:
                conexao = psycopg2.connect(db_string, cursor_factory=RealDictCursor)
                try:
                    yield conexao
                finally:
                    if not conexao.closed:
                        conexao.close()
                return
            else:
                raise e
        except Exception:
            raise e
    
    # Try to set user context if request is provided and has user
    try:
        if request and hasattr(request, "state") and hasattr(request.state, "user"):
            user = request.state.user
            user_id = user.get("username") if isinstance(user, dict) else getattr(user, "username", "SYSTEM")
            if hasattr(conexao, "set_user"):
                conexao.set_user(user_id)
    except Exception:
        pass # Fallback to SYSTEM

    try:
        yield conexao
    finally:
        conexao.close()

def init_db():
    """Valida conexão com o banco de dados (SQLite local ou Supabase Cloud)"""
    
    # Se estivermos na Vercel, o FS é Read-only. Não tentamos criar tabelas no SQLite local.
    if os.getenv("VERCEL"):
        logging.info("Ambiente Vercel detectado. Pulando inicialização de tabelas SQLite locais.")
        
        # Validação do Supabase (Cloud Database)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if supabase_url and supabase_key:
            try:
                from supabase import create_client
                create_client(supabase_url, supabase_key)
                logging.info("✅ Conexão com Supabase validada com sucesso.")
            except Exception as e:
                logging.error(f"⚠️ Erro ao validar conexão Supabase: {e}")
        else:
            logging.warning("⚠️ Supabase não configurado (SUPABASE_URL/KEY ausentes).")
        
        return

    # Fallback LOCAL: Importações tardias para evitar ghost imports em PROD
    import sys
    if sys.platform == "win32":
        for qgis_bin in [
            r"C:\Program Files\QGIS 3.44.12\bin",
            r"C:\Program Files\QGIS 3.44.12\apps\Python312\DLLs",
            r"C:\Program Files\QGIS 3.44.12\apps\Python312",
            r"C:\Program Files\QGIS 3.44.12\apps\qt5\bin",
            r"C:\Program Files\QGIS 3.34.0\bin",
            r"C:\Program Files\QGIS 3.34.0\apps\Python312\DLLs"
        ]:
            if os.path.exists(qgis_bin):
                try:
                    os.add_dll_directory(qgis_bin)
                except Exception:
                    pass
    import sqlite3

    DB_PATH_FIX = os.path.join(os.getcwd(), "agendha.db")
    logging.info(f"Inicializando banco de dados local em: {DB_PATH_FIX}")
    
    conn = sqlite3.connect(DB_PATH_FIX)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()

    
    # --- MÓDULO DE ACESSO E USUÁRIOS ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        is_active BOOLEAN NOT NULL DEFAULT 1,
        full_name TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_project_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        project_id TEXT NOT NULL,
        role TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # --- MÓDULO ADMINISTRATIVO ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS oficios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_oficio TEXT,
        destinatario TEXT NOT NULL,
        data_envio TEXT NOT NULL,
        motivo_descricao TEXT,
        criado_por TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fornecedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT NOT NULL,
        nome_fantasia TEXT,
        cnpj_cpf TEXT UNIQUE,
        email TEXT,
        telefone TEXT,
        endereco TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materiais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        unidade TEXT NOT NULL,
        categoria TEXT,
        descricao TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cotacao_itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cotacao_master_id INTEGER NOT NULL,
        material_id INTEGER NOT NULL,
        quantidade REAL NOT NULL,
        FOREIGN KEY (cotacao_master_id) REFERENCES cotacoes_master (id),
        FOREIGN KEY (material_id) REFERENCES materiais (id)
    )
    """)

    # --- MÓDULO FINANCEIRO (GARANTINDO A CRIAÇÃO) ---
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

    # --- MÓDULO PROJETOS (SUGESTÕES) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sugestoes_projetos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projeto_id TEXT NOT NULL,
        usuario_id TEXT,
        sugestao TEXT NOT NULL,
        data_criacao TEXT
    )
    """)

    # --- MÓDULO BAHIA SEM FOME (BSF) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bsf_metas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        municipio TEXT NOT NULL,
        mes INTEGER NOT NULL,
        ano INTEGER NOT NULL,
        meta_total INTEGER NOT NULL,
        UNIQUE(municipio, mes, ano)
    )
    """)

    # --- MÓDULO ÁGUA QUE ALIMENTA (AQA) ---
    # Tabelas recuperadas via Code Archaeology (2026-02-12)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedreiros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_completo TEXT NOT NULL,
        cpf TEXT UNIQUE,
        telefone TEXT,
        endereco TEXT,
        dados_pagamento TEXT,
        status TEXT DEFAULT 'Ativo'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faturamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedreiro_id INTEGER NOT NULL,
        valor_total REAL DEFAULT 0.0,
        valor_dam REAL DEFAULT 0.0,
        status_dam TEXT DEFAULT 'Pendente',
        arquivo_nf TEXT,
        arquivo_dam TEXT,
        data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pedreiro_id) REFERENCES pedreiros(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS beneficiarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_completo TEXT,
        nome_familiar TEXT,
        cpf TEXT UNIQUE,
        cpf_familiar TEXT,
        nis TEXT,
        data_nascimento TEXT,
        sexo TEXT,
        escolaridade TEXT,
        municipio TEXT,
        comunidade TEXT,
        estado_uf TEXT,
        ref_localizacao TEXT, 
        latitude TEXT,
        longitude TEXT,
        status TEXT DEFAULT 'Em Cadastro',
        doc_status TEXT, 
        pedreiro_id INTEGER,
        link_nota_fiscal TEXT,
        status_pagamento TEXT DEFAULT 'PENDENTE',
        data_conclusao TEXT,
        faturamento_id INTEGER,
        FOREIGN KEY (pedreiro_id) REFERENCES pedreiros(id),
        FOREIGN KEY (faturamento_id) REFERENCES faturamentos(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cronograma (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarefa TEXT NOT NULL,
        data_prevista TEXT,
        data_realizada TEXT,
        status TEXT DEFAULT 'Pendente',
        responsavel TEXT,
        observacao TEXT
    )
    """)

    # --- MÓDULO BAHIA SEM FOME (BSF) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bsf_atividades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT,
        meta_padrao INTEGER DEFAULT 0
    )
    """)

    # Seed de atividades — as 16 reais do Contrato 014/2024
    # Formato: (nome, descricao, meta_mensal, meta_anual)
    atividades_contrato = [
        ("Reunião de Articulação com os Parceiros", "Reuniões com lideranças e parceiros", 1, 6),
        ("Levantamento Socioeconômico e Geolocalização", "Levantamento inicial de dados", 41, 490),
        ("Cadastro do Grupo Familiar", "Cadastro de famílias no sistema", 41, 490),
        ("Caracterização da UPF I (Inicial)", "Caracterização inicial da unidade", 41, 490),
        ("Caracterização da UPF II (Intermediária)", "Caracterização intermediária", 41, 490),
        ("Caracterização da UPF III (Final)", "Caracterização final da unidade", 41, 490),
        ("Visita Técnica Social", "Visitas de acompanhamento a famílias", 163, 1960),
        ("Elaboração do Plano Produtivo da UPF", "Elaboração de planos produtivos", 41, 490),
        ("Visita Técnica", "Visitas técnicas de campo", 898, 10771),
        ("Demonstração Didática", "Demonstrações práticas", 25, 300),
        ("Seminário Territorial", "Seminários territoriais", 1, 1),
        ("Seminário Final", "Seminários de encerramento", 1, 1),
        ("Excursão/Intercâmbio", "Visitas de intercâmbio entre comunidades", 1, 12),
        ("Curso", "Cursos de capacitação", 8, 93),
        ("Oficina Temática", "Oficinas e treinamentos temáticos", 8, 96),
        ("Dia de Campo", "Demonstração prática em campo", 8, 96),
    ]
    for nome, desc, _, _ in atividades_contrato:
        try:
            cursor.execute("INSERT OR IGNORE INTO bsf_atividades (nome, descricao) VALUES (?, ?)", (nome, desc))
        except Exception:
            pass
        # Garantir que a descrição esteja atualizada
        cursor.execute("UPDATE bsf_atividades SET descricao = ? WHERE nome = ?", (desc, nome))

    # --- Tabela de Metas do Contrato BSF ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bsf_metas_contrato (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        atividade_id INTEGER NOT NULL,
        ano INTEGER NOT NULL,
        meta_mensal INTEGER DEFAULT 0,
        meta_anual INTEGER DEFAULT 0,
        FOREIGN KEY (atividade_id) REFERENCES bsf_atividades(id),
        UNIQUE(atividade_id, ano)
    )
    """)

    # Seed das metas do contrato para 2025 e 2026
    for nome, _, meta_mensal, meta_anual in atividades_contrato:
        cursor.execute("SELECT id FROM bsf_atividades WHERE nome = ?", (nome,))
        row = cursor.fetchone()
        if row:
            atv_id = row[0]
            for ano_seed in [2025, 2026]:
                try:
                    cursor.execute("""
                        INSERT INTO bsf_metas_contrato (atividade_id, ano, meta_mensal, meta_anual)
                        VALUES (?, ?, ?, ?)
                    """, (atv_id, ano_seed, meta_mensal, meta_anual))
                except sqlite3.IntegrityError:
                    pass  # Já existe

    # --- Tabela de Composição de Metas BSF ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bsf_metas_composicao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meta_id INTEGER NOT NULL,
        atividade_id INTEGER NOT NULL,
        valor_meta INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(meta_id) REFERENCES bsf_metas(id) ON DELETE CASCADE,
        FOREIGN KEY(atividade_id) REFERENCES bsf_atividades(id)
    )
    """)

    # NOTE: SEM FOREIGN KEY em municipio! bsf_metas usa UNIQUE(municipio,mes,ano)
    # então FK simples em municipio é inválida e causa constraint failure.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bsf_visitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tecnico_id TEXT NOT NULL,
        beneficiario_id TEXT NOT NULL,
        municipio TEXT NOT NULL,
        comunidade TEXT,
        data_visita TEXT NOT NULL,
        status TEXT DEFAULT 'Realizada',
        atividade_id INTEGER,
        data_registro TEXT
    )
    """)

    # --- Tabela de Metas por Técnico ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bsf_metas_tecnicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tecnico_id TEXT NOT NULL,
        atividade_id INTEGER NOT NULL,
        mes INTEGER NOT NULL,
        ano INTEGER NOT NULL,
        valor_meta INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (atividade_id) REFERENCES bsf_atividades(id),
        UNIQUE(tecnico_id, atividade_id, mes, ano)
    )
    """)

    # --- MÓDULO DE ATIVOS E CREDENCIAIS (ADMINISTRATIVO) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bsf_powerbi_credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_projeto TEXT NOT NULL,
        email_login TEXT NOT NULL,
        senha TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Ativo',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendha_dispositivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        marca_modelo TEXT NOT NULL,
        numero_serie_imei TEXT UNIQUE NOT NULL,
        responsavel_atual TEXT,
        status TEXT NOT NULL DEFAULT 'Disponível',
        url_termo_pdf TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # --- MÓDULO P1+2 (CLONE ADAPTADO) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS p12_beneficiarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_completo TEXT,
        nome_familiar TEXT,
        cpf TEXT UNIQUE,
        cpf_familiar TEXT,
        nis TEXT,
        data_nascimento TEXT,
        sexo TEXT,
        escolaridade TEXT,
        municipio TEXT,
        comunidade TEXT,
        estado_uf TEXT DEFAULT 'BA',
        ref_localizacao TEXT, 
        latitude TEXT,
        longitude TEXT,
        status TEXT DEFAULT 'Ativo',
        doc_status TEXT DEFAULT 'Pendente',
        data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
        observacoes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS p12_monitoramentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL, -- 'GAPA', 'SISMA', 'INTERCAMBIO'
        titulo TEXT NOT NULL,
        data_evento TEXT NOT NULL,
        municipio TEXT,
        comunidade TEXT,
        responsavel TEXT,
        status TEXT DEFAULT 'Realizado',
        quantidade_participantes INTEGER DEFAULT 0,
        participantes_ids TEXT DEFAULT '[]',
        observacao TEXT,
        link_documento TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS p12_plano_produtivo_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chave_coluna TEXT UNIQUE NOT NULL,
        titulo_coluna TEXT NOT NULL,
        tipo_coluna TEXT DEFAULT 'texto',
        ordem INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS p12_plano_produtivo_dados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        beneficiario_id INTEGER,
        nome_beneficiario TEXT,
        municipio TEXT,
        comunidade TEXT,
        status_parcela_1 TEXT DEFAULT 'Pendente',
        status_parcela_2 TEXT DEFAULT 'Pendente',
        observacoes TEXT,
        campos_dinamicos TEXT DEFAULT '{}',
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (beneficiario_id) REFERENCES p12_beneficiarios(id) ON DELETE SET NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS p12_cronograma_execucao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        municipio TEXT NOT NULL,
        semana_referencia INTEGER DEFAULT 1,
        ano INTEGER DEFAULT 2026,
        meta_planejada INTEGER DEFAULT 0,
        qtd_executada INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Em Andamento',
        observacoes TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS p12_documentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_documento TEXT NOT NULL,
        categoria TEXT DEFAULT 'Geral',
        nome_arquivo TEXT NOT NULL,
        caminho_arquivo TEXT NOT NULL,
        data_upload TEXT DEFAULT CURRENT_TIMESTAMP,
        tamanho_bytes INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS p12_cotacoes_master (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_cotacao TEXT UNIQUE NOT NULL,
        titulo TEXT NOT NULL,
        descricao TEXT,
        status TEXT DEFAULT 'Aberta',
        data_abertura TEXT DEFAULT CURRENT_TIMESTAMP,
        data_fechamento TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS p12_cotacao_itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cotacao_master_id INTEGER NOT NULL,
        descricao_item TEXT NOT NULL,
        unidade TEXT DEFAULT 'UN',
        quantidade REAL NOT NULL,
        valor_unitario_estimado REAL DEFAULT 0.0,
        valor_total_estimado REAL DEFAULT 0.0,
        fornecedor_vencedor TEXT,
        status TEXT DEFAULT 'Pendente',
        FOREIGN KEY (cotacao_master_id) REFERENCES p12_cotacoes_master(id) ON DELETE CASCADE
    )
    """)

    # --- MIGRAÇÕES E DADOS PADRÃO ---
    try:
        cursor.execute("ALTER TABLE propostas ADD COLUMN fornecedor_id INTEGER REFERENCES fornecedores(id)")
    except sqlite3.OperationalError:
        pass

    # Migração: adicionar atividade_id em bsf_visitas (para bancos antigos)
    try:
        cursor.execute("ALTER TABLE bsf_visitas ADD COLUMN atividade_id INTEGER")
    except sqlite3.OperationalError:
        pass

    # Migração: adicionar data_registro em bsf_visitas (para bancos antigos)
    try:
        cursor.execute("ALTER TABLE bsf_visitas ADD COLUMN data_registro TEXT")
    except sqlite3.OperationalError:
        pass

    # Migração: adicionar tecnico_responsavel em bsf_metas (para bancos antigos)
    try:
        cursor.execute("ALTER TABLE bsf_metas ADD COLUMN tecnico_responsavel TEXT")
    except sqlite3.OperationalError:
        pass
        
    # Migração: adicionar faturamento_id em beneficiarios
    try:
        cursor.execute("ALTER TABLE beneficiarios ADD COLUMN faturamento_id INTEGER REFERENCES faturamentos(id)")
    except sqlite3.OperationalError:
        pass

    # Migração: adicionar participantes_nomes em p12_monitoramentos
    try:
        cursor.execute("ALTER TABLE p12_monitoramentos ADD COLUMN participantes_nomes TEXT")
    except sqlite3.OperationalError:
        pass

    
    # Cria usuário admin se não existir
    cursor.execute("SELECT * FROM users WHERE username = ?", (settings.ADMIN_USERNAME,))
    if not cursor.fetchone():
        logging.info("Criando usuário admin padrão...")
        password_hash = pwd_context.hash(settings.ADMIN_PASSWORD)
        cursor.execute("""
        INSERT INTO users (username, password_hash, role, is_active, full_name)
        VALUES (?, ?, 'admin', 1, 'Administrador do Sistema')
        """, (settings.ADMIN_USERNAME, password_hash))
        conn.commit()
    
    # Garantir que tudo é salvo e FK volta a funcionar
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.close()
    logging.info("Banco de dados inicializado com sucesso.")

def get_supabase():
    """Retorna o cliente do Supabase centralizado"""
    import os
    from supabase import create_client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL ou SUPABASE_KEY não configuradas no ambiente!")
    return create_client(supabase_url, supabase_key)

def fetch_all(table_name: str, select_query: str = '*'):
    """Busca todos os registros de uma tabela Supabase ou SQLite local (fallback resiliente)"""
    all_data = []
    try:
        supabase = get_supabase()
        page_size = 1000
        start = 0

        while True:
            end = start + page_size - 1
            res = supabase.table(table_name).select(select_query).range(start, end).execute()
            if not res.data:
                break
            all_data.extend(res.data)
            if len(res.data) < page_size:
                break
            start += page_size
        return all_data
    except Exception as e:
        # Fallback para SQLite local
        import os
        db_path = os.path.join(os.getcwd(), "agendha.db")
        if os.path.exists(db_path):
            try:
                import sys
                if sys.platform == "win32":
                    for qgis_bin in [
                        r"C:\Program Files\QGIS 3.44.12\bin",
                        r"C:\Program Files\QGIS 3.44.12\apps\Python312\DLLs",
                        r"C:\Program Files\QGIS 3.44.12\apps\Python312"
                    ]:
                        if os.path.exists(qgis_bin):
                            try:
                                os.add_dll_directory(qgis_bin)
                            except Exception:
                                pass
                import sqlite3
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(f"SELECT {select_query} FROM {table_name}")
                rows = cursor.fetchall()
                conn.close()
                return [dict(r) for r in rows]
            except Exception as e_sql:
                logging.warning(f"Aviso fetch_all ({table_name}): Supabase e SQLite falharam ({e_sql})")
        return []


def _get_sqlite_conn():
    """Retorna uma conexão configurada com o SQLite local agendha.db"""
    import os
    import sys
    if sys.platform == "win32":
        for qgis_bin in [
            r"C:\Program Files\QGIS 3.44.12\bin",
            r"C:\Program Files\QGIS 3.44.12\apps\Python312\DLLs",
            r"C:\Program Files\QGIS 3.44.12\apps\Python312",
            r"C:\Program Files\QGIS 3.34.0\bin",
            r"C:\Program Files\QGIS 3.34.0\apps\Python312\DLLs"
        ]:
            if os.path.exists(qgis_bin):
                try:
                    os.add_dll_directory(qgis_bin)
                except Exception:
                    pass
    import sqlite3
    db_path = os.path.join(os.getcwd(), "agendha.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def db_insert(table_name: str, data: dict) -> dict:
    """Insere registro no Supabase ou no SQLite local de forma transparente."""
    import json
    clean_data = {k: v for k, v in data.items() if v is not None}

    # 1. Tentar Supabase
    try:
        supabase = get_supabase()
        res = supabase.table(table_name).insert(clean_data).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception as e:
        logging.info(f"[db_insert] Supabase indisponível para tabela {table_name} ({e}). Salvando no SQLite local...")

    # 2. Fallback SQLite
    try:
        conn = _get_sqlite_conn()
        cursor = conn.cursor()

        # Obter colunas existentes na tabela SQLite
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_cols = {col[1] for col in cursor.fetchall()}

        sqlite_data = {}
        for k, v in clean_data.items():
            val = v
            if isinstance(v, (dict, list)):
                val = json.dumps(v)
            elif isinstance(v, bool):
                val = 1 if v else 0
            
            if existing_cols:
                if k in existing_cols:
                    sqlite_data[k] = val
                elif k == "item_nome" and "descricao_item" in existing_cols:
                    sqlite_data["descricao_item"] = val
                elif k == "descricao_item" and "item_nome" in existing_cols:
                    sqlite_data["item_nome"] = val
            else:
                sqlite_data[k] = val

        cols = list(sqlite_data.keys())
        placeholders = ["?"] * len(cols)
        sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(sql, list(sqlite_data.values()))
        new_id = cursor.lastrowid
        conn.commit()

        cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (new_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return {"id": new_id, **clean_data}
    except Exception as e_sql:
        logging.error(f"[db_insert] Falha no SQLite para {table_name}: {e_sql}")
        raise RuntimeError(f"Erro ao salvar dados em {table_name}: {e_sql}")


def db_update(table_name: str, id_value: any, data: dict, id_col: str = "id") -> dict:
    """Atualiza registro no Supabase ou no SQLite local de forma transparente."""
    import json
    clean_data = {k: v for k, v in data.items() if v is not None}

    # 1. Tentar Supabase
    try:
        supabase = get_supabase()
        res = supabase.table(table_name).update(clean_data).eq(id_col, id_value).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception as e:
        logging.info(f"[db_update] Supabase indisponível para tabela {table_name} ({e}). Atualizando no SQLite local...")

    # 2. Fallback SQLite
    try:
        conn = _get_sqlite_conn()
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_cols = {col[1] for col in cursor.fetchall()}

        sqlite_data = {}
        for k, v in clean_data.items():
            val = v
            if isinstance(v, (dict, list)):
                val = json.dumps(v)
            elif isinstance(v, bool):
                val = 1 if v else 0
            
            if existing_cols:
                if k in existing_cols:
                    sqlite_data[k] = val
                elif k == "item_nome" and "descricao_item" in existing_cols:
                    sqlite_data["descricao_item"] = val
                elif k == "descricao_item" and "item_nome" in existing_cols:
                    sqlite_data["item_nome"] = val
            else:
                sqlite_data[k] = val

        if not sqlite_data:
            conn.close()
            return {id_col: id_value}

        set_clause = ", ".join([f"{k} = ?" for k in sqlite_data.keys()])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {id_col} = ?"
        cursor.execute(sql, list(sqlite_data.values()) + [id_value])
        conn.commit()

        cursor.execute(f"SELECT * FROM {table_name} WHERE {id_col} = ?", (id_value,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return {id_col: id_value, **clean_data}
    except Exception as e_sql:
        logging.error(f"[db_update] Falha no SQLite para {table_name}: {e_sql}")
        raise RuntimeError(f"Erro ao atualizar dados em {table_name}: {e_sql}")


def db_delete(table_name: str, id_value: any, id_col: str = "id") -> bool:
    """Exclui registro no Supabase ou no SQLite local de forma transparente."""
    # 1. Tentar Supabase
    try:
        supabase = get_supabase()
        supabase.table(table_name).delete().eq(id_col, id_value).execute()
    except Exception as e:
        logging.info(f"[db_delete] Supabase indisponível para tabela {table_name} ({e}). Excluindo no SQLite local...")

    # 2. Fallback SQLite
    try:
        conn = _get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE {id_col} = ?", (id_value,))
        conn.commit()
        conn.close()
        return True
    except Exception as e_sql:
        logging.error(f"[db_delete] Falha no SQLite para {table_name}: {e_sql}")
        raise RuntimeError(f"Erro ao excluir dados em {table_name}: {e_sql}")




def sync_projects() -> None:
    """
    Sincroniza a tabela `projetos` no Supabase com os módulos físicos em app/modules/.

    - Insere projetos novos (pastas que existem no FS mas não no Supabase).
    - Desativa projetos removidos (registros no Supabase cujas pastas não existem mais).
    - É idempotente e non-blocking: falhas são logadas mas não interrompem o boot.

    Chamada uma vez durante o lifespan do FastAPI em `main.py`.
    """
    try:
        import pathlib

        supabase = get_supabase()

        # 1. Detecta pastas físicas em app/modules/
        modules_dir = pathlib.Path(__file__).resolve().parent.parent / "modules"
        if not modules_dir.exists():
            logging.warning(f"[sync_projects] Diretório de módulos não encontrado: {modules_dir}")
            return

        # Nomes de pastas que são módulos válidos (têm __init__.py ou views.py)
        fs_slugs: set[str] = set()
        for folder in modules_dir.iterdir():
            if folder.is_dir() and not folder.name.startswith("_"):
                # Considera módulo válido se tem views.py ou routers/
                has_views = (folder / "views.py").exists()
                has_routers = (folder / "routers").is_dir()
                has_routes = (folder / "routes.py").exists()
                if has_views or has_routers or has_routes:
                    fs_slugs.add(folder.name)

        # 2. Busca projetos já registrados no Supabase
        res = supabase.table("projetos").select("id, ativo").execute()
        db_rows = {row["id"]: row["ativo"] for row in (res.data or [])}
        db_slugs = set(db_rows.keys())

        # 3. Inserir novos projetos (existem no FS, não no DB)
        to_insert = fs_slugs - db_slugs
        for slug in to_insert:
            nome_display = slug.replace("_", " ").title()
            pasta = f"app/modules/{slug}"
            supabase.table("projetos").insert({
                "id": slug,
                "nome": nome_display,
                "descricao": f"Módulo {nome_display} (auto-detectado)",
                "ativo": True,
                "pasta_fisica": pasta,
            }).execute()
            logging.info(f"[sync_projects] ✅ Novo projeto registrado: {slug}")

        # 4. Desativar projetos removidos (existem no DB, não no FS)
        to_deactivate = db_slugs - fs_slugs
        for slug in to_deactivate:
            if db_rows.get(slug):  # Só desativa se ainda estava ativo
                supabase.table("projetos").update({"ativo": False}).eq("id", slug).execute()
                logging.warning(f"[sync_projects] ⚠️ Projeto desativado (pasta removida): {slug}")

        logging.info(
            f"[sync_projects] Sync concluído. "
            f"FS={len(fs_slugs)} módulos | "
            f"Inseridos={len(to_insert)} | "
            f"Desativados={len(to_deactivate)}"
        )

    except Exception as e:
        # Non-blocking: falha no sync não impede o boot da aplicação
        logging.error(f"[sync_projects] Falha na sincronização de projetos (non-fatal): {e}")
