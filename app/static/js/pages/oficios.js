let modalOficio;

document.addEventListener('DOMContentLoaded', function () {
    const modalEl = document.getElementById('modalOficio');
    if (modalEl) {
        if (typeof bootstrap !== 'undefined') {
            modalOficio = new bootstrap.Modal(modalEl);
        } else {
            console.warn('Bootstrap não carregado. O modal de ofício não funcionará.');
        }

        // Reset form when modal closes
        modalEl.addEventListener('hidden.bs.modal', function () {
            document.getElementById('formOficio').reset();
            document.getElementById('oficio_id').value = '';
            document.getElementById('modalTitulo').innerHTML = '<i class="bi bi-file-earmark-plus-fill me-2"></i><span>Novo Ofício</span>';
            document.getElementById('formOficio').classList.remove('was-validated');
        });
    }

    // Submit handler
    const form = document.getElementById('formOficio');
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            if (!form.checkValidity()) {
                e.stopPropagation();
                form.classList.add('was-validated');
                return;
            }

            const id = document.getElementById('oficio_id').value;
            const isEdit = !!id;
            const url = isEdit ? `/oficios/${id}` : '/oficios';
            const method = isEdit ? 'PUT' : 'POST';

            const formData = new FormData(form);
            // Corrige o bug do numero_oficio vazio virar null na API se necessário, ou deixa o backend tratar

            try {
                if (window.ui && window.Swal) Swal.showLoading();

                const response = await fetch(url, {
                    method: method,
                    body: formData
                });

                if (response.ok) {
                    modalOficio.hide();

                    // No reload, apenas feedback ou recarregar tabela se fosse SPA. 
                    // Como é template rendering, reload é aceitável, mas o user pediu feedback com timer.
                    // O timer do feedbackSucesso já faz reload se passar callback? 
                    // No ui_utils.js geralmente feedbackSucesso(msg, callback).

                    ui.feedbackSucesso(
                        isEdit ? 'Ofício atualizado com sucesso!' : 'Ofício registrado com sucesso!',
                        () => window.location.reload()
                    );
                } else {
                    const err = await response.json();
                    ui.feedbackErro(`Erro: ${err.detail || 'Falha ao salvar'}`);
                }
            } catch (error) {
                console.error('Erro:', error);
                ui.feedbackErro('Erro de conexão com o servidor.');
            }
        });
    }
});

// Tornar global para acesso no HTML
window.abrirModalNovoOficio = function () {
    if (modalOficio) modalOficio.show();
    else ui.feedbackErro('Erro: Componente de modal não inicializado.');
};

window.abrirModalEdicaoOficio = function (btn) {
    const data = btn.dataset;

    document.getElementById('oficio_id').value = data.id;
    document.getElementById('numero_oficio').value = data.numero || '';
    document.getElementById('destinatario').value = data.destinatario;
    document.getElementById('data_envio').value = data.data;
    document.getElementById('motivo_descricao').value = data.motivo;

    document.getElementById('modalTitulo').innerHTML = '<i class="bi bi-pencil-square me-2"></i><span>Editar Ofício</span>';

    if (modalOficio) modalOficio.show();
    else ui.feedbackErro('Erro: Componente de modal não inicializado.');
};

window.excluirOficio = function (id) {
    ui.confirmarExclusao(
        `/oficios/${id}`,
        'Ofício',
        () => window.location.reload()
    );
};
