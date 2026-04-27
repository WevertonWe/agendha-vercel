# 📌 Project Backlog & Roadmap

## 📅 Próxima Sessão: Refino de UI & Correção de Fluxos (Prioridade Máxima)

### 1. 🎨 UI/UX: Fim dos Alertas e Conforto Visual
- [ ] **Substituir Alerts**: Remover definitivamente `window.alert()` de `beneficiarios.js` e substituir por Modais Bootstrap ou Toasts (Toastify/SweetAlert).
- [ ] **Maximização de Espaço (Revisão)**: Garantir que o modal `modal-xl` ocupe de fato 95% da tela (width/height) em todas as resoluções.
- [ ] **Simplificação da Lista**: Refinar ainda mais a lista da esquerda (Remove padding desnecessário, fonte menor, ícones de status compactos) para maximizar "Nomes por Pixel".

### 2. 🐛 Correção Crítica: Importação Individual
- [ ] **Fix "Importar Este"**: Debugar por que as vezes o salvamento individual falha ou não atualiza a UI.
- [ ] **Feedback de Sucesso**: Implementar toast/notificação sutil ("Salvo com sucesso") ao invés de travar a tela.
- [ ] **Estado Visual**: Marcar imediatamente o item como `[IMPORTADO]` (Check Verde + Opacidade 50% + Disable Inputs) sem precisar recarregar a lista inteira.

### 3. 🧠 Inteligência de Planejamento (Abaré)
- [ ] **Sincronização Real-Time**: Garantir que ao importar um beneficiário na Curadoria, ele apareça imediatamente na tela de "Planejamento Abaré" sem delay.
- [ ] **Dashboard Operacional**: Ajustar layout dos cards (Novos, Em Construção, Concluídos) para melhor visualização.
- [ ] **PDF Financeiro**: Corrigir layout do PDF de solicitação de recursos para assinatura (Campos de data, valor total, e lista de beneficiários atendidos).

### 4. 📅 Novo Módulo: Planejamento e Cronogramas
- [ ] **Estrutura de Dados**: Criar tabelas para `Cronogramas` (Data, Local, Tipo de Evento, Responsável).
- [ ] **Tela de Gestão**: Criar `cronogramas.html` com calendário ou lista de eventos.
- [ ] **Integração GRH**: Permitir agendar eventos de "Assinatura de GRH" vinculados a múltiplos beneficiários.


### 5. 🛠️ Manutenção e Scripts
- [ ] **Validar Scripts**: Validar se todos os scripts movidos continuam operacionais dentro da pasta app/scripts/ (Tarefa para amanhã).
- [ ] **Validar Iniciar Sistema**: Verificar se o arquivo `iniciar_sistema.bat` ainda funciona perfeitamente com a nova estrutura.

---

## 🚀 Backlog Futuro / Em Espera

### Fase 3: Integração Avançada
- [ ] **Comparativo de Cotações**: Tela de análise de vencedores.
- [ ] **Fila de Validação**: Implementar aprovação visual (Status colorido) para gestores.
- [ ] **Integração com Mapas**: Visualizar cronograma de visitas no mapa.
