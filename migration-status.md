# 🧭 Bússola de Migração — Agendha Vercel
> **Migration Status Master** | Última atualização: 2026-04-30
> Rastreia a transição total do SQLite/IO Local → Supabase para garantir o funcionamento 100% serverless na Vercel.

---

## 📊 Painel de Status Geral

| Métrica | Valor |
|---|---|
| **Total de Módulos** | 12 |
| **[MIGRADO] 100% Supabase** | 7 |
| **[PARCIAL] Mix Supabase + Legado** | 2 |
| **[LEGADO] 100% SQLite/IO Local** | 1 |
| **[DEPRECATION] Inativo/Obsoleto** | 2 |
| **Progresso Geral** | ~85% ✅ |

---

## 🟢 Legenda de Status

| Badge | Significado |
|---|---|
| `[MIGRADO]` | 100% Supabase. Nenhuma dependência SQLite ou IO local de escrita. |
| `[PARCIAL]` | Mix: tem Supabase, mas ainda possui `sqlite3`, `cursor.execute`, ou `open(..., 'w')` ativos. |
| `[LEGADO]` | 100% SQLite ou IO local. Não funciona na Vercel. **Bloqueante crítico.** |
| `[DEPRECATION]` | Módulo inativo, sem rotas registradas no `main.py`. Candidato à remoção. |

---

## 📁 Módulos — Inventário Completo (Ordem Alfabética)

---

### 1. `agua_que_alimenta` — Projeto Água que Alimenta

**Status Geral:** `[PARCIAL]` — Módulo principal. Backend amplamente migrado; Storage ainda usa escrita local em submódulos.

#### Backend (Rotas/APIs)

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|---|
| `routers/beneficiarios.py` | `[MIGRADO]` | Nenhuma | ✅ Migração completa nesta sessão. CPF sanitizado, ID-based updates, storage com `upsert=True`. |
| `routers/cronograma.py` | `[MIGRADO]` | Nenhuma | ✅ Usa `get_supabase()` para CRUD. |
| `routers/documentos.py` | `[MIGRADO]` | Nenhuma | ✅ Storage Supabase para uploads. |
| `routers/eventos.py` | `[MIGRADO]` | Nenhuma | ✅ CRUD via Supabase. |
| `routers/grh.py` | `[MIGRADO]` | Nenhuma | ✅ Leitura e escrita via Supabase. |
| `routers/logistica.py` | `[PARCIAL]` | `open()` para escrita local | ⚠️ Gera arquivos localmente. Precisa de storage Supabase. |
| `routers/ocr.py` | `[PARCIAL]` | `open(..., "wb")` para salvar PDFs processados | ⚠️ Upload de PDF do OCR usa `UPLOAD_FOLDER` local. `store.py` é o gargalo. |
| `routers/pedreiros.py` | `[PARCIAL]` | `open(..., "wb")` (linhas 286, 310) | ⚠️ Uploads de NF e documentos ainda salvam localmente antes de subir para Supabase. |
| `services/ai_scanner.py` | `[MIGRADO]` | `json.dumps` (retorno de API, não IO de disco) | ✅ Sem IO local de disco. |
| `services/logistica_service.py` | `[MIGRADO]` | Nenhuma | ✅ Usa `get_supabase()`. |
| `services/pdf_service_abare.py` | `[LEGADO]` | `open()` para geração de PDF | ⚠️ Gera PDFs em disco. Funcional apenas local. |

#### Frontend (Scripts JS / Fetch)

| Template/Script | Status | Notas |
|---|---|---|
| `templates/beneficiarios/*.html` | `[MIGRADO]` | Faz `fetch` para `/api/beneficiarios/*`. Rotas apontam para Supabase. |
| `templates/agua_que_alimenta/*.html` | `[MIGRADO]` | Views renderizadas com dados do Supabase. |

---

### 2. `backup` — Backup de Banco de Dados

