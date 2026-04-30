-- ============================================================
-- MASTER SUPABASE SETUP — Agendha Cloud
-- ============================================================
-- Arquivo único e idempotente (IF NOT EXISTS em tudo).
-- Execute no SQL Editor do Supabase Dashboard.
-- Ordem: Extensions → Core Tables → Auth Tables → App Tables → Indexes → RLS
-- ============================================================


-- ============================================================
-- 0. EXTENSÕES NECESSÁRIAS
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_cron";   -- Para TTL automático de audit_logs


-- ============================================================
-- 1. TABELAS CORE — AUTENTICAÇÃO E USUÁRIOS
-- ============================================================

-- Tabela de Usuários (espelho do SQLite local para ambiente cloud)
CREATE TABLE IF NOT EXISTS users (
    id            UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    username      TEXT        UNIQUE NOT NULL,
    password_hash TEXT        NOT NULL,
    full_name     TEXT,
    role          TEXT        NOT NULL DEFAULT 'user', -- 'admin' | 'user' | 'viewer'
    is_active     BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  users IS 'Usuários do sistema Agendha. Migrado do SQLite local.';
COMMENT ON COLUMN users.role IS 'Role global: admin = acesso total, user = acesso padrão, viewer = somente leitura.';


-- ============================================================
-- 2. TABELA DE PROJETOS
-- ============================================================

-- Projetos/Módulos do sistema (sincronizado com app/modules/)
CREATE TABLE IF NOT EXISTS projetos (
    id          TEXT        PRIMARY KEY,           -- Slug do módulo: 'agua_que_alimenta', 'financeiro', etc.
    nome        TEXT        NOT NULL,              -- Nome de exibição: 'Água que Alimenta'
    descricao   TEXT,
    ativo       BOOLEAN     NOT NULL DEFAULT TRUE,
    pasta_fisica TEXT,                             -- Caminho relativo em app/modules/
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  projetos IS 'Catálogo de módulos/projetos do sistema. Sincronizado com app/modules/ via sync_projects().';
COMMENT ON COLUMN projetos.id IS 'Slug único do módulo (ex: agua_que_alimenta). Espelha o nome da pasta física.';

-- Seed inicial dos projetos ativos (insert idempotente)
INSERT INTO projetos (id, nome, descricao, ativo, pasta_fisica) VALUES
    ('agua_que_alimenta', 'Água que Alimenta', 'Gestão de beneficiários do Projeto Água que Alimenta', TRUE, 'app/modules/agua_que_alimenta'),
    ('bahia_sem_fome',    'Bahia Sem Fome',    'Atestes, renomeador e documentação BSF',              TRUE, 'app/modules/bahia_sem_fome'),
    ('cotacoes',          'Cotações',          'Extração e gestão de cotações via IA',                TRUE, 'app/modules/cotacoes'),
    ('dashboard',         'Dashboard',         'Painel de indicadores e KPIs',                        TRUE, 'app/modules/dashboard'),
    ('financeiro',        'Financeiro',        'Lançamentos, rubricas e plano de trabalho',           TRUE, 'app/modules/financeiro'),
    ('fornecedores',      'Fornecedores',      'Cadastro e gestão de fornecedores',                   TRUE, 'app/modules/fornecedores'),
    ('mapa',              'Mapa Interativo',   'Pontos georreferenciados e shapes',                   TRUE, 'app/modules/mapa'),
    ('materiais',         'Materiais',         'Controle de materiais e insumos',                     TRUE, 'app/modules/materiais'),
    ('oficios',           'Ofícios',           'Geração e gestão de ofícios',                         TRUE, 'app/modules/oficios'),
    ('planejamento',      'Planejamento',      'Cronograma e planejamento de atividades',             TRUE, 'app/modules/planejamento'),
    ('projetos',          'Hub de Projetos',   'Hub central e sugestões de projetos',                 TRUE, 'app/modules/projetos')
ON CONFLICT (id) DO UPDATE SET
    nome        = EXCLUDED.nome,
    ativo       = EXCLUDED.ativo,
    pasta_fisica = EXCLUDED.pasta_fisica,
    updated_at  = NOW();


-- ============================================================
-- 3. RBAC — ROLES POR PROJETO (MULTI-TENANCY)
-- ============================================================

CREATE TABLE IF NOT EXISTS user_project_roles (
    id         BIGSERIAL   PRIMARY KEY,
    user_id    UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id TEXT        NOT NULL REFERENCES projetos(id) ON DELETE CASCADE,
    role       TEXT        NOT NULL DEFAULT 'viewer', -- 'admin' | 'editor' | 'viewer'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, project_id)
);

COMMENT ON TABLE  user_project_roles IS 'RBAC granular por projeto. Define o que cada usuário pode fazer em cada módulo.';
COMMENT ON COLUMN user_project_roles.role IS 'viewer=leitura, editor=leitura+escrita, admin=acesso total ao projeto.';

-- Índice de performance para lookup de permissões por usuário
CREATE INDEX IF NOT EXISTS idx_upr_user_id    ON user_project_roles (user_id);
CREATE INDEX IF NOT EXISTS idx_upr_project_id ON user_project_roles (project_id);


-- ============================================================
-- 4. TABELA DE AUDITORIA
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id           BIGSERIAL   PRIMARY KEY,
    user_id      TEXT        NOT NULL DEFAULT 'SYSTEM',
    acao         TEXT        NOT NULL,
    modulo       TEXT        NOT NULL DEFAULT 'core',
    tabela       TEXT,
    registro_id  TEXT,
    detalhes     JSONB       NOT NULL DEFAULT '{}',
    ip           TEXT,
    user_agent   TEXT,
    ia_tokens    INTEGER     DEFAULT 0,
    ia_modelo    TEXT,
    duracao_ms   INTEGER,
    nivel        TEXT        NOT NULL DEFAULT 'INFO',
    timestamp    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id   ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_modulo    ON audit_logs (modulo);
CREATE INDEX IF NOT EXISTS idx_audit_logs_acao      ON audit_logs (acao);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_nivel     ON audit_logs (nivel);
CREATE INDEX IF NOT EXISTS idx_audit_logs_errors
    ON audit_logs (timestamp DESC)
    WHERE nivel IN ('ERROR', 'CRITICAL');

COMMENT ON TABLE audit_logs IS 'Log de auditoria centralizado — ações críticas, erros e uso de IA.';


-- ============================================================
-- 5. FILA DE VALIDAÇÃO OCR
-- ============================================================

CREATE TABLE IF NOT EXISTS ocr_fila_validacao (
    id           TEXT        PRIMARY KEY,
    dados        JSONB       NOT NULL DEFAULT '{}',
    data_criacao TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ocr_fila_validacao IS 'Fila persistente de validação OCR. Substitui /tmp/fila_validacao.json.';


-- ============================================================
-- 6. ROW LEVEL SECURITY (RLS)
-- ============================================================

-- audit_logs: apenas service_role
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_full_access_audit" ON audit_logs;
CREATE POLICY "service_role_full_access_audit" ON audit_logs
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ocr_fila_validacao: apenas service_role
ALTER TABLE ocr_fila_validacao ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_full_access_ocr" ON ocr_fila_validacao;
CREATE POLICY "service_role_full_access_ocr" ON ocr_fila_validacao
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- projetos: leitura pública (qualquer autenticado), escrita apenas service_role
ALTER TABLE projetos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "projetos_read_auth" ON projetos;
CREATE POLICY "projetos_read_auth" ON projetos
    FOR SELECT TO authenticated USING (true);
DROP POLICY IF EXISTS "projetos_write_service" ON projetos;
CREATE POLICY "projetos_write_service" ON projetos
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- user_project_roles: apenas service_role
ALTER TABLE user_project_roles ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "upr_service_role" ON user_project_roles;
CREATE POLICY "upr_service_role" ON user_project_roles
    FOR ALL TO service_role USING (true) WITH CHECK (true);


-- ============================================================
-- 7. TTL AUTOMÁTICO DE AUDIT LOGS VIA pg_cron
-- ============================================================
-- Remove logs com mais de 7 dias todo dia às 03:00 UTC.
-- Requer extensão pg_cron habilitada (disponível no Supabase Pro).
-- Se não disponível, use a Edge Function supabase/functions/purge-audit-logs/.

SELECT cron.schedule(
    'purge-audit-logs-daily',
    '0 3 * * *',
    $$ DELETE FROM audit_logs WHERE timestamp < NOW() - INTERVAL '7 days'; $$
)
WHERE NOT EXISTS (
    SELECT 1 FROM cron.job WHERE jobname = 'purge-audit-logs-daily'
);


-- ============================================================
-- FIM — Verificação de integridade
-- ============================================================
DO $$
BEGIN
    ASSERT (SELECT COUNT(*) FROM projetos) >= 11,
        'FALHA: Tabela projetos deve ter pelo menos 11 registros após seed.';
    RAISE NOTICE '✅ Master Supabase Setup executado com sucesso.';
END $$;
