# Projeto Cisterna Deivi e Atualização Chicão - Água que Alimenta

## Objetivo
Renomear a exibição do projeto atual para "Chicão - Água que Alimenta", criar o módulo do novo projeto "Cisterna Deivi" com gestão de beneficiários e geração automática dos termos de recibo com a assinatura digitalizada da coordenadora geral Luciene Marilac.

## Tarefas
- [x] 1. Renomeação visual: Atualizar o card no Hub (`admin_hub.html`) e na barra de navegação (`base.html`) para "Chicão - Água que Alimenta" → Verificar: Visualização na página do Hub e no topo.
- [x] 2. Integração de Assets: Copiar assinatura de Luciene Marilac e modelos de recibos da pasta SEADES para o projeto (`app/static/imagens/` e módulo `cisterna_deivi`) → Verificar: Arquivos acessíveis localmente e em deploy.
- [x] 3. Banco de Dados: Criar tabela `cisterna_beneficiarios` no banco de dados (`app/core/database.py`) com campos `id`, `nome_completo`, `cpf`, `municipio`, `comunidade`, `data_cadastro`, `status` → Verificar: Inicialização do schema sem erros.
- [x] 4. Módulo Backend Cisterna Deivi: Criar estrutura `app/modules/cisterna_deivi` (`models.py`, `routers/beneficiarios.py`, `views.py`) e registrar no `app/main.py` → Verificar: Rotas `/cisterna-deivi` e `/api/cisterna-deivi/*` respondendo 200.
- [x] 5. Hub e Navegação: Adicionar card moderno com tema próprio para "Cisterna Deivi" na Central de Operações (`admin_hub.html`) e link correspondente → Verificar: Card clicável redirecionando para a área do projeto.
- [x] 6. Frontend de Beneficiários: Criar template `app/templates/cisterna_deivi/beneficiarios.html` com listagem, busca, modal de cadastro rápido (Nome, CPF, Município, Comunidade) e ações de termos → Verificar: Inclusão e listagem de beneficiário funcional.
- [x] 7. Gerador de Termos & Assinatura: Criar rotas e templates de impressão para:
  - Termo 1: Recibo de Contribuição à Família (Construção 16m³ e Cozinheira - R$ 1.180,00)
  - Termo 2: Recibo de Contribuição à Família (Água para abastecimento e cura - R$ 200,00)
  - Termo 3: Termo com inserção automática da assinatura da coordenadora geral Luciene Marilac
  → Verificar: Botão "Emitir Termo" preenche os dados do beneficiário e formata em padrão A4 pronto para impressão/PDF.
- [x] 8. Testes e Validação: Testar fluxo completo de ponta a ponta (cadastro de beneficiário, geração dos termos, exibição das assinaturas) → Verificar: Execução limpa sem erros 500 ou quebras de layout.

## Critérios de Conclusão (Done When)
- [x] O projeto "Água que Alimenta" exibe visualmente o nome "Chicão - Água que Alimenta" no card e cabeçalho.
- [x] O card "Cisterna Deivi" está ativo no Hub de Projetos.
- [x] É possível cadastrar beneficiários com Nome e CPF (e Município/Comunidade).
- [x] Os recibos e termos são gerados automaticamente com os dados do beneficiário e a assinatura de Luciene Marilac posicionada.
