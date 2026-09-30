# 🏛️ Agendha System - Arquitetura de Software

> **Plataforma Inteligente de Gestão Integrada, Auditoria Documental e Extração com IA.**

---

## 🗺️ 1. Visão Geral do Sistema

O Agendha é uma aplicação fullstack baseada em **Python (FastAPI)**, hospedada de forma serverless na **Vercel** e conectada ao **Supabase (PostgreSQL 15 + Storage)**, integrando motores avançados de **IA (Google Gemini 2.5/3.5)** e APIs de coleta de campo (**Coletum v2**).

```mermaid
graph TD
    Client([Navegador / Dispositivo Móvel]) -->|HTTPS / REST API| Vercel[Vercel Serverless (Região gru1)]
    Vercel --> FastAPI[FastAPI Core Engine (Python 3.12)]
    
    subgraph Módulos de Domínio
        FastAPI --> BSF[Bahia Sem Fome: Beneficiários, Atestes, Coletum v2]
        FastAPI --> AQA[Água que Alimenta: Fila de Validação, OCR de Campo]
        FastAPI --> FIN[Financeiro: Metas, Etapas, Rubricas e Lançamentos]
        FastAPI --> COT[Cotações & Materiais: Extrator Gemini AI]
        FastAPI --> P12[P1+2: Monitoramento & Documentação]
        FastAPI --> ADM[Admin: Auditoria, Credenciais PowerBI, Dispositivos]
    end

    BSF & AQA & FIN & COT & P12 & ADM --> Supabase[(Supabase PostgreSQL + pg_trgm + unaccent)]
    BSF & AQA & COT --> Gemini[Google Gemini AI Engine (Cascade Fallback)]
    BSF --> ColetumAPI[Coletum WebService API v2]
```

---

## 🧩 2. Módulos e Responsabilidades

### 1. `app/modules/bahia_sem_fome/` (BSF)
- **Beneficiários:** Gestão cadastral com busca inteligente trigram, paginação server-side e cache em memória (TTL 5 min).
- **Atestes & Atividades:** Geração dinâmica de atestes em DOCX/PDF, categorização de atividades e verificação de conformidade.
- **Coletum v2:** Cruzamento automatizado com respostas de formulários de campo, detecção de divergências de grafia (fuzzy matching) e inconsistências de datas.
- **Renomeador em Lote:** Processamento assíncrono paralelo com controle de concorrência (`asyncio.Semaphore`).

### 2. `app/modules/financeiro/`
- **Hierarquia:** `Projeto ➔ Metas ➔ Etapas ➔ Rubricas ➔ Lançamentos`.
- **Performance:** Consultas agregadas em batch (`.in_()`), eliminando gargalos N+1.
- **Dashboard:** Visão executiva em tempo real de saldo programado vs executado com percentual de conclusão.

### 3. `app/modules/agua_que_alimenta/` (AQA)
- **Fila de Validação:** Recepção de fotos de fichas físicas e processamento assistido por IA.
- **Pedreiros & Conferencia:** Monitoramento de medições de obras e conferência com planilhas Excel.

### 4. `app/modules/cotacoes/`
- **Extrator de Preços via IA:** Upload de propostas em PDF/imagem com extração estruturada de itens, CNPJs, fornecedores e valores unitários.

---

## 🤖 3. Motor de Inteligência Artificial (Google Gemini)

O sistema utiliza a biblioteca oficial `google-genai` com estratégia de **Cascata de Fallback**:
1. `gemini-2.5-flash` (Principal, ultrarrápido com raciocínio multimodal)
2. `gemini-2.5-flash-lite` (Fallback rápido e econômico)
3. `gemini-3.5-flash` / `gemini-3.5-flash-lite` (Geração avançada)
4. `gemini-3.1-pro-preview` (Casos de alta complexidade analítica)

---

## 🛡️ 4. Segurança, Observabilidade e CI/CD

- **Headers de Defesa:** `X-Content-Type-Options`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection`, `Referrer-Policy`.
- **Healthcheck:** `/healthz` e `/api/healthz` para monitoramento de liveness/readiness.
- **CI Pipeline:** Workflow automatizado no GitHub Actions (`.github/workflows/ci.yml`) validando sintaxe, rotas e 100% da suíte de testes em cada PR/commit.