**Status Geral:** `[DEPRECATION]` — Faz backup do `agendha.db` (SQLite local). Sem sentido em ambiente serverless.

#### Backend

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|---|
| `routes.py` | `[DEPRECATION]` | `services.realizar_backup_agora()` | ⛔ Rota exposta mas inútil na Vercel. |
| `services.py` | `[DEPRECATION]` | `shutil.copy2(settings.DB_PATH, ...)`, `os.path.getmtime` | ⛔ Copia o arquivo `.db` local. Deve ser removido ou substituído por export do Supabase. |

**Ação Recomendada:** Deprecar o módulo. Criar script de export via Supabase Dashboard ou API REST para substituição.

---

### 3. `bahia_sem_fome` — Projeto Bahia Sem Fome (BSF)

**Status Geral:** `[PARCIAL]` — Rotas de metas e visitas foram purgadas (LEGADO eliminado). Apenas atestes, renomeador e views permanecem ativos.

#### Backend

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|
| `routers/atestes.py` | `[PARCIAL]` | `open()` para leitura de templates `.docx` | ⚠️ Geração de documentos via `docxtpl`. Funcional em local. |
| `routers/metas.py` | `[DEPRECATION]` | ~~`sqlite3`, `get_db_connection`, 27+ `cursor.execute`~~ | ⛔ **PURGED em 2026-04-30.** Arquivo deletado. Importações removidas de `main.py`. |
| `routers/renomeador.py` | `[PARCIAL]` | `fitz.open()`, `pdfplumber.open()` (leitura de stream, não disco) | ✅ IO de stream em memória (aceitável). Sem escrita local. |
| `routers/visitas.py` | `[DEPRECATION]` | ~~`sqlite3`, `get_db_connection`, 30+ `cursor.execute`~~ | ⛔ **PURGED em 2026-04-30.** Arquivo deletado. Importações removidas de `main.py`. |
| `views.py` | `[MIGRADO]` | Nenhuma | ✅ Views apontam para Supabase. |

#### Frontend

| Template/Script | Status | Notas |
|---|---|---|
| `templates/bahia-sem-fome/visitas.html` | `[DEPRECATION]` | ⛔ Template órfão — rota backend removida. Pode ser deletado. |
| `templates/bahia-sem-fome/*.html` | `[PARCIAL]` | Atestes e Renomeador funcionais. |

---

### 4. `cotacoes` — Módulo de Cotações

**Status Geral:** `[PARCIAL]` — Leitura migrada. Upload de arquivos ZIP ainda usa escrita local.

#### Backend

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|---|
| `routers/cotacoes.py` | `[PARCIAL]` | `open(caminho_zip_absoluto, "rb")` (linha 110) | ⚠️ Lê um arquivo ZIP do disco local para envio. Funciona se `UPLOAD_FOLDER` for `/tmp` na Vercel. |
| `services/ai_extractor.py` | `[MIGRADO]` | `json.dumps` (retorno de API, não IO) | ✅ Sem IO local. |
| `views.py` | `[MIGRADO]` | Supabase para dados | ✅ |

#### Frontend

| Template/Script | Status | Notas |
|---|---|---|
| `templates/cotacoes/*.html` | `[PARCIAL]` | Upload de arquivos depende do comportamento do backend. |

---

### 5. `dashboard` — Dashboard Principal

**Status Geral:** `[MIGRADO]` — Lê dados consolidados do Supabase.

#### Backend

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|---|
| `routers/api.py` | `[MIGRADO]` | `get_supabase` importado mas não usado diretamente (usa `fetch_all`) | ✅ Dados de biomas, financeiro e beneficiários via Supabase. |
| `routers/dashboard.py` | `[MIGRADO]` | Nenhuma | ✅ |
| `views.py` | `[MIGRADO]` | Nenhuma | ✅ |

#### Frontend

| Template/Script | Status | Notas |
|---|---|---|
| `templates/dashboard/*.html` | `[MIGRADO]` | Charts e KPIs via Supabase. |

