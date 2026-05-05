import logging
import os
from passlib.context import CryptContext
from app.config import settings

# --- DEBUG AUDIT (Handshake 2025) ---
print(f"DEBUG: VERCEL_ENV_VAR: {os.getenv('VERCEL')}")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_connection(request=None): 
    """Conexão por requisição (Hard-Locked for Production)"""
    if os.getenv("VERCEL"):
        # Bloqueio total de SQLite em produção
        raise RuntimeError("CRITICAL: SQLite is disabled in production. Use Supabase SDK!")
        
    # Fallback apenas para DEV LOCAL
    import sqlite3
    from app.database.wrapper import AuditConnection
    conexao = AuditConnection(os.path.join(os.getcwd(), "agendha.db"), check_same_thread=False)
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.row_factory = sqlite3.Row
    
    try:
        yield conexao
    finally:
        conexao.close()
    
    # Try to set user context if request is provided and has user
    try:
        if request and hasattr(request, "state") and hasattr(request.state, "user"):
            user = request.state.user
            # Assuming user is dict or object with username or id
            user_id = user.get("username") if isinstance(user, dict) else getattr(user, "username", "SYSTEM")
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
    """Busca todos os registros de uma tabela Supabase com paginação recursiva para evitar limite de 1000"""
    supabase = get_supabase()
    all_data = []
    page_size = 1000
    start = 0

    while True:
        end = start + page_size - 1
        try:
            res = supabase.table(table_name).select(select_query).range(start, end).execute()
            if not res.data:
                break
            all_data.extend(res.data)
            if len(res.data) < page_size:
                break
            start += page_size
        except Exception as e:
            logging.error(f"Erro ao fazer fetch_all na tabela {table_name}: {e}")
            break

    return all_data


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
