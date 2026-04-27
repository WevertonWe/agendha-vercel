# 🗺️ Inventário Completo do Projeto "Agendha" (Code Diagnosis)

**Data do Relatório:** 2026-02-12
**Agente Responsável:** Code Archeologist

---

---

## 📚 Documentação & Padrões (Meta-Docs)

| Arquivo | Classificação | Conteúdo |
|---|---|---|
| **[docs/PROTOCOLS.md](PROTOCOLS.md)** | 🔴 **Crítico - Leitura Obrigatória** | Regras de Blindagem JS, UI Safety e Backend Nulls. |
| `docs/INVENTORY.md` | Informativo | Mapa do sistema e diagnóstico. |

## 1. Mapeamento de Portais e Módulos

O sistema é uma aplicação FastAPI modular, servindo múltiplos "portais" ou áreas funcionais.

### Módulos Ativos (Rotas em `main.py`)

| Módulo | Rota Base | Diretório de Templates | Status & Estilo UI |
|---|---|---|---|
| **Core (Auth/Admin)** | `/`, `/login` | `templates/admin` | Login centralizado, estilo Bootstrap padrão. |
| **Água que Alimenta** | `/agua` | `templates/agua` | **Legado**. Usa Modais/Toasts embutidos no HTML (Bootstrap 5 nativo). |
| **Bahia Sem Fome** | `/bsf` | `templates/bahia-sem-fome` | **Moderno**. Padronizado com `ui_utils.js` (SweetAlert2). |
| **Financeiro** | `/financeiro` | `templates/financeiro` | **Híbrido**. Usa `ui_utils.js` mas mantém alguns `alert()` e CSS customizado (`card-custom`). |
| **Ofícios** | `/admin/oficios` | `templates/admin` | **Moderno**. Padronizado com `ui_utils.js`. |
| **Fornecedores** | `/fornecedores` | `templates/fornecedores` | Cadastro central. UI a verificar. |
| **Materiais** | `/materiais` | `templates/materiais` | Base de produtos. UI a verificar. |
| **Projetos (Hub)** | `/projetos` | `templates/projetos` | Hub central. |
| **Mapa Interativo** | `/mapa` | `templates/mapa` | Visualização geoespacial (Leaflet?). |
| **Audit Log** | `/admin/auditoria` | `templates/admin` | Dashboard de auditoria. |

---

## 2. Estrutura de Dados (SQLite)

O banco de dados `agendha.db` é inicializado em `app.core.database.init_db`.
**Nota Crítica:** Não existe um diretório `app/models`. Os modelos Pydantic e esquemas SQL estão dispersos.

### Tabelas Principais (Core Schema)
- **Acesso:** `users`, `user_project_roles`.
- **Administrativo:** `oficios`, `fornecedores`, `materiais`.
- **Financeiro:** `financeiro_projetos`, `financeiro_rubricas`, `financeiro_lancamentos`.
- **Bahia Sem Fome (BSF):** `bsf_metas` (Cubo), `bsf_atividades`, `bsf_visitas` (Principal), `bsf_metas_tecnicos`.
- **Água que Alimenta (AQA):** Tabelas **NÃO** estão no `init_db`. Provavelmente criadas via script sql direto ou migrações antigas.
  - *Risco:* Dificuldade em replicar o ambiente do zero sem um dump do banco.

---

## 3. Funcionalidades de Suporte (Infraestrutura)

- **UI Utils (`ui_utils.js`):**
  - Wrapper global para SweetAlert2 (`ui.feedbackSucesso`, `ui.confirmarExclusao`).
  - **Status:** Padrão ouro para interação. Deve ser expandido para todos os módulos.
- **Database Wrapper (`AuditConnection`):**
  - Intercepta `INSERT/UPDATE/DELETE` para gerar logs automáticos na tabela `audit_logs`.
  - Excelente infraestrutura de rastreabilidade (Desfazer ações disponível no Admin).
- **Middleware de Auditoria:**
  - Registra navegação (`GET`) de usuários autenticados.
- **Autenticação:**
  - JWT + Passlib. Centralizado no Core. Middleware de decodificação manual para logs.
- **Backup:**
  - Agendado (Cron 23h) via `APScheduler`. Módulo dedicado em `app/modules/backup`.

---

## 4. Diagnóstico de Saúde

### 🔴 Dívida Técnica (Otimização Prioritária)
1.  **Inconsistência Visual (UI/UX):**
    -   **Problema:** O módulo **Água que Alimenta** (`beneficiarios.html`) carrega ~100 linhas de HTML morto (Toasts/Modais genéricos) em cada página. O módulo **Financeiro** mistura estilos.
    -   **Solução:** Refatorar para usar `ui_utils.js` e remover HTML duplicado (como feito no BSF).
2.  **Modelos Ocultos:**
    -   **Problema:** Tabelas do AQA não estão no `init_db`. Se apagar o `agendha.db`, o sistema AQA quebra.
    -   **Solução:** Incorporar CREATE TABLEs do AQA no `init_db` ou criar sistema de migração real (Alembic).
3.  **Variações de CSS:**
    -   Financeiro usa classes `btn-custom-primary` enquanto outros usam `btn-primary` (Bootstrap padrão). Isso cria dissonância visual.

### 🟢 Pontos Fortes
1.  **Arquitetura Modular:** A separação em `app/modules` é excelente. Permite refatorar um módulo sem quebrar outro.
2.  **Auditoria:** O sistema de logs é robusto e integrado ao banco. Poucos sistemas legados têm isso.
3.  **Performance:** Uso de SQLite com DataTables no frontend garante velocidade mesmo com muitos registros (paginação server-side detectada em AQA).

---

## 5. Status de Integração

| Recurso | Nível de Integração | Obs |
|---|---|---|
| **Login** | ✅ Total | `users` único. |
| **Logs** | ✅ Total | `audit_logs` centralizado. |
| **UI** | ⚠️ Parcial | BSF/Ofícios (Novo) vs AQA (Antigo). |
| **Banco** | ⚠️ Parcial | Core Schema define BSF/Financeiro/Admin. AQA desconhecido. |

---

## Próximos Passos (Plano de Ação)

1.  **Code Archeology AQA:** Descobrir onde estão as queries `CREATE TABLE` do Água que Alimenta.
2.  **Refatoração UI (Lote 2):** Aplicar a "Unificação Visual" (SweetAlert2) no módulo **Água que Alimenta** (maior ganho de limpeza de código).
3.  **Padronização CSS:** Remover `btn-custom` do Financeiro e alinhar com Design System do BSF/Ofícios.
