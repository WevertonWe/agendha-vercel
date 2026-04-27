---
trigger: always_on
---

# 🗺️ Regras Específicas: Projeto Agendha

> Este protocolo deve ser lido por qualquer agente antes de modificar o código da Agendha.

## 🏗️ Template & UI Integrity
- **Herança Obrigatória:** Todo ficheiro `.html` funcional DEVE estender um template base (ex: `{% extends "base.html" %}` ou `{% extends "base_financeiro.html" %}`). Nunca criar páginas "órfãs".
- **Zero Gap Policy:** O header deve estar sempre colado ao topo (`sticky-top`) sem margens brancas entre o menu e o conteúdo.
- **Glassmorphism Style:** Dashboards devem usar a classe `.stat-card` com efeito `hover-lift` (`transform: translateY(-5px)`).

## 🛡️ JS & Feedback Protocol
- **Anti-ReferenceError:** Toda chamada a `bootstrap`, `Swal` ou `jQuery` deve ser protegida: 
  `if (typeof bootstrap !== 'undefined') { ... }`
- **Feedback Unificado:** Proibido o uso de `window.alert()`. Use obrigatoriamente `ui_utils.js`:
  - `ui.feedbackSucesso()` para confirmações.
  - `ui.confirmarExclusao()` para ações destrutivas.

## 📊 Backend & Data Safety
- **Filtro de Moeda:** Valores financeiros no Jinja2 devem sempre usar o filtro `| currency`.
- **Null Safety:** O backend (Python) deve garantir que valores nulos sejam passados como `0` ou `0.0` para evitar Erros 500 no template.