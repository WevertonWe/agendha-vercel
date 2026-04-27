# Plano de Implementação: Gerador de Atestes BSF

Objetivo: Implementar funcionalidade de geração de documentos Word em lote a partir de planilhas para o projeto Bahia Sem Fome.

## 🛠 Atividades de Backend
- [ ] Instalar dependência `python-docx`.
- [ ] Criar roteador `app/modules/bahia_sem_fome/routers/atestes.py`.
- [ ] Implementar endpoint `POST /api/bsf/gerar-atestes`.
    - [ ] Processar Excel/CSV (Pandas).
    - [ ] Manipular Word Template (python-docx).
    - [ ] Gerar ZIP em memória (zipfile + io.BytesIO).
- [ ] Registrar roteador em `app/main.py`.

## 🎨 Atividades de Frontend
- [ ] Criar template `app/templates/bahia-sem-fome/gerador_atestes.html`.
    - [ ] Área de upload drag-and-drop.
    - [ ] Barra de progresso visual.
    - [ ] Botão de download de ZIP.
- [ ] Adicionar link no menu lateral/navegação (base_bsf.html ou similar).

## 🧪 Verificação & Qualidade
- [ ] Validar mapeamento de campos.
- [ ] Testar com planilha de exemplo.
- [ ] Executar `python .agent/scripts/checklist.py .`.

## 📌 Mapeamento de Campos
- `Dados do Grupo Familiar > Nome` -> `{nome_beneficiario}`
- `Dados do Grupo Familiar > CPF` -> `{cpf_beneficiario}`
- `DAP / CAF` -> `{caf_beneficiario}`
- `Dados de Execução > Nome do(a) técnico(a) responsável` -> `{nome_tecnico}`
- `Dados de Execução > CPF do(a) técnico(a) responsável` -> `{cpf_tecnico}`
- `Dados de Execução > Comunidade` -> `{COMUNIDADE}`