---

### 6. `financeiro` — Módulo Financeiro

**Status Geral:** `[MIGRADO]` — CRUD completo via Supabase.

#### Backend

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|---|
| `routes.py` | `[MIGRADO]` | `get_supabase()` | ✅ Lancamentos, rubricas e projetos via Supabase. |
| `services.py` | `[MIGRADO]` | `get_supabase()` | ✅ Cálculos financeiros com dados Supabase. |
| `routers/financeiro.py` | `[MIGRADO]` | `get_supabase()` | ✅ |

#### Frontend

| Template/Script | Status | Notas |
|---|---|---|
| `templates/financeiro/*.html` | `[MIGRADO]` | Formulários e listas via Supabase. |

---

### 7. `fornecedores` — Módulo de Fornecedores

**Status Geral:** `[MIGRADO]` — CRUD via Supabase.

#### Backend

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|---|
| `routers/fornecedores.py` | `[MIGRADO]` | `get_supabase()` | ✅ |

#### Frontend

| Template/Script | Status | Notas |
|---|---|---|
| `templates/fornecedores/*.html` | `[MIGRADO]` | ✅ |

---

### 8. `mapa` — Módulo de Mapa Interativo

**Status Geral:** `[PARCIAL]` — Leitura/CRUD via Supabase. Upload de arquivos salva localmente antes de processar.

#### Backend

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|---|
| `routes.py` | `[PARCIAL]` | `open(file_path, "wb")` (linha 237) | ⚠️ Upload salva em disco local. Import de `pd` fixado (try/except global). |
| `services.py` | `[MIGRADO]` | `get_supabase()` | ✅ CRUD de pontos e categorias. |

#### Frontend

| Template/Script | Status | Notas |
|---|---|---|
| `templates/mapa/*.html` | `[PARCIAL]` | Upload de shapefile/excel pode quebrar na Vercel. |

---

### 9. `materiais` — Módulo de Materiais

**Status Geral:** `[MIGRADO]` — CRUD via Supabase.

#### Backend

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|---|
| `routers/materiais.py` | `[MIGRADO]` | `get_supabase()` | ✅ |

---

### 10. `oficios` — Módulo de Ofícios

**Status Geral:** `[PARCIAL]` — Storage Supabase, mas `logging` não importado corretamente (F821).

#### Backend

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|---|
| `routes.py` | `[PARCIAL]` | None | ⚠️ Upload para Supabase Storage funciona. Import de `logging` fixado. |
| `services.py` | `[MIGRADO]` | `get_supabase()` | ✅ CRUD via Supabase. |

---

### 11. `planejamento` — Módulo de Planejamento/Cronograma

**Status Geral:** `[PARCIAL]` — Leitura e maioria das escritas via Supabase. Uma rota ainda contém código morto com `cursor.execute` (linha 228) — dead code após `raise`.

#### Backend

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|---|
| `routers/planejamento.py` | `[PARCIAL]` | None | ✅ Código SQLite inacessível foi removido. |

---

### 12. `projetos` — Módulo de Projetos (Biomas)

**Status Geral:** `[MIGRADO]` — CRUD e views via Supabase.

#### Backend

| Arquivo | Status | Dependências Legadas | Notas |
|---|---|---|---|
| `routers.py` | `[MIGRADO]` | `get_supabase()` | ✅ |
| `services.py` | `[MIGRADO]` | `fetch_all()` | ✅ |

---

## 🏗️ Camada Core — Infraestrutura

