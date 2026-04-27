-- Supabase Schema para Agendha
-- Arquivo gerado pelo Database Architect

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT true,
    full_name TEXT
);

CREATE TABLE user_project_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    project_id TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE pedreiros (
    id SERIAL PRIMARY KEY,
    nome_completo TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    telefone TEXT,
    endereco TEXT,
    status TEXT DEFAULT 'Ativo',
    dados_pagamento TEXT
);

CREATE TABLE faturamentos (
    id SERIAL PRIMARY KEY,
    pedreiro_id INTEGER NOT NULL REFERENCES pedreiros(id),
    valor_total NUMERIC DEFAULT 0.0,
    valor_dam NUMERIC DEFAULT 0.0,
    status_dam TEXT DEFAULT 'Pendente',
    arquivo_nf TEXT,
    arquivo_dam TEXT,
    data_criacao TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE beneficiarios (
    id SERIAL PRIMARY KEY,
    codigo TEXT,
    nome_tecnico TEXT,
    cpf_tecnico TEXT,
    municipio TEXT,
    comunidade TEXT,
    latitude TEXT,
    longitude TEXT,
    data_atividade DATE,
    nome_familiar TEXT,
    cpf_familiar TEXT,
    nis TEXT,
    renda_media TEXT,
    status TEXT,
    tecnico_agua_que_alimenta TEXT,
    doc_status TEXT,
    grh TEXT,
    verificado_bsf TEXT,
    nome_completo TEXT,
    sexo TEXT,
    data_nascimento DATE,
    cpf TEXT,
    escolaridade TEXT,
    ref_localizacao TEXT,
    estado_uf TEXT,
    pedreiro_id INTEGER REFERENCES pedreiros(id),
    status_pagamento TEXT DEFAULT 'PENDENTE',
    link_nota_fiscal TEXT,
    data_conclusao DATE,
    faturamento_id INTEGER REFERENCES faturamentos(id)
);

CREATE TABLE financeiro_entidades (
    id SERIAL PRIMARY KEY,
    tipo_pessoa TEXT,
    nome_razao_social TEXT NOT NULL,
    cpf_cnpj TEXT,
    funcao TEXT,
    municipio_atuacao TEXT,
    endereco_rua TEXT,
    endereco_numero TEXT,
    endereco_bairro TEXT,
    endereco_cidade TEXT,
    endereco_cep TEXT,
    contato_telefone TEXT,
    contato_email TEXT,
    dados_bancarios_banco TEXT,
    dados_bancarios_agencia TEXT,
    dados_bancarios_conta TEXT
);

CREATE TABLE financeiro_projetos (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    numero_contrato TEXT,
    data_inicio DATE,
    data_fim DATE,
    valor_total NUMERIC
);

CREATE TABLE financeiro_metas (
    id SERIAL PRIMARY KEY,
    projeto_id INTEGER REFERENCES financeiro_projetos(id),
    numero_meta TEXT,
    descricao TEXT
);

CREATE TABLE financeiro_etapas (
    id SERIAL PRIMARY KEY,
    meta_id INTEGER REFERENCES financeiro_metas(id),
    numero_etapa TEXT,
    descricao TEXT
);

CREATE TABLE financeiro_rubricas (
    id SERIAL PRIMARY KEY,
    etapa_id INTEGER REFERENCES financeiro_etapas(id),
    codigo TEXT,
    descricao TEXT,
    unidade TEXT,
    quantidade_programada NUMERIC,
    valor_unitario_programado NUMERIC,
    valor_total_programado NUMERIC
);

CREATE TABLE financeiro_lancamentos (
    id SERIAL PRIMARY KEY,
    projeto_id INTEGER REFERENCES financeiro_projetos(id),
    rubrica_id INTEGER REFERENCES financeiro_rubricas(id),
    entidade_id INTEGER REFERENCES financeiro_entidades(id),
    data_lancamento DATE,
    numero_processo TEXT,
    numero_nota_fiscal TEXT,
    historico TEXT,
    quantidade_executada NUMERIC,
    valor_total_executado NUMERIC
);

CREATE TABLE oficios (
    id SERIAL PRIMARY KEY,
    numero_oficio TEXT,
    destinatario TEXT NOT NULL,
    data_envio DATE NOT NULL,
    motivo_descricao TEXT,
    criado_por TEXT,
    caminho_arquivo TEXT
);

CREATE TABLE logs_acesso (
    id SERIAL PRIMARY KEY,
    data_hora TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    usuario TEXT,
    rota TEXT,
    metodo TEXT,
    ip_origem TEXT
);

CREATE TABLE mapa_pontos (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,
    latitude NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL,
    descricao TEXT,
    projeto_id INTEGER,
    poligono TEXT,
    cor TEXT,
    contexto TEXT DEFAULT 'geral',
    responsavel TEXT,
    status_beneficiario TEXT,
    verificacao_bsf BOOLEAN DEFAULT false,
    endereco TEXT
);

CREATE TABLE mapa_categorias (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    cor TEXT NOT NULL
);

CREATE TABLE historico_conferencias (
    id SERIAL PRIMARY KEY,
    municipio TEXT,
    data_criacao TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    resumo_json JSONB
);

CREATE TABLE cronograma_execucao (
    id SERIAL PRIMARY KEY,
    municipio TEXT NOT NULL,
    semana_referencia DATE NOT NULL,
    meta_planejada INTEGER DEFAULT 0,
    qtd_executada INTEGER DEFAULT 0,
    quant_cisternas INTEGER DEFAULT 0
);

CREATE TABLE cronograma_beneficiarios (
    id SERIAL PRIMARY KEY,
    cronograma_id INTEGER NOT NULL REFERENCES cronograma_execucao(id) ON DELETE CASCADE,
    beneficiario_id INTEGER REFERENCES beneficiarios(id), 
    pedreiro_id INTEGER REFERENCES pedreiros(id),
    data_execucao DATE
);

CREATE TABLE fornecedores (
    id SERIAL PRIMARY KEY,
    razao_social TEXT NOT NULL,
    nome_fantasia TEXT,
    cnpj_cpf TEXT UNIQUE,
    email TEXT,
    telefone TEXT,
    endereco TEXT
);

CREATE TABLE materiais (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    unidade TEXT NOT NULL,
    categoria TEXT,
    descricao TEXT
);

CREATE TABLE cotacoes_master (
    id SERIAL PRIMARY KEY,
    codigo_cotacao TEXT NOT NULL,
    titulo TEXT NOT NULL,
    descricao TEXT,
    data_criacao TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Aberto'
);

CREATE TABLE cotacao_itens (
    id SERIAL PRIMARY KEY,
    cotacao_master_id INTEGER NOT NULL REFERENCES cotacoes_master(id),
    material_id INTEGER NOT NULL REFERENCES materiais(id),
    quantidade NUMERIC NOT NULL
);

CREATE TABLE teste_persistencia (
    id SERIAL PRIMARY KEY,
    timestamp TEXT
);

CREATE TABLE sugestoes_projetos (
    id SERIAL PRIMARY KEY,
    projeto_id TEXT NOT NULL,
    usuario_id TEXT,
    sugestao TEXT NOT NULL,
    data_criacao TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Nova tabela de Logs de Auditoria
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    action TEXT NOT NULL,
    table_name TEXT,
    record_id TEXT,
    old_data JSONB,
    new_data JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
