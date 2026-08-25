-- =========================================================================
-- ESQUEMA DE TABELAS SUPABASE POSTGRESQL PARA O PROJETO P1+2 (AGENDHA)
-- Execute este script no SQL Editor do Supabase para criar as tabelas Cloud.
-- =========================================================================

-- 1. Beneficiários do P1+2
CREATE TABLE IF NOT EXISTS public.p12_beneficiarios (
    id BIGSERIAL PRIMARY KEY,
    nome_completo TEXT,
    nome_familiar TEXT,
    cpf TEXT,
    cpf_familiar TEXT,
    nis TEXT,
    rg TEXT,
    telefone TEXT,
    municipio TEXT NOT NULL,
    comunidade TEXT,
    territorio TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    status_validacao TEXT DEFAULT 'Pendente',
    grh TEXT,
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 2. Monitoramentos (GAPA, SISMA, INTERCÂMBIO)
CREATE TABLE IF NOT EXISTS public.p12_monitoramentos (
    id BIGSERIAL PRIMARY KEY,
    tipo TEXT NOT NULL, -- 'GAPA', 'SISMA', 'INTERCAMBIO'
    titulo TEXT NOT NULL,
    descricao TEXT,
    data_evento DATE,
    municipio TEXT,
    comunidade TEXT,
    responsavel TEXT,
    participantes_ids JSONB DEFAULT '[]'::jsonb,
    qtd_participantes INTEGER DEFAULT 0,
    anexos JSONB DEFAULT '[]'::jsonb,
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 3. Configuração de Colunas do Plano Produtivo
CREATE TABLE IF NOT EXISTS public.p12_plano_produtivo_config (
    id BIGSERIAL PRIMARY KEY,
    chave_coluna TEXT UNIQUE NOT NULL,
    titulo_coluna TEXT NOT NULL,
    tipo_coluna TEXT DEFAULT 'texto',
    ordem INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 4. Dados e Células da Planilha do Plano Produtivo
CREATE TABLE IF NOT EXISTS public.p12_plano_produtivo_dados (
    id BIGSERIAL PRIMARY KEY,
    beneficiario_id BIGINT REFERENCES public.p12_beneficiarios(id) ON DELETE SET NULL,
    nome_beneficiario TEXT,
    municipio TEXT,
    comunidade TEXT,
    status_parcela_1 TEXT DEFAULT 'Pendente',
    status_parcela_2 TEXT DEFAULT 'Pendente',
    observacoes TEXT,
    campos_dinamicos JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 5. Cronograma e Metas Semanais de Execução Física
CREATE TABLE IF NOT EXISTS public.p12_cronograma_execucao (
    id BIGSERIAL PRIMARY KEY,
    municipio TEXT NOT NULL,
    semana_referencia INTEGER DEFAULT 1,
    ano INTEGER DEFAULT 2026,
    meta_planejada INTEGER DEFAULT 0,
    qtd_executada INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Em Andamento',
    observacoes TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 6. Repositório de Documentos do P1+2
CREATE TABLE IF NOT EXISTS public.p12_documentos (
    id BIGSERIAL PRIMARY KEY,
    nome_documento TEXT NOT NULL,
    categoria TEXT DEFAULT 'Geral',
    nome_arquivo TEXT NOT NULL,
    caminho_arquivo TEXT NOT NULL,
    data_upload TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    tamanho_bytes BIGINT DEFAULT 0
);

-- 7. Cotações Master
CREATE TABLE IF NOT EXISTS public.p12_cotacoes_master (
    id BIGSERIAL PRIMARY KEY,
    codigo_cotacao TEXT UNIQUE NOT NULL,
    titulo TEXT NOT NULL,
    descricao TEXT,
    categoria TEXT DEFAULT 'Materiais',
    status TEXT DEFAULT 'Em Elaboração',
    prazo_limite DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 8. Itens de Cotação
CREATE TABLE IF NOT EXISTS public.p12_cotacao_itens (
    id BIGSERIAL PRIMARY KEY,
    cotacao_master_id BIGINT REFERENCES public.p12_cotacoes_master(id) ON DELETE CASCADE,
    item_nome TEXT NOT NULL,
    unidade TEXT DEFAULT 'UN',
    quantidade DOUBLE PRECISION DEFAULT 1,
    valor_unitario_estimado DOUBLE PRECISION DEFAULT 0.0,
    valor_total_estimado DOUBLE PRECISION DEFAULT 0.0,
    fornecedor_vencedor TEXT
);

-- Habilitar RLS e Políticas Permissivas para a Chave Anon
ALTER TABLE public.p12_beneficiarios ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Permitir Acesso Geral p12_beneficiarios" ON public.p12_beneficiarios FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE public.p12_monitoramentos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Permitir Acesso Geral p12_monitoramentos" ON public.p12_monitoramentos FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE public.p12_plano_produtivo_config ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Permitir Acesso Geral p12_plano_produtivo_config" ON public.p12_plano_produtivo_config FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE public.p12_plano_produtivo_dados ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Permitir Acesso Geral p12_plano_produtivo_dados" ON public.p12_plano_produtivo_dados FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE public.p12_cronograma_execucao ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Permitir Acesso Geral p12_cronograma_execucao" ON public.p12_cronograma_execucao FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE public.p12_documentos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Permitir Acesso Geral p12_documentos" ON public.p12_documentos FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE public.p12_cotacoes_master ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Permitir Acesso Geral p12_cotacoes_master" ON public.p12_cotacoes_master FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE public.p12_cotacao_itens ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Permitir Acesso Geral p12_cotacao_itens" ON public.p12_cotacao_itens FOR ALL USING (true) WITH CHECK (true);