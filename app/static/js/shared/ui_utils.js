/**
 * UI Utilities - Wrapper para SweetAlert2 e funções comuns de Interface.
 * Deve ser incluído no base.html após o SweetAlert2.
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
                    console.error(e);
                    ui.feedbackErro('Erro de conexão com o servidor.');
                }
            };
        }

        const modalEl = document.getElementById('modalExcluirPadrao');
        if (!modalEl) return;

        // Atualizar Textos
        modalEl.querySelector('.modal-title').textContent = titulo;
        modalEl.querySelector('.modal-body p').innerHTML = msg;

        const btnConfirmar = document.getElementById('btnConfirmarExclusao');
        if (btnConfirmar) {
            // Técnica de Clonagem para Resetar Listeners (Erradica Injeção e Duplicidade)
            const novoBtn = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(novoBtn, btnConfirmar);

            novoBtn.addEventListener('click', async function(e) {
                e.preventDefault();
                const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
                modalInstance.hide();
                if (callback) await callback();
            });
        }

        const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
        modalInstance.show();
    },

    /**
     * Exibe um modal de confirmação para ações genéricas.
     * Wrapper para confirmarGeneric para manter compatibilidade simples.
     */
    confirmar: function(titulo, texto, callback, confirmText = 'Sim') {
        ui.confirmarGeneric(callback, titulo, texto, confirmText);
    },

    /**
     * Exibe um modal de confirmação genérico.
     */
    confirmarGeneric: function(callback, titulo = "Confirmação", htmlMsg = "Tem certeza?", confirmText = "Confirmar") {
        const modalEl = document.getElementById('modalConfirmacaoGenerico');
        if (!modalEl) return;

        // Atualizar Textos/Header
        const header = document.getElementById('modalConfirmacaoGenericoHeader');
        if (header) {
             header.className = 'modal-header text-white bg-primary'; // Reset para padrão azul
        }
        
        document.getElementById('modalConfirmacaoGenericoTitle').textContent = titulo;
        document.getElementById('modalConfirmacaoGenericoBody').innerHTML = htmlMsg;
        
        const btnConfirmar = document.getElementById('btnConfirmarGenerico');
        if (btnConfirmar) {
            btnConfirmar.textContent = confirmText;
            
            // Clonagem para limpar bindings antigos
            const novoBtn = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(novoBtn, btnConfirmar);

            novoBtn.addEventListener('click', async function(e) {
                e.preventDefault();
                bootstrap.Modal.getOrCreateInstance(modalEl).hide();
                if (callback) await callback();
            });
        }

        bootstrap.Modal.getOrCreateInstance(modalEl).show();
    },

    /**
     * Exibe um Toast ou Popup de sucesso.
     * @param {string} mensagem - Mensagem a ser exibida.
     * @param {function} callback - Função opcional a ser executada após fechar.
     */
    feedbackSucesso: (mensagem, callback) => {
        Swal.fire({
            icon: 'success',
            title: 'Sucesso!',
            text: mensagem,
            timer: 2000,
            showConfirmButton: false
        }).then(() => {
            if (callback) callback();
        });
    },

    /**
     * Exibe um Popup de erro.
     * @param {string} mensagem - Mensagem a ser exibida.
     */
    feedbackErro: (mensagem) => {
        Swal.fire({
            icon: 'error',
            title: 'Ops...',
            text: mensagem
        });
    },

    /**
     * Exibe um Popup de informação.
     * @param {string} mensagem - Mensagem a ser exibida.
     */
    feedbackInfo: (mensagem) => {
        Swal.fire({
            icon: 'info',
            title: 'Informação',
            text: mensagem
        });
    }
};

window.ui = ui;
