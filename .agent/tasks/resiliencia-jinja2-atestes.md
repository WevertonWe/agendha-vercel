# Task: Resiliência contra Erros de Sintaxe (Jinja2) - Gerador de Atestes

## 🎯 Objetivo
Configurar o ambiente Jinja2 para ser tolerante a strings no documento Word que usem chaves `{ }` mas não sejam variáveis válidas, evitando falhas catastróficas na renderização.

## 🛠️ Alterações Realizadas

### 1. Backend: `app/modules/bahia_sem_fome/routers/atestes.py`
- [x] Importação de `DebugUndefined` da biblioteca `jinja2`.
- [x] Configuração do ambiente Jinja2 com `undefined=DebugUndefined`.
- [x] Garantia de que variáveis não reconhecidas ou erros de sintaxe (ex: `{ B29 }`) sejam ignorados e impressos como texto puro.
- [x] Verificação do escope: variável `mapa` passada corretamente para `doc.render()`.

## 🧪 Verificação
- [x] Lint Check: PASSED.
- [x] Test Runner: PASSED.
- [x] Resiliência: Verificado que o motor não trava ao encontrar chaves que não fazem parte do mapeamento de contexto.

## 📜 Regras Aplicáveis
- P0 (GEMINI.md)
- agendha_specific.md
