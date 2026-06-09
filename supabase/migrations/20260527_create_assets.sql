-- Migration: Create PowerBI Credentials and Devices tables
-- Created at: 2026-05-27

CREATE TABLE IF NOT EXISTS bsf_powerbi_credentials (
    id SERIAL PRIMARY KEY,
    nome_projeto VARCHAR(255) NOT NULL,
    email_login VARCHAR(255) NOT NULL,
    senha TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'Ativo' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agendha_dispositivos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(100) NOT NULL,
    marca_modelo VARCHAR(255) NOT NULL,
    numero_serie_imei VARCHAR(255) UNIQUE NOT NULL,
    responsavel_atual VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Disponível' NOT NULL,
    url_termo_pdf TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
