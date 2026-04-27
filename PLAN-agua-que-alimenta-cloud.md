# PLAN - Agendha Cloud: Água que Alimenta

## 1. Overview
**Objetivo:** Realizar um inventário de todas as funções existentes do módulo "Projeto Água que Alimenta" para garantir sua reutilização no novo ecossistema "Agendha Cloud". Além disso, planejar a estrutura de banco de dados (Supabase) contemplando as tabelas principais para a gestão do projeto: Beneficiários, Atividades, Técnicos e Validade de CAF.
**Contexto:** O Agendha Cloud busca unificar e modernizar as operações. O módulo "Água que Alimenta" possui uma forte carga de gestão de beneficiários, vistorias (GRH), integração de IA (OCR para listas de presença), geração de documentos (PDFs, KML) e gestão de técnicos/pedreiros.

## 2. Project Type
**BACKEND** (API / Banco de Dados / Supabase)

## 3. Success Criteria
- [ ] Inventário de funções mapeado e catalogado por domínio de negócio.
- [ ] Estrutura relacional do Supabase (tabelas, relacionamentos, chaves) desenhada e documentada.
- [ ] Migração do modelo mental do SQLite/Pydantic antigo para o padrão Supabase.
- [ ] Sem quebras de regras de nulidade ou consistência (Null Safety protocol).

## 4. Tech Stack
- **Database:** Supabase (PostgreSQL) com RLS (Row Level Security).
- **Backend:** Python (FastAPI) ou Edge Functions (Node/Hono) para acessar o Supabase, dependendo da evolução da stack.
- **Integração:** IA Scanner (Gemini OCR) e Gerador de Relatórios.

## 5. File Structure (Proposed for Cloud)
```
/app
 ├── /modules
 │   └── /agua_que_alimenta_cloud
 │       ├── /controllers       # Rotas da API
 │       ├── /services          # Regras de negócios e IA
 │       ├── /repositories      # Conexões com o SDK do Supabase
 │       └── /schemas           # Pydantic / Zod
```

## 6. Inventário de Funções (Herdadas do Água que Alimenta)

Abaixo estão catalogadas as funções existentes nos arquivos `.py` do módulo atual, para serem migradas/reutilizadas:

### 🧩 Domínio: Beneficiários (`routers/beneficiarios.py`)
- `get_beneficiarios`, `get_beneficiario_por_id`, `ver_perfil_beneficiario`
- `update_beneficiario`, `excluir_beneficiario`
- `confirmar_importacao_csv`, `comparar_importacao_csv`
- `upload_documento_beneficiario`, `upload_nota_fiscal`
- `desvincular_pedreiro`, `salvar_validacao`
- `exportar_beneficiarios_kml`, `gerar_relatorio_excel`, `gerar_analise_ia`
- `get_consolidado_atividades`, `get_municipios_unicos`
- Funções auxiliares: `fix_sync_cpf_familiar`, `find_column`, `get_val`, `check_diff`

### 🏗️ Domínio: Pedreiros e Faturamento (`routers/pedreiros.py`)
- `listar_pedreiros`, `criar_pedreiro`, `perfil_pedreiro`, `atualizar_pedreiro`
- `listar_producao_pedreiro`, `listar_pendentes_faturamento`
- `gerar_lote_faturamento`, `listar_historico_faturamentos`
- `upload_faturamento_nf`, `upload_faturamento_dam`, `estornar_lote_faturamento`

### 🤖 Domínio: IA e OCR (`routers/ocr.py`, `services/ai_scanner.py`)
- `configure_gemini`, `extrair_lista_presenca`
- `upload_e_processar_ocr`, `verificar_conferencia_excel`
- `listar_itens_pendentes`, `get_item_pendente_por_id`, `delete_item_pendente`
- `listar_historico_conferencias`, `get_historico_detalhe`, `excluir_historico`

### 📋 Domínio: GRH e Eventos (`routers/grh.py`, `routers/eventos.py`)
- `scan_lista_grh`, `vincular_grh_lote`, `buscar_beneficiario_manual`, `download_grh_documento`
- `criar_evento_grh`, `listar_eventos_grh`, `atualizar_evento_grh_form`, `atualizar_evento_grh_status`, `deletar_evento_grh`

### 🚚 Domínio: Logística e Cronograma (`routers/logistica.py`, `routers/cronograma.py`, `services/logistica_service.py`)
- `get_abare_candidates`, `calculate_logistics_preview`, `get_abare_preview`, `get_abare_pdf`
- `listar_itens_cronograma`, `get_item_cronograma_por_id`, `criar_item_cronograma`, `atualizar_item_cronograma`

### 📄 Domínio: Relatórios e Documentos (`routers/documentos.py`, `services/pdf_service_abare.py`)
- `listar_documentos`, `criar_documento`, `atualizar_documento`, `deletar_documento`
- `gerar_pdf_cotacao_logistica`
- Views HTML renderizadas (`views.py`): `get_mapa`, `get_graficos_page`, `get_tabela_completa`, etc.

