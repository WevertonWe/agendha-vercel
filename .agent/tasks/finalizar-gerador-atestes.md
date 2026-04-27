# Task: Finalização do Gerador de Atestes (docxtpl) - Planilha Reduzida

## 🎯 Objetivo
Restaurar o ambiente padrão do `docxtpl` com chaves duplas `{{ }}` e ajustar o mapeamento para os nomes exatos das colunas da planilha reduzida.

## 🛠️ Alterações Realizadas

### 1. Backend: `app/modules/bahia_sem_fome/routers/atestes.py`
- [x] Remoção do ambiente Jinja2 customizado (retorno ao padrão `{{ variable }}`).
- [x] Implementação da função auxiliar `limpar_valor` para tratar `NaN` e floats `.0`.
- [x] Atualização do mapeamento para capturar colunas específicas:
  *   `MUNICIPIO`: Extraído da coluna `COMUNIDADE` (com limpeza de código numérico).
  *   `COMUNIDADE`: Extraído da coluna `Dados de Execução > Comunidade`.
  *   Demais campos mapeados conforme caminhos do grupo familiar/execução.
- [x] Limpeza técnica: Remoção de variáveis de busca flexível não utilizadas para satisfazer o Lint Check.

## 🧪 Verificação
- [x] Lint Check: PASSED.
- [x] Test Runner: PASSED.
- [x] Mapeamento: Confirmado que o dicionário de contexto atende exclusivamente à planilha reduzida do usuário.

## 📜 Regras Aplicáveis
- P0 (GEMINI.md)
- agendha_specific.md
