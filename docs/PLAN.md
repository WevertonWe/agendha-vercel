# PLAN.md - Agendha Assets & Credentials Management Suite

Este plano descreve o fluxo de trabalho detalhado para a implementação das credenciais do PowerBI e inventário de dispositivos no Agendha.

---

## 🏗️ 1. Banco de Dados e Storage Layer

### PostgreSQL & SQLite DDL
Criar arquivo de migração contendo as definições de:
- `bsf_powerbi_credentials`:
  - `id` serial/integer primary key
  - `nome_projeto` varchar/text
  - `email_login` varchar/text
  - `senha` text (criptografada com Fernet)
  - `status` varchar/text default 'Ativo'
- `agendha_dispositivos`:
  - `id` serial/integer primary key
  - `tipo` varchar/text
  - `marca_modelo` varchar/text
  - `numero_serie_imei` varchar/text unique
  - `responsavel_atual` varchar/text
  - `status` varchar/text default 'Disponível'
  - `url_termo_pdf` text

### Supabase Storage
- Bucket privado: `termos-dispositivos`.
- Download seguro via URLs assinadas expiráveis (5 minutos).

---

## 💻 2. Backend (FastAPI Routers)

- **Helper de Criptografia:** `app/core/utils/crypto.py` com Fernet.
- **Roteador Dedicado:** `app/routers/admin_assets.py`.
- **Endpoints do PowerBI:**
  - `GET /api/admin/powerbi`
  - `GET /api/admin/powerbi/{id}/reveal` (Descriptografa)
  - `POST /api/admin/powerbi`
  - `PUT /api/admin/powerbi/{id}`
  - `DELETE /api/admin/powerbi/{id}`
- **Endpoints de Dispositivos:**
  - `GET /api/admin/dispositivos`
  - `GET /api/admin/dispositivos/{id}/termo-url` (Gera URL assinada)
  - `POST /api/admin/dispositivos`
  - `PUT /api/admin/dispositivos/{id}`
  - `DELETE /api/admin/dispositivos/{id}`
  - `POST /api/admin/dispositivos/{id}/upload-termo` (Upload binário ao bucket privado)

---

## 🎨 3. Frontend (UI/UX)

- **Abas de Usuários e PowerBI:** `app/templates/admin/usuarios.html` com Bootstrap 5 Nav-Tabs.
- **Interação do PowerBI:** `/static/js/pages/usuarios.js`.
  - Tabela com revelar senha mascarada com o ícone "olhinho".
  - Botão de cadastro e edição no `modalPowerBI`.
- **View de Dispositivos:** `app/templates/admin/dispositivos.html`.
  - Herda `base.html`
  - Layout limpo e moderno.
  - Tabela de inventário com os botões normais e o botão especial de "Upload Termo".
  - Ícone de PDF com link dinâmico curto ou botão de download em nova aba (`target="_blank"`).
- **Scripts de Dispositivos:** `/static/js/pages/dispositivos.js` gerenciando CRUD e upload direto.
- **Menu Lateral:** Inserir o link em `base.html` sob dropdown administrativo.

---

## 🧪 4. Validação & Deploy

- Rodar `python -m py_compile` em todo o projeto.
- Rodar scripts de UX e segurança do agente.
- Git commit padronizado: `feat(admin): implementa painel de credenciais PowerBI e inventario de dispositivos com upload de termos`
- Enviar com `git push origin main`.