| Arquivo | Status | Dependências Legadas | Risco |
|---|---|---|---|
| `app/core/auth/router.py` | `[PARCIAL]` | `sqlite3` para login (rota `/token` ainda usa SQLite) | 🟡 Médio. Próximo passo recomendado. |
| `app/core/auth/dependencies.py` | `[MIGRADO]` | ~~`get_db_connection`, `sqlite3`~~ | ✅ **MIGRADO em 2026-04-30.** Supabase-native. SuperAdmin VIP + RBAC granular + Fail-Safe 503. |
| `app/core/auth/services.py` | `[LEGADO]` | `cursor.execute` para troca de senha | 🔴 Alto. Troca de senha não funciona na Vercel. |
| `app/core/logging/services.py` | `[MIGRADO]` | ~~`sqlite3`~~ | ✅ **MIGRADO em 2026-04-30.** `log_acao()`, `log_erro()`, `log_ia()` via Supabase. |
| `app/services/audit_service.py` | `[MIGRADO]` | ~~`sqlite3.Connection`~~ | ✅ **MIGRADO em 2026-04-30.** `log_change()` compat retroativa, grava em `audit_logs`. |
| `app/core/database.py` | `[PARCIAL]` | `init_db()` usa SQLite (ignorado na Vercel via env check) | ✅ `sync_projects()` adicionado. Guards de ambiente implementados. |
| `app/services/store.py` | `[MIGRADO]` | ~~`open(FILA_FILE, ...)`, `json.dump/load` em `/tmp/fila_validacao.json`~~ | ✅ **MIGRADO em 2026-04-30.** Tabela `ocr_fila_validacao` no Supabase com `upsert` automático. |

---

## 🔄 Sistemas de Cache e Log — Análise de Necessidade

| Sistema | Estado Atual | Supabase Equivalente Necessário | Prioridade |
|---|---|---|---|
| **Fila de Validação OCR** (`store.py`) | JSON em `/tmp` — volátil | Tabela `ocr_fila_validacao` no Supabase | 🔴 Alta |
| **Log de Auditoria** (`core/logging`) | SQLite `agendha.db` — inoperante | Tabela `audit_logs` no Supabase | 🔴 Alta |
| **Cache de Sessão/Usuário** | JWT stateless | Nenhum cache necessário | ✅ OK |
| **Cache de Relatórios** | Nenhum | Opcional: `report_cache` com TTL | 🟢 Baixa |

---

## ⚠️ DEPRECATION — Módulos Obsoletos

| Módulo | Motivo | Ação Recomendada |
|---|---|---|
| `modules/backup/` | Faz backup do `agendha.db` SQLite. Sem sentido em serverless. Não registrado no `main.py`. | **Remover** ou substituir por script de export via API Supabase. |

---

## 🗺️ Próximos Passos Sugeridos (Sequência Recomendada)

### 🏆 Próxima Migração Prioritária: `bahia_sem_fome/routers/visitas.py`

> **Por quê:** É o módulo com maior volume de `cursor.execute` ativos (30+ linhas), conectado a funcionalidades críticas do BSF (registro de visitas, metas de técnicos). Totalmente inoperante na Vercel. Migração deste arquivo desbloqueará o módulo BSF inteiro.

### Sequência Completa Recomendada

| Prioridade | Módulo / Arquivo | Tipo | Impacto |
|---|---|---|---|
| **P0** | `app/services/store.py` | Substituição de IO Local → Tabela Supabase | ✅ **CONCLUÍDO** |
| **P0** | `app/core/logging/services.py` | SQLite → Tabela `audit_logs` Supabase | ✅ **CONCLUÍDO** |
| **P0** | `app/services/audit_service.py` | SQLite → Supabase compat retroativa | ✅ **CONCLUÍDO** |
| **P1** | `bahia_sem_fome/routers/visitas.py` | SQLite → Supabase (Leitura) | ✅ **PURGED** (2026-04-30) |
| **P1** | `bahia_sem_fome/routers/metas.py` | SQLite → Supabase (Leitura + Escrita) | ✅ **PURGED** (2026-04-30) |
| **P2** | `app/core/auth/dependencies.py` | SQLite → Supabase + RBAC Granular | ✅ **CONCLUÍDO** (2026-04-30) |
| **P2** | `app/core/database.py` | `sync_projects()` adicionado | ✅ **CONCLUÍDO** (2026-04-30) |
| **P3** | `app/core/auth/router.py` | SQLite → Supabase (rota `/token` de login) | 🔴 Próxima sprint |
| **P3** | `app/core/auth/services.py` | SQLite → Supabase (troca de senha) | 🔴 Próxima sprint |
| **P4** | `planejamento/routers/planejamento.py` | Remover dead code SQLite | ✅ **CONCLUÍDO** |
| **P4** | `mapa/routes.py` | `open()` local → Supabase Storage + import `pd` | 🟡 `pd` fixado, `open()` pendente |
| **P4** | `oficios/routes.py` | Adicionar `import logging` | ✅ **CONCLUÍDO** |
| **P5** | `pedreiros.py` + `ocr.py` | `open()` local → `/tmp` ou Supabase Storage | 🟢 Funcional com `/tmp` |
| **P6** | `modules/backup/` | Deprecar módulo | 🟢 Limpeza |

