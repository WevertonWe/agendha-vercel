/**
 * UI Utilities - Wrapper para SweetAlert2 e funções comuns de Interface.
 * Blindagem P1 contra ReferenceError em ambientes de conectividade intermitente.
 */

const ui = {
    /**
     * Exibe um modal de confirmação para exclusão.
     * Suporta assinatura legada (urlApi, itemNome, callbackSucesso) ou nova (callback, titulo, msg).
     */
    confirmarExclusao: function(arg1, arg2, arg3) {
        let callback, titulo, msg;

        if (typeof arg1 === 'function') {
            // Nova Assinatura: (callback, titulo, msg)
            callback = arg1;
            titulo = arg2 || "Confirmar Exclusão";
            msg = arg3 || "Tem a certeza de que deseja excluir este item? Esta ação não pode ser desfeita.";
        } else {
            // Assinatura Legada: (urlApi, itemNome, callbackSucesso)
            const urlApi = arg1;
            const itemNome = arg2 || "este item";
            const callbackSucesso = arg3;
            titulo = `Excluir ${itemNome}?`;
            msg = `Essa ação não pode ser desfeita e pode afetar registros dependentes.`;
            
            callback = async () => {
                try {
                    const token = localStorage.getItem('access_token');
                    const headers = { 'Content-Type': 'application/json' };
                    if (token) headers['Authorization'] = `Bearer ${token}`;

                    const res = await fetch(urlApi, { method: 'DELETE', headers: headers });
                    if (res.ok) {
                        ui.feedbackSucesso(`${itemNome} foi removido com sucesso.`);
                        if (callbackSucesso) callbackSucesso();
                        else window.location.reload();
                    } else {
                        let errorMsg = "Erro desconhecido.";
                        try { const err = await res.json(); errorMsg = err.detail || errorMsg; } catch (e) { }
                        ui.feedbackErro(`Falha ao excluir: ${errorMsg}`);
                    }
                } catch (e) {
                    console.error('Erro na requisição de exclusão:', e);
                    ui.feedbackErro('Erro de conexão com o servidor.');
                }
            };
        }

        const modalEl = document.getElementById('modalExcluirPadrao');
        if (!modalEl || typeof bootstrap === 'undefined') {
            // Fallback seguro caso o modal ou Bootstrap não estejam presentes
            if (confirm(`${titulo}\n\n${msg}`)) {
                if (callback) callback();
            }
            return;
        }

        // Atualizar Textos
        const titleEl = modalEl.querySelector('.modal-title');
        if (titleEl) titleEl.textContent = titulo;
        const msgEl = modalEl.querySelector('.modal-body p');
        if (msgEl) msgEl.innerHTML = msg;

        const btnConfirmar = document.getElementById('btnConfirmarExclusao');
        if (btnConfirmar) {
            // Técnica de Clonagem para Resetar Listeners (Erradica Injeção e Duplicidade)
            const novoBtn = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(novoBtn, btnConfirmar);

            novoBtn.addEventListener('click', async function(e) {
                e.preventDefault();
                if (typeof bootstrap !== 'undefined') {
                    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
                    if (modalInstance) modalInstance.hide();
                }
                if (callback) await callback();
            });
        }

        if (typeof bootstrap !== 'undefined') {
            const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
            if (modalInstance) modalInstance.show();
        }
    },

    /**
     * Exibe um modal de confirmação para ações genéricas.
     */
    confirmar: function(titulo, texto, callback, confirmText = 'Sim') {
        ui.confirmarGeneric(callback, titulo, texto, confirmText);
    },

    /**
     * Exibe um modal de confirmação genérico com proteção P1.
     */
    confirmarGeneric: function(callback, titulo = "Confirmação", htmlMsg = "Tem certeza?", confirmText = "Confirmar") {
        const modalEl = document.getElementById('modalConfirmacaoGenerico');
        if (!modalEl || typeof bootstrap === 'undefined') {
            if (confirm(`${titulo}\n\n${htmlMsg}`)) {
                if (callback) callback();
            }
            return;
        }

        // Atualizar Textos/Header
        const header = document.getElementById('modalConfirmacaoGenericoHeader');
        if (header) {
             header.className = 'modal-header text-white bg-primary';
        }
        
        const titleEl = document.getElementById('modalConfirmacaoGenericoTitle');
        if (titleEl) titleEl.textContent = titulo;
        const bodyEl = document.getElementById('modalConfirmacaoGenericoBody');
        if (bodyEl) bodyEl.innerHTML = htmlMsg;
        
        const btnConfirmar = document.getElementById('btnConfirmarGenerico');
        if (btnConfirmar) {
            btnConfirmar.textContent = confirmText;
            
            // Clonagem para limpar bindings antigos
            const novoBtn = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(novoBtn, btnConfirmar);

            novoBtn.addEventListener('click', async function(e) {
                e.preventDefault();
                if (typeof bootstrap !== 'undefined') {
                    const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
                    if (modalInstance) modalInstance.hide();
                }
                if (callback) await callback();
            });
        }

        if (typeof bootstrap !== 'undefined') {
            const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
            if (modalInstance) modalInstance.show();
        }
    },

    /**
     * Exibe um Toast ou Popup de sucesso.
     */
    feedbackSucesso: (mensagem, callback) => {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'success',
                title: 'Sucesso!',
                text: mensagem,
                timer: 2000,
                showConfirmButton: false
            }).then(() => {
                if (callback) callback();
            });
        } else {
            console.log('[SUCESSO]', mensagem);
            if (callback) callback();
        }
    },

    /**
     * Formata erros de validação do Pydantic/FastAPI ou respostas de exceção em texto amigável.
     * @param {string|object|Array} erro - Erro bruto retornado pelo backend.
     * @returns {string} Mensagem legível em português.
     */
    formatarErro: function(erro) {
        if (!erro) return "Ocorreu um erro inesperado.";
        if (typeof erro === 'string') return erro;

        if (erro.detail) {
            if (typeof erro.detail === 'string') {
                return erro.detail;
            }
            if (Array.isArray(erro.detail)) {
                // Erros de validação estruturados do Pydantic (HTTP 422)
                const mensagens = erro.detail.map(item => {
                    const campo = Array.isArray(item.loc) ? item.loc.filter(x => x !== 'body').join(' > ') : '';
                    const msg = item.msg || 'valor inválido';
                    return campo ? `• <strong>${campo}</strong>: ${msg}` : `• ${msg}`;
                });
                return mensagens.join('<br>');
            }
            if (typeof erro.detail === 'object') {
                try { return JSON.stringify(erro.detail); } catch (e) { return "Erro de validação."; }
            }
        }

        if (erro.message) return erro.message;
        try { return JSON.stringify(erro); } catch (e) { return "Erro na operação."; }
    },

    /**
     * Exibe um Popup de erro (com auto-formatação para erros Pydantic).
     */
    feedbackErro: function(mensagem) {
        const msgFormatada = ui.formatarErro(mensagem);
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Ops...',
                html: msgFormatada
            });
        } else {
            console.error('[ERRO]', msgFormatada);
        }
    },

    /**
     * Exibe um Popup de informação.
     */
    feedbackInfo: (mensagem) => {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'info',
                title: 'Informação',
                text: mensagem
            });
        } else {
            console.info('[INFO]', mensagem);
        }
    },

    /**
     * Exibe um Popup de aviso/alerta.
     */
    feedbackAviso: (mensagem) => {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'warning',
                title: 'Atenção',
                text: mensagem
            });
        } else {
            console.warn('[AVISO]', mensagem);
        }
    },

    /**
     * Alterna botão para estado de carregamento com spinner (Micro-interação UX).
     */
    setLoadingButton: (btnEl, loadingText = 'Processando...') => {
        if (!btnEl) return;
        btnEl.setAttribute('data-original-html', btnEl.innerHTML);
        btnEl.disabled = true;
        btnEl.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>${loadingText}`;
    },

    /**
     * Restaura botão ao estado original.
     */
    resetLoadingButton: (btnEl) => {
        if (!btnEl) return;
        const original = btnEl.getAttribute('data-original-html');
        if (original) {
            btnEl.innerHTML = original;
            btnEl.removeAttribute('data-original-html');
        }
        btnEl.disabled = false;
    },

    /**
     * Renderiza um Empty State visual rico e amigável.
     */
    renderEmptyState: (containerEl, titulo = 'Nenhum registro encontrado', subtitulo = '', iconClass = 'fa-search', actionHtml = '') => {
        if (!containerEl) return;
        containerEl.innerHTML = `
            <div class="text-center py-5 px-3">
                <div class="mb-3">
                    <div class="rounded-circle bg-light d-inline-flex align-items-center justify-content-center text-muted shadow-sm" style="width: 72px; height: 72px;">
                        <i class="fas ${iconClass} fa-2x opacity-50"></i>
                    </div>
                </div>
                <h6 class="fw-bold text-dark mb-1">${titulo}</h6>
                ${subtitulo ? `<p class="text-muted small mb-3" style="max-width: 400px; margin: 0 auto;">${subtitulo}</p>` : ''}
                ${actionHtml ? `<div class="mt-3">${actionHtml}</div>` : ''}
            </div>
        `;
    }
};

window.ui = ui;
