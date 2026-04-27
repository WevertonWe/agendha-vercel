# Task: Atualização do Mapeamento do Gerador de Atestes BSF

## 🎯 Objetivo
Atualizar o loop de geração de atestes em `atestes.py` para utilizar a nova coluna "Comunidade" e aprimorar o tratamento da string do Município.

## 🛠️ Alterações Necessárias

### 1. Backend: `app/modules/bahia_sem_fome/routers/atestes.py`
- [x] Analisar mapeamento atual.
- [x] Atualizar a lógica de limpeza do Município para garantir UPPERCASE e remoção de códigos numéricos (ex: "Paulo Afonso-2924009" -> "PAULO AFONSO").
- [x] Atualizar o dicionário `mapa` para incluir as chaves com `{}` (ex: `{nome_beneficiario}`).
- [x] Mapear a nova coluna `{COMUNIDADE}` utilizando a coluna simplificada da planilha.
- [x] Garantir que `substituir_texto` continue verificando parágrafos e tabelas.

## 🧪 Verificação
- [x] Validar se as chaves no código coincidem com as tags no template Word.
- [x] Executar script de linting e testes básicos.

## 📜 Regras Aplicáveis
- P0 (GEMINI.md)
- agendha_specific.md
