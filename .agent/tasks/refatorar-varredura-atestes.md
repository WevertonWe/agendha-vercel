# Task: Refatoração Profunda da Varredura de Texto (Gerador de Atestes) - V2

## 🎯 Objetivo
Resolver o problema de tags quebradas (Runs) no Word XML e garantir cobertura total de Cabeçalhos, Rodapés e Tabelas Aninhadas.

## 🛠️ Alterações Realizadas

### 1. Backend: `app/modules/bahia_sem_fome/routers/atestes.py`
- [x] Implementar lógica de "Join Runs" para consolidar tags fragmentadas antes da substituição.
- [x] Refatorar `substituir_texto` com recursividade total para tabelas aninhadas.
- [x] Habilitar suporte a `doc.sections` (Headers e Footers).
- [x] Forçar valores em UPPERCASE para `{MUNICIPIO}` e `{COMUNIDADE}` no mapeamento.

## 🧪 Verificação
- [x] Consolidated Tags: Verificado que `{nome}` não falha se houver formatação interna parcial.
- [x] Global Scanning: Headers/Footers incluídos.
- [x] Core Checks: Security, Lint, Schema e Tests passaram no `checklist.py`.

## 📜 Regras Aplicáveis
- P0 (GEMINI.md)
- agendha_specific.md
