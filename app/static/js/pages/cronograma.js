document.addEventListener('DOMContentLoaded', () => {
    const API_URL = '/api/cronograma';

    const createModalEl = document.getElementById('createModal');
    const editModalEl = document.getElementById('editModal');
    let createModal, editModal;
    if (typeof bootstrap !== 'undefined') {
        createModal = new bootstrap.Modal(createModalEl);
        editModal = new bootstrap.Modal(editModalEl);
    }

    const formCriacao = document.getElementById('form-criacao');
    const formEdicao = document.getElementById('form-edicao');
    const tbody = document.getElementById('tbody-cronograma');

    // --- FUNÇÕES AUXILIARES ---

    function formatarDataParaExibicao(dataStr) {
        if (!dataStr) return '';
        const [ano, mes, dia] = dataStr.split('-');
        return `${dia}/${mes}/${ano}`;
    }

    function getStatusBadgeClass(status) {
        switch (status?.toLowerCase()) {
            case 'concluído': return 'bg-success';
            case 'em andamento': return 'bg-warning text-dark';
            case 'cancelado': return 'bg-danger';
            case 'pendente':
            default: return 'bg-secondary';
        }
    }

    function getFormularioHtml() {
        return `
            <input type="hidden" id="item-id">
            <div class="row g-3">
                <div class="col-12"><label for="tarefa" class="form-label">Tarefa</label><input type="text" class="form-control" id="tarefa" required></div>
                <div class="col-md-6"><label for="status" class="form-label">Status</label><select id="status" class="form-select"><option value="Pendente">Pendente</option><option value="Em Andamento">Em Andamento</option><option value="Concluído">Concluído</option><option value="Cancelado">Cancelado</option></select></div>
                <div class="col-md-6"><label for="responsavel" class="form-label">Responsável</label><input type="text" class="form-control" id="responsavel"></div>
                <div class="col-md-6"><label for="data_prevista" class="form-label">Data Prevista</label><input type="date" class="form-control" id="data_prevista" required></div>
                <div class="col-md-6"><label for="data_realizada" class="form-label">Data Realizada</label><input type="date" class="form-control" id="data_realizada"></div>
                <div class="col-12"><label for="observacao" class="form-label">Observação</label><textarea class="form-control" id="observacao" rows="3"></textarea></div>
            </div>
            <div class="modal-footer mt-4 border-0">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="submit" class="btn btn-primary">Salvar</button>
            </div>
        `;
    }

    // --- LÓGICA PRINCIPAL ---

    async function carregarItens() {
        try {
            const response = await fetchWithAuth(API_URL);
            const itens = await response.json();
            tbody.innerHTML = '';

            if (itens.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">Nenhuma tarefa encontrada.</td></tr>';
                return;
            }

            itens.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${item.tarefa}</td>
                    <td><span class="badge ${getStatusBadgeClass(item.status)} status-badge">${item.status}</span></td>
                    <td>${formatarDataParaExibicao(item.data_prevista)}</td>
                    <td>${formatarDataParaExibicao(item.data_realizada)}</td>
                    <td>${item.responsavel || ''}</td>
                    <td class="text-center">
                        <button class="btn btn-warning btn-sm btn-editar" data-id="${item.id}" title="Editar"><i class="bi bi-pencil-fill"></i></button>
                        <button type="button" class="btn btn-danger btn-sm btn-deletar" data-id="${item.id}" title="Deletar"><i class="bi bi-trash-fill"></i></button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } catch (error) {
            console.error('Erro ao carregar itens:', error);
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Erro ao carregar dados.</td></tr>';
        }
    }

    // --- EVENT LISTENERS ---

    // CRIAÇÃO
    formCriacao.addEventListener('submit', async (e) => {
        e.preventDefault();
        const dados = {
            tarefa: formCriacao.querySelector('#tarefa').value,
            data_prevista: formCriacao.querySelector('#data_prevista').value,
            data_realizada: formCriacao.querySelector('#data_realizada').value || null,
            status: formCriacao.querySelector('#status').value,
            responsavel: formCriacao.querySelector('#responsavel').value,
            observacao: formCriacao.querySelector('#observacao').value,
        };

        await fetchWithAuth(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados),
        });
        if (createModal) createModal.hide();
        ui.feedbackSucesso('Tarefa criada com sucesso!');
        carregarItens();
    });

    // EDIÇÃO E DELEÇÃO (usando delegação de eventos)
    tbody.addEventListener('click', async (e) => {
        const btnEditar = e.target.closest('.btn-editar');
        const btnDeletar = e.target.closest('.btn-deletar');

        if (btnDeletar) {
            const id = btnDeletar.dataset.id;
            ui.confirmarExclusao(
                `${API_URL}/${id}`,
                `Tarefa ID ${id}`,
                () => carregarItens()
            );
        }

        if (btnEditar) {
            const id = btnEditar.dataset.id;
            const response = await fetchWithAuth(`${API_URL}/${id}`);
            const item = await response.json();

            formEdicao.querySelector('#item-id').value = item.id;
            formEdicao.querySelector('#tarefa').value = item.tarefa;
            formEdicao.querySelector('#data_prevista').value = item.data_prevista;
            formEdicao.querySelector('#data_realizada').value = item.data_realizada;
            formEdicao.querySelector('#status').value = item.status;
            formEdicao.querySelector('#responsavel').value = item.responsavel;
            formEdicao.querySelector('#observacao').value = item.observacao;

            if (editModal) editModal.show();
        }
    });

    // SALVAR EDIÇÃO
    formEdicao.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = formEdicao.querySelector('#item-id').value;
        const dados = {
            tarefa: formEdicao.querySelector('#tarefa').value,
            data_prevista: formEdicao.querySelector('#data_prevista').value,
            data_realizada: formEdicao.querySelector('#data_realizada').value || null,
            status: formEdicao.querySelector('#status').value,
            responsavel: formEdicao.querySelector('#responsavel').value,
            observacao: formEdicao.querySelector('#observacao').value,
        };

        await fetchWithAuth(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados),
        });
        if (editModal) editModal.hide();
        ui.feedbackSucesso('Tarefa atualizada com sucesso!');
        carregarItens();
    });

    // INICIALIZAÇÃO
    formCriacao.innerHTML = getFormularioHtml();
    formEdicao.innerHTML = getFormularioHtml();
    carregarItens();
});