## 7. Planejamento da Estrutura de Tabelas (Supabase)

A base foi pensada com PostgreSQL relacional em mente, aproveitando integridade referencial.

### Tabela `tecnicos`
Responsável por cadastrar os técnicos que visitam e atuam com os beneficiários.
- `id` (UUID, PK)
- `nome_completo` (VARCHAR)
- `cpf` (VARCHAR, Unique)
- `telefone` (VARCHAR, Nullable)
- `email` (VARCHAR, Nullable)
- `status` (VARCHAR) - Ex: 'Ativo', 'Inativo'
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

### Tabela `beneficiarios`
Cadastro principal do "Projeto Água que Alimenta".
- `id` (UUID, PK)
- `nome_completo` (VARCHAR)
- `cpf` (VARCHAR, Unique)
- `nis` (VARCHAR, Nullable)
- `data_nascimento` (DATE)
- `sexo` (VARCHAR)
- `escolaridade` (VARCHAR, Nullable)
- `municipio` (VARCHAR)
- `comunidade` (VARCHAR)
- `estado_uf` (VARCHAR, Default 'BA')
- `latitude` (VARCHAR/DECIMAL, Nullable)
- `longitude` (VARCHAR/DECIMAL, Nullable)
- `ref_localizacao` (TEXT, Nullable)
- `renda_media` (NUMERIC, Nullable)
- `status` (VARCHAR) - Ex: 'Ativo', 'Pendente'
- `tecnico_id` (UUID, FK -> `tecnicos.id`, Nullable)
- `grh` (VARCHAR, Nullable)
- `doc_status` (VARCHAR, Nullable)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

### Tabela `validade_caf`
Mantém o histórico e a situação atual da CAF (Cadastro Ambiental Rural / Cadastro de Agricultor Familiar). Separar em tabela própria evita problemas se o beneficiário emitir novas CAFs ao longo do tempo.
- `id` (UUID, PK)
- `beneficiario_id` (UUID, FK -> `beneficiarios.id`)
- `numero_caf` (VARCHAR, Unique, Nullable)
- `data_emissao` (DATE, Nullable)
- `data_validade` (DATE) - Data chave para alertas.
- `status` (VARCHAR) - Ex: 'Válida', 'Vencida', 'Em Processamento'
- `documento_url` (VARCHAR, Nullable) - Caminho no Storage do Supabase.
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

### Tabela `atividades`
Registro unificado de ações, vistorias (GRH) e visitas atreladas a beneficiários e técnicos.
- `id` (UUID, PK)
- `beneficiario_id` (UUID, FK -> `beneficiarios.id`)
- `tecnico_id` (UUID, FK -> `tecnicos.id`, Nullable)
- `tipo_atividade` (VARCHAR) - Ex: 'Visita Técnica', 'Entrega de Insumos', 'Validação OCR'
- `data_atividade` (DATE)
- `descricao` (TEXT, Nullable)
- `status` (VARCHAR) - Ex: 'Realizada', 'Pendente', 'Cancelada'
- `anexo_url` (VARCHAR, Nullable) - PDF/Imagem da atividade
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

## 8. Task Breakdown

| Task ID | Nome | Agente | Prioridade | Dependencies | Input → Output → Verify |
|---------|------|--------|------------|--------------|-------------------------|
| T01 | Criar Schema Supabase `tecnicos` e `beneficiarios` | `database-architect` | P0 | Nenhuma | Esquema SQL → Tabelas Criadas → Verificar FKs e Integridade no Supabase |
| T02 | Criar Schema Supabase `validade_caf` e `atividades` | `database-architect` | P0 | T01 | Esquema SQL → Tabelas Criadas → Verificar relacionamentos com `beneficiarios` |
| T03 | Criar Tipagem Typescript/Pydantic | `backend-specialist` | P1 | T02 | Modelos antigos → Modelos migrados → Validar com `tsc` ou `pydantic` |
| T04 | Migrar Funções de Beneficiários (CRUD e KML) | `backend-specialist` | P1 | T03 | Rotas FastAPI antigas → Repositórios Supabase → Testes unitários com mock db |
| T05 | Migrar Lógica de IA Scanner e OCR | `backend-specialist` | P1 | T03 | Funções Gemini → Serviço isolado Cloud → PDF parse via IA funcionando |
| T06 | Integrar View de Validacao CAF e GRH | `frontend-specialist` | P2 | T04, T05 | HTML antigo → UI Cloud → Filtros por validade CAF respondendo |

## 9. Phase X: Verification

- [ ] Socratic Gate check (OK, requisitos já mapeados e aprovados via este plano)
- [ ] Segurança: Políticas RLS (Row Level Security) definidas nas tabelas do Supabase
- [ ] Segurança: `security_scan.py` aprovado
- [ ] Lint/Type Check do backend aprovado
- [ ] Sem violações de "null safety" no mapeamento do banco

## ✅ PHASE X COMPLETE
(Aguardando Execução do T01 ao T06)
