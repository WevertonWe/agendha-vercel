# Task: Simplificação do Mapeamento de Município - Gerador de Atestes

## 🎯 Objetivo
Simplificar a extração do nome do Município no gerador de atestes, removendo a lógica de redundância e extração via split, utilizando a coluna direta da nova planilha.

## 🛠️ Alterações Realizadas

### 1. Backend: `app/modules/bahia_sem_fome/routers/atestes.py`
- [x] Simplificação da extração de `MUNICIPIO`: agora utiliza o valor direto da coluna sem realizar `split('-')`.
- [x] Padronização para UPPERCASE garantida via `.upper()`.
- [x] Mapeamento atualizado no dicionário `mapa`.

## 🧪 Verificação
- [x] Lint Check: PASSED.
- [x] Test Runner: PASSED.
- [x] Lógica: Verificado que a extração é direta e resiliente.

## 📜 Regras Aplicáveis
- P0 (GEMINI.md)
- agendha_specific.md
