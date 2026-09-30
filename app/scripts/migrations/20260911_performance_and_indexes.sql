-- ============================================================
-- MIGRAÇÃO DE PERFORMANCE & ÍNDICES (2026-09-11)
-- Sistema: Agendha Platform (Supabase PostgreSQL)
-- ============================================================
-- Idempotente (pode ser executado múltiplas vezes com segurança).
-- ============================================================

-- 1. EXTENSÕES PARA BUSCA TEXTUAL AVANÇADA
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- 2. ÍNDICES DE ALTA PERFORMANCE (BENEFICIÁRIOS)
CREATE INDEX IF NOT EXISTS idx_beneficiarios_projeto_nome 
ON beneficiarios (projeto, nome_completo);

CREATE INDEX IF NOT EXISTS idx_beneficiarios_cpf 
ON beneficiarios (cpf);

CREATE INDEX IF NOT EXISTS idx_beneficiarios_caf 
ON beneficiarios (caf);

CREATE INDEX IF NOT EXISTS idx_beneficiarios_tec_mun_com 
ON beneficiarios (nome_tecnico, municipio, comunidade);

CREATE INDEX IF NOT EXISTS idx_beneficiarios_nome_trgm 
ON beneficiarios USING gin (nome_completo gin_trgm_ops);

-- 3. ÍNDICES PARA ATIVIDADES (BAHIA SEM FOME)
CREATE INDEX IF NOT EXISTS idx_bsf_atividades_ben_data 
ON bsf_atividades (beneficiario_id, data_atividade DESC);

CREATE INDEX IF NOT EXISTS idx_bsf_atividades_tipo_data 
ON bsf_atividades (tipo_atividade, data_atividade DESC);

-- 4. VIEW DE RESUMO DE CONFORMIDADE DOS BENEFICIÁRIOS (BSF)
CREATE OR REPLACE VIEW vw_bsf_resumo_beneficiarios AS
SELECT 
    b.id AS beneficiario_id,
    b.nome_completo,
    b.cpf,
    b.caf,
    b.municipio,
    b.comunidade,
    b.nome_tecnico,
    b.status,
    b.projeto,
    COUNT(a.id) AS total_atividades,
    COUNT(CASE 
        WHEN jsonb_array_length(COALESCE(a.link_ateste, '[]'::jsonb)) > 0 
         AND jsonb_array_length(COALESCE(a.link_colletum, '[]'::jsonb)) > 0 
        THEN 1 END) AS atividades_completas,
    COUNT(CASE 
        WHEN a.id IS NOT NULL AND jsonb_array_length(COALESCE(a.link_ateste, '[]'::jsonb)) = 0 
        THEN 1 END) AS pendencias_ateste,
    COUNT(CASE 
        WHEN a.id IS NOT NULL AND jsonb_array_length(COALESCE(a.link_colletum, '[]'::jsonb)) = 0 
        THEN 1 END) AS pendencias_coletum,
    MAX(a.data_atividade) AS ultima_atividade
FROM beneficiarios b
LEFT JOIN bsf_atividades a ON a.beneficiario_id = b.id
WHERE b.projeto = 'Bahia Sem Fome' OR b.projeto IS NULL
GROUP BY b.id, b.nome_completo, b.cpf, b.caf, b.municipio, b.comunidade, b.nome_tecnico, b.status, b.projeto;

COMMENT ON VIEW vw_bsf_resumo_beneficiarios IS 'View agregada de beneficiários e conformidade de atividades no BSF.';
