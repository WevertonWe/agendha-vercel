-- ============================================================
-- Schema: audit_logs (Supabase)
-- Sistema de Observabilidade Total — Agendha
-- ============================================================
-- Execute este script no SQL Editor do Supabase Dashboard
-- ou via migrations automatizadas.
-- ============================================================

-- 1. Tabela Principal de Auditoria
CREATE TABLE IF NOT EXISTS audit_logs (
    id           BIGSERIAL PRIMARY KEY,
    user_id      TEXT        NOT NULL DEFAULT 'SYSTEM',
    acao         TEXT        NOT NULL,           -- 'INSERT', 'UPDATE', 'DELETE', 'LOGIN', 'ERROR', 'IA_REQUEST'
    modulo       TEXT        NOT NULL DEFAULT 'core', -- ex: 'beneficiarios', 'financeiro', 'ocr'
    tabela       TEXT,                            -- nome da tabela afetada (opcional)
    registro_id  TEXT,                            -- ID do registro afetado (optional)
    detalhes     JSONB       NOT NULL DEFAULT '{}', -- payload livre: valor_antigo, valor_novo, ia_tokens, etc.
    ip           TEXT,
    user_agent   TEXT,
    ia_tokens    INTEGER     DEFAULT 0,           -- tokens consumidos em requisições IA (0 se não aplicável)
    ia_modelo    TEXT,                            -- modelo IA usado (ex: 'gemini-2.0-flash')
    duracao_ms   INTEGER,                         -- duração da requisição em ms (performance)
    nivel        TEXT        NOT NULL DEFAULT 'INFO', -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    timestamp    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Índices de Performance (queries frequentes)
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id    ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_modulo     ON audit_logs (modulo);
CREATE INDEX IF NOT EXISTS idx_audit_logs_acao       ON audit_logs (acao);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp  ON audit_logs (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_nivel      ON audit_logs (nivel);
-- Índice parcial para busca de erros críticos (query mais comum em alertas)
CREATE INDEX IF NOT EXISTS idx_audit_logs_errors
    ON audit_logs (timestamp DESC)
    WHERE nivel IN ('ERROR', 'CRITICAL');

-- 3. Row Level Security (RLS) — Apenas service_role pode inserir/ler
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Política: leitura permitida apenas para service_role (backend) e admins autenticados
CREATE POLICY "service_role_full_access" ON audit_logs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- 4. Comentários de documentação
COMMENT ON TABLE  audit_logs IS 'Log de auditoria centralizado — registra ações críticas, erros e uso de IA.';
COMMENT ON COLUMN audit_logs.detalhes IS 'Payload JSONB livre. Exemplos: {"valor_antigo": {...}, "valor_novo": {...}} ou {"ia_prompt_tokens": 150, "ia_completion_tokens": 80}';
COMMENT ON COLUMN audit_logs.ia_tokens IS 'Total de tokens consumidos em requisições de IA (soma de prompt + completion).';
COMMENT ON COLUMN audit_logs.duracao_ms IS 'Duração total da operação em milissegundos para análise de performance.';


-- ============================================================
-- Schema: ocr_fila_validacao (Supabase) — Se ainda não existir
-- ============================================================
CREATE TABLE IF NOT EXISTS ocr_fila_validacao (
    id           TEXT        PRIMARY KEY,
    dados        JSONB       NOT NULL DEFAULT '{}',
    data_criacao TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ocr_fila_validacao IS 'Fila persistente de validação OCR. Substitui o arquivo JSON local /tmp/fila_validacao.json.';
