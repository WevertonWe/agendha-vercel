# Task: Correção de Sintaxe no Mapeamento (docxtpl) - Gerador de Atestes

## 🎯 Objetivo
Garantir que as chaves do dicionário de contexto (`mapa`) não contenham delimitadores `{ }`, permitindo olookup correto pelo motor Jinja2 dentro do `docxtpl`.

## 🛠️ Alterações Realizadas

### 1. Backend: `app/modules/bahia_sem_fome/routers/atestes.py`
- [x] Renomeação da variável de contexto de `contexto` para `mapa` para maior clareza.
- [x] Remoção de todos os delimitadores `{` e `}` das chaves do dicionário.
- [x] Garantia de que a rotina de limpeza de floats (`.0`) utiliza a nova variável `mapa`.
- [x] Verificação final da renderização: `doc.render(mapa, jinja_env)`.

## 🧪 Verificação
- [x] Lint Check: PASSED.
- [x] Test Runner: PASSED.
- [x] Integridade de dados: Mapeamento limpo confirmado.

## 📜 Regras Aplicáveis
- P0 (GEMINI.md)
- agendha_specific.md
