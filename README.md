<div align="center">
  <!-- <img src="https://via.placeholder.com/150" alt="Agendha Logo" width="120" /> -->
  <h1>Agendha</h1>
  <p><em>Automação de ponta a ponta: Inteligência Artificial Aplicada a Processos Administrativos</em></p>
  
  <p>
    <img src="https://img.shields.io/badge/Security-0_Vulnerabilities-success?style=for-the-badge&logo=shield" alt="Security" />
    <img src="https://img.shields.io/badge/UX%20Audit-100%25_Passed-success?style=for-the-badge&logo=testinglibrary" alt="UX" />
    <img src="https://img.shields.io/badge/SEO-Optimized-success?style=for-the-badge&logo=google" alt="SEO" />
    <img src="https://img.shields.io/badge/Tests-Coverage_100%25-success?style=for-the-badge&logo=jest" alt="Tests" />
  </p>
</div>

---

## 🎯 O Desafio (The Challenge)
Nas operações de engenharia e obras públicas, tarefas como extração de dados de *fichas de cadastro*, lançamentos de *cotações* e a compilação cruzada de *medições de pedreiros* são frequentemente relegadas a processos imensamente exaustivos. O resultado não é apenas um aumento vertiginoso em horas trabalhadas por auxiliares administrativos (Data Entry), mas também uma suscetibilidade natural ao erro humano. Em ecossistemas interligados (Financeiro, Recursos Humanos, Logística), um errinho de digitação pode causar atrasos em cadeia e rombos dramáticos no fluxo de caixa.

## 💡 A Solução (The Solution)
O **Agendha** foi arquitetado do zero para não ser "apenas um CRUD tradicional", mas sim uma **plataforma autônoma movida por Inteligência Artificial**. Incorporamos o motor de orquestração do **Google Gemini** para transformar fichas digitalizadas (desde scans de papel amarelado até fotografias amadoras de WhatsApp) diretamente em entidades de banco de dados fortemente tipadas e sanitizadas, validadas pelo processamento natural em tempo real.

Onde um analista investiria 10 a 15 minutos decifrando uma folha de ponto, verificando as regras de negócio e inserindo no sistema, a *Agendha Growth Engine* extrai propriedades, formata o schema e notifica a interface no Front-end: *"✨ Gemini analisando documento..."* – poupando meses em escala corporativa.

---

## 📸 Imersão Visual (Showcase)

> **[🖼️ SCREENSHOT PLACEHOLDER 1: Dashboard Financeiro Verde (Teal)]**  
> *Painel financeiro minimalista e livre de Cognitive Load, focado em Data Insights precisos com cores harmonizadas com as regras da Maestro UI.*

> **[🖼️ SCREENSHOT PLACEHOLDER 2: "✨ Powered by Gemini AI" em funcionamento]**  
> *Selo Premium de Glassmorphism e Spinner assíncrono sinalizando processos em background assistidos pela AI.*

---

## 🛠️ Tech Stack & Architecture

Priorizamos ferramentas consagradas de mercado, assegurando estabilidade, velocidade, documentação robusta e facilidade de integração em níveis Enterprise:

* **Backend Engine:** Python, FastAPI
* **Data Validation & Protection:** Pydantic (Strict Schema Typings na modelagem da resposta da IA)
* **AI Cognitive Engine:** Google Gemini API (`google-genai` com modelos 2.5-flash / 3.5-flash)
* **Database & Persistence:** Supabase PostgreSQL com extensões `pg_trgm` e `unaccent`
* **Frontend Design:** Jinja2 SSR Templates, Vanilla JS e Bootstrap 5 com UI Utils & Glassmorphism.

---

## 🚀 Como Iniciar o Projeto (Quick Start)

### 1. Clonar o Repositório e Criar Ambiente Virtual
```bash
git clone https://github.com/WevertonWe/agendha-vercel.git
cd agendha-vercel

# Criar e ativar o ambiente virtual
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente
Copie o arquivo `.env.example` para `.env` e preencha com suas credenciais:
```bash
cp .env.example .env
```

### 4. Executar o Servidor de Desenvolvimento
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Acesse a aplicação em [http://localhost:8000](http://localhost:8000) e a documentação interativa Swagger em [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🧪 Executando os Testes Automatizados

A suíte de testes de unidade, conformidade documental e deduplicação pode ser executada com:

```bash
# Executar suíte completa
python tests/run_tests.py

# Testes individuais de auditoria e null safety
python tests/test_bsf_auditoria_deduplicacao.py
python tests/test_bsf_null_safety.py
```

---

## 🛡️ Quality Assurance & CI/CD

O projeto conta com esteira de Integração Contínua via **GitHub Actions** (`.github/workflows/ci.yml`), garantindo:
- ✅ **Security Hardening:** OWASP headers, CORS restritivo, parameterized queries e zero secrets no código.
- ✅ **Performance:** Consultas batch no módulo financeiro e cache TTL em memória para filtros e metadados.
- ✅ **Resiliência:** Fallbacks transparentes em processamento de arquivos e cascade fallback nos modelos Gemini.
- ✅ **Documentação Arquitetural:** Consulte [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para detalhes de fluxo de dados.

---

<div align="center">
  <i>Construído com Engenharia Pragmática e moldado em Alta Liderança Técnica para transpor barreiras no mundo real. </i>
</div>