# Task: Migração para DocxTemplate (docxtpl) - Gerador de Atestes

## 🎯 Objetivo
Substituir a manipulação manual de Runs por uma engine de template robusta (docxtpl) para garantir integridade visual e funcional dos atestes.

## 🛠️ Alterações Realizadas

### 1. Ambiente & Dependências
- [x] Instalação da biblioteca `docxtpl` via pip.

### 2. Backend: `app/modules/bahia_sem_fome/routers/atestes.py`
- [x] Remoção das referências manuais ao `docx.Document`.
- [x] Remoção da função legada `substituir_texto`.
- [x] Implementação do `DocxTemplate` para renderização via contexto Jinja2.
- [x] Implementação de loop de limpeza de floats (`.0`) no dicionário de contexto.
- [x] Manutenção do tratamento de UPPERCASE para campos geográficos (`MUNICIPIO`, `COMUNIDADE`).

## 🧪 Verificação
- [x] Lint Check: PASSED.
- [x] Test Runner: PASSED.
- [x] Renderização: Verificado que a lógica de contexto utiliza chaves simples adequadas ao `{{ variable }}` do docxtpl.

## 📜 Regras Aplicáveis
- P0 (GEMINI.md)
- agendha_specific.md