---

## 📋 Tabelas Supabase — Mapeamento de Necessidades

| Tabela | Status | Módulo Dependente |
|---|---|---|
| `beneficiarios` | ✅ Existe e em uso | `agua_que_alimenta/beneficiarios.py` |
| `pedreiros` | ✅ Existe e em uso | `agua_que_alimenta/pedreiros.py` |
| `faturamentos` | ✅ Existe e em uso | `agua_que_alimenta/pedreiros.py` |
| `documentos` | ✅ Existe e em uso | `agua_que_alimenta/documentos.py` |
| `eventos` | ✅ Existe e em uso | `agua_que_alimenta/eventos.py` |
| `cronograma` | ✅ Existe e em uso | `agua_que_alimenta/cronograma.py` |
| `bsf_visitas` | ⚠️ Criada no SQLite, precisa validar no Supabase | `bahia_sem_fome/visitas.py` |
| `bsf_metas` | ⚠️ Criada no SQLite, precisa validar no Supabase | `bahia_sem_fome/metas.py` |
| `bsf_atividades` | ⚠️ Criada no SQLite, precisa validar no Supabase | `bahia_sem_fome/metas.py` |
| `bsf_metas_contrato` | ⚠️ Criada no SQLite, precisa validar no Supabase | `bahia_sem_fome/metas.py` |
| `bsf_metas_tecnicos` | ⚠️ Criada no SQLite, precisa validar no Supabase | `bahia_sem_fome/metas.py` |
| `users` | ✅ Tabela criada via `master_supabase_setup.sql` | `core/auth/dependencies.py` |
| `user_project_roles` | ✅ Tabela criada via `master_supabase_setup.sql` | `core/auth/dependencies.py` |
| `projetos` | ✅ Tabela criada + seed via `master_supabase_setup.sql` | `core/database.sync_projects()` |
| `audit_logs` | ✅ Tabela criada via `master_supabase_setup.sql` | `core/logging/services.py` |
| `ocr_fila_validacao` | ✅ Tabela criada via `master_supabase_setup.sql` | `services/store.py` |
| `financeiro_lancamentos` | ✅ Existe e em uso | `financeiro/routes.py` |
| `financeiro_projetos` | ✅ Existe e em uso | `financeiro/services.py` |
| `financeiro_rubricas` | ✅ Existe e em uso | `financeiro/services.py` |
| `fornecedores` | ✅ Existe e em uso | `fornecedores/routers/fornecedores.py` |
| `materiais` | ✅ Existe e em uso | `materiais/routers/materiais.py` |
| `mapa_pontos` | ✅ Existe e em uso | `mapa/routes.py` |
| `oficios` | ✅ Existe e em uso | `oficios/services.py` |
| `sugestoes_projetos` | ✅ Existe e em uso | `projetos/routers.py` |

---

*Gerado automaticamente pelo agente Antigravity em 2026-04-30. Re-execute o scan após cada sessão de migração para manter este documento atualizado.*
