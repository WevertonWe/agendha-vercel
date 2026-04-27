# 🛡️ Protocolos de Desenvolvimento Agendha

> **Status:** Obrigatório
> **Última Atualização:** 19/02/2026
> **Aplicação:** Todos os módulos (BSF, Financeiro, Ofícios, RH)

Este documento consolida as regras de ouro para desenvolvimento no projeto Agendha. A violação destes protocolos resultará na rejeição do PR ou da tarefa.

---

## 1. 🔐 Blindagem JavaScript (P1 - Crítico)

**Objetivo:** Prevenir "Tela Branca" ou travamento de scripts por dependências não carregadas.

### 1.1. Inicialização Segura (Bootstrap/Swal)
Proibido instanciar componentes globais sem verificação de existência.

**❌ INCORRETO:**
```javascript
const modal = new bootstrap.Modal(document.getElementById('meuModal'));
modal.show();
Swal.fire('Erro', 'Mensagem', 'error');
```

**✅ CORRETO:**
```javascript
if (typeof bootstrap !== 'undefined') {
    const el = document.getElementById('meuModal');
    if (el) {
        const modal = new bootstrap.Modal(el);
        modal.show();
    }
}

if (typeof Swal !== 'undefined') {
    Swal.fire('Erro', 'Mensagem', 'error');
} else {
    alert('Erro: Mensagem'); // Fallback aceitável apenas se Swal falhar
}
```

### 1.2. Feedback ao Usuário
Proibido usar `window.alert()` ou `console.log()` para feedback final.

*   **Sucesso:** `ui.feedbackSucesso(mensagem, [callback])`
*   **Erro:** `ui.feedbackErro(mensagem)`
*   **Confirmação:** `ui.confirmarExclusao(url, nomeItem, callback)`

---

## 2. 🏗️ Integridade de UI & Templates

**Objetivo:** Manter a consistência visual e evitar quebras de layout.

### 2.1. Herança Obrigatória
Nenhum arquivo `.html` pode ser órfão. Todos devem estender um template base.

```jinja2
{% extends "base.html" %} 
<!-- OU -->
{% extends "bahia-sem-fome/base_bsf.html" %}
```

### 2.2. Zero Gap Policy
O cabeçalho e a navegação devem ser `sticky-top`. Não deixar espaços em branco (gaps) entre o menu e o conteúdo.

### 2.3. Padrão Visual (Glassmorphism)
Dashboards e Cards de KPI devem usar a classe utilitária `.stat-card` e o efeito de hover:
```css
.stat-card:hover {
    transform: translateY(-5px);
    transition: transform 0.3s ease;
}
```

---

## 3. 📊 Segurança de Dados & Backend

**Objetivo:** Evitar erros 500 no render do Jinja2 e garantir formatação correta.

### 3.1. Tratamento de Nulos (Backend)
O Backend (Python/Flask) deve garantir que valores financeiros NUNCA sejam `None`.
*   **Errado:** `valor = None`
*   **Certo:** `valor = 0.0`

### 3.2. Formatação de Moeda (Frontend)
Sempre utilize o filtro Jinja2 customizado para exibir valores monetários.

**Uso:**
```jinja2
{{ valor_total | currency }}
<!-- Saída: R$ 1.250,00 -->
```

---

## 4. 🔄 Fluxo de Trabalho (Agentes)

1.  **Refactoring:** Antes de qualquer refatoração JS, aplicar o protocolo de **Blindagem (1.1)**.
2.  **Novo Módulo:** Começar estendendo `base.html` **(2.1)**.
3.  **Deploy:** Verificar logs por erros de template 500 causados por nulos **(3.1)**.
