const API_URL = '/api/pedreiros';
let dataTable;

// Função inicial
document.addEventListener('DOMContentLoaded', () => {
    initDataTable();
    setupForm();
    carregarSelectPedreirosFaturamento();
});

function initDataTable() {
    // Verificação de segurança
    if (!document.getElementById('tabelaPedreiros')) {
        console.error('Tabela #tabelaPedreiros não encontrada!');
        return;
    }

    /**
     * @descrição Define a DataTable com carregamento AJAX.
     * @colunas 
     *  - ID, Nome (Link perfil), CPF, Telefone, Endereço, Total Obras (badge), Status, Ações.
     */
    dataTable = $('#tabelaPedreiros').DataTable({
        ajax: {
            url: API_URL,
            dataSrc: '',
            beforeSend: function (xhr) {
                const token = localStorage.getItem('access_token');
                if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`);
            },
            error: function (xhr, error, thrown) {
                if (xhr.status === 401) {
                    window.location.href = '/login';
                } else {
                    console.error('Erro ao carregar dados:', error);
                    if (window.ui) ui.feedbackErro('Erro ao carregar lista de pedreiros.');
                    else alert('Erro ao carregar lista de pedreiros.');
                }
            }
        },
        columns: [
            { data: 'id' },
            {
                data: 'nome_completo',
                render: function (data, type, row) {
                    return `<a href="/api/pedreiros/perfil/${row.id}" target="_blank" class="text-primary fw-bold text-decoration-none">${data || 'Sem Nome'}</a>`;
                }
            },
            { data: 'cpf' },
            { data: 'telefone', defaultContent: '-' },
            { data: 'endereco', defaultContent: '-' },
            {
                data: 'dados_pagamento',
                defaultContent: '-',
                render: function (data) {
                    return `<small class="text-muted text-break" style="max-width: 150px; display:block;">${data || '-'}</small>`;
                }
            },
            {
                data: 'ultima_producao',
                className: 'text-center text-nowrap',
                render: function (data) {
                    if (!data) return '<span class="text-muted">-</span>';
                    // Format Date YYYY-MM-DD to DD/MM/YYYY
                    try {
                        const [y, m, d] = data.split('-');
                        return `${d}/${m}/${y}`;
                    } catch (e) { return data; }
                }
            },
            {
                data: 'status_financeiro',
                className: 'text-center text-nowrap',
                render: function (data) {
                    let badge = 'secondary';
                    let label = data || 'Sem Obras';
                    if (data === 'Pago') badge = 'success';
                    if (data === 'Pendente') badge = 'warning text-dark';
                    return `<span class="badge bg-${badge}">${label}</span>`;
                }
            },
            {
                data: 'producao_count',
                defaultContent: '0',
                render: function (data, type, row) {
                    console.log('Dados do Pedreiro:', row.nome_completo, ' | Contagem:', data);
                    return `<span class="badge bg-info text-dark fs-6">${data || 0} Cisternas</span>`;
                }
            },
            {
                data: 'status',
                render: function (data) {
                    const color = data === 'Ativo' ? 'success' : 'secondary';
                    return `<span class="badge bg-${color}">${data || 'Desconhecido'}</span>`;
                }
            },
            {
                data: null,
                orderable: false,
                render: function (data, type, row) {
                    return `
                        <button class="btn btn-sm btn-info text-white shadow-sm me-1" onclick="verProducao(${row.id})" title="Financeiro">
                            <i class="bi bi-cash-coin"></i>
                        </button>
                        <button class="btn btn-sm btn-warning shadow-sm" onclick="editarPedreiro(${row.id})" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger shadow-sm" onclick="confirmarExclusao(${row.id}, '${row.nome_completo || 'Item'}')" title="Excluir">
                            <i class="bi bi-trash"></i>
                        </button>
                    `;
                }
            }
        ],
        language: {
            url: 'https://cdn.datatables.net/plug-ins/1.13.7/i18n/pt-BR.json'
        }
    });
}

window.verProducao = async function (id) {
    const modalEl = document.getElementById('modalProducao');
    const tbody = document.getElementById('listaProducao');
    tbody.innerHTML = '<tr><td colspan="6" class="text-center"><div class="spinner-border text-primary"></div></td></tr>';

    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }

    try {
        const response = await fetchWithAuth(`${API_URL}/${id}/producao`);
        const data = await response.json();

        tbody.innerHTML = '';
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhuma produção encontrada.</td></tr>';
            return;
        }

        data.forEach(item => {
            const statusPagto = item.status_pagamento || 'Pendente';
            const badgePagto = statusPagto === 'PAGO' ? 'success' : 'warning text-dark';

            // Data format
            let dataConclusao = '-';
            if (item.data_conclusao) {
                try { const [y, m, d] = item.data_conclusao.split('-'); dataConclusao = `${d}/${m}/${y}`; } catch (e) { }
            }

            const tr = `
                <tr>
                    <td>${item.nome_completo}</td>
                    <td>${item.comunidade || '-'} / ${item.municipio || '-'}</td>
                    <td>
                        <input type="date" class="form-control form-control-sm" 
                               value="${item.data_conclusao || ''}" 
                               onchange="salvarProducaoRapida(${item.id}, 'data_conclusao', this.value)">
                    </td>
                    <td><span class="badge bg-secondary">${item.status || '-'}</span></td>
                    <td>
                        <select class="form-select form-select-sm" 
                                onchange="salvarProducaoRapida(${item.id}, 'status_pagamento', this.value)">
                            <option value="PENDENTE" ${statusPagto === 'PENDENTE' ? 'selected' : ''}>Pendente</option>
                            <option value="PAGO" ${statusPagto === 'PAGO' ? 'selected' : ''}>Pago</option>
                        </select>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-danger w-100" onclick="desvincularObra(${item.id})" title="Desvincular Pedreiro">
                            <i class="bi bi-trash"></i> Desvincular
                        </button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += tr;
        });

    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Erro ao carregar dados: ${error.message}</td></tr>`;
    }
}

window.salvarProducaoRapida = async function (id, campo, valor) {
    try {
        const payload = {};
        payload[campo] = valor;

        // Se mudou data, atualiza também status pagamento se necessário? Não, regra simples por enquanto.

        await fetchWithAuth(`/api/beneficiarios/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (window.ui) ui.feedbackSucesso('Atualizado com sucesso!', 'toast-bottom-right');

    } catch (e) {
        if (window.ui) ui.feedbackErro(`Erro ao atualizar: ${e.message}`);
        else alert(`Erro: ${e.message}`);
    }
}

window.desvincularObra = async function (id) {
    if (!confirm('Deseja remover esta obra deste pedreiro? (Desvincular)')) return;

    try {
        await fetchWithAuth(`/api/beneficiarios/${id}/desvincular-pedreiro`, {
            method: 'PATCH'
        });

        // Recarrega o modal de produção. Precisamos saber o ID do pedreiro.
        // Como o botão está dentro do modal, podemos pegar o pedreiro associado ou fechar o modal.
        // Helper: vamos pegar o ID do pedreiro do contexto ou reload da tabela.
        // Reload tabela
        dataTable.ajax.reload(null, false);

        // Remove a linha da tabela do modal visualmente
        const btn = document.querySelector(`button[onclick="desvincularObra(${id})"]`);
        if (btn) btn.closest('tr').remove();

        if (window.ui) ui.feedbackSucesso('Desvinculado com sucesso!');
    } catch (e) {
        if (window.ui) ui.feedbackErro(`Erro ao desvincular: ${e.message}`);
        else alert(`Erro: ${e.message}`);
    }
}

function setupForm() {
    const form = document.getElementById('formPedreiro');
    const modalEl = document.getElementById('modalPedreiro');

    if (!form || !modalEl) {
        console.error('Elementos do formulário ou modal não encontrados!');
        return;
    }

    let modal;
    if (typeof bootstrap !== 'undefined') {
        modal = new bootstrap.Modal(modalEl);
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Basic Validation
        if (!form.checkValidity()) {
            e.stopPropagation();
            form.classList.add('was-validated');
            return;
        }

        const id = document.getElementById('pedreiroId').value;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_URL}/${id}` : API_URL;

        try {
            const response = await fetchWithAuth(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Erro ao salvar');
            }

            if (modal) modal.hide();
            dataTable.ajax.reload();
            if (window.ui) ui.feedbackSucesso('Pedreiro salvo com sucesso!');
            else alert('Salvo com sucesso!');

        } catch (error) {
            if (window.ui) ui.feedbackErro(error.message);
            else alert(error.message);
        }
    });
}

window.limparFormulario = function () {
    const form = document.getElementById('formPedreiro');
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }
    const idEl = document.getElementById('pedreiroId');
    if (idEl) idEl.value = '';

    const tituloEl = document.getElementById('modalTitulo');
    if (tituloEl) tituloEl.innerHTML = '<i class="bi bi-person-worker me-2"></i><span>Novo Pedreiro</span>';
}

/**
 * @descrição Prepara modal para edição buscando dados da instância local do DataTable (sem request extra).
 * @param {int} id - ID do pedreiro.
 */
window.editarPedreiro = function (id) {
    if (!dataTable) return;
    const row = dataTable.row((idx, data) => data.id === id).data();
    if (!row) return;

    safeSetValue('pedreiroId', row.id);
    safeSetValue('nome', row.nome_completo);
    safeSetValue('cpf', row.cpf);
    safeSetValue('telefone', row.telefone || '');
    safeSetValue('endereco', row.endereco || '');
    safeSetValue('dados_pagamento', row.dados_pagamento || '');
    safeSetValue('status', row.status || 'Ativo');

    const tituloEl = document.getElementById('modalTitulo');
    if (tituloEl) tituloEl.innerHTML = '<i class="bi bi-pencil-square me-2"></i><span>Editar Pedreiro</span>';

    const modalEl = document.getElementById('modalPedreiro');
    if (modalEl && typeof bootstrap !== 'undefined') {
        const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
        modal.show();
    }
}

function safeSetValue(id, value) {
    const el = document.getElementById(id);
    if (el) el.value = value;
    else console.warn(`Elemento #${id} não encontrado para definir valor.`);
}

window.confirmarExclusao = function (id, nome) {
    if (window.ui) {
        ui.confirmarExclusao(`${API_URL}/${id}`, nome, () => {
            dataTable.ajax.reload();
        });
    } else {
        if (confirm(`Excluir ${nome}?`)) {
            // Fallback manual delete if UI lib missing
            fetchWithAuth(`${API_URL}/${id}`, { method: 'DELETE' })
                .then(() => dataTable.ajax.reload());
        }
    }
}

// ==========================================
// ABA FINANCEIRO: FATURAMENTO EM LOTE
// ==========================================

async function carregarSelectPedreirosFaturamento() {
    const sel = document.getElementById('selectPedreiroFaturamento');
    if (!sel) return;
    try {
        const res = await fetchWithAuth(API_URL);
        const pedreiros = await res.json();

        let html = '<option value="">-- Selecione o Pedreiro --</option>';
        pedreiros.forEach(p => {
            if (p.status === 'Ativo') {
                html += `<option value="${p.id}">${p.nome_completo} (CPF: ${p.cpf})</option>`;
            }
        });
        sel.innerHTML = html;
    } catch (e) {
        console.error("Erro ao carregar lista de pedreiros para faturamento:", e);
    }
}

window.carregarPendentesFaturamento = async function () {
    const sel = document.getElementById('selectPedreiroFaturamento');
    const tbody = document.getElementById('tabelaFaturamentoCorpo');
    const checkTodos = document.getElementById('checkTodosFaturamento');
    const pedreiroId = sel.value;

    checkTodos.checked = false;
    calcularLoteFaturamento(); // Reseta os contadores

    if (!pedreiroId) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4"><i class="bi bi-arrow-up-circle fs-3 d-block mb-2"></i>Selecione um pedreiro acima para listar obras.</td></tr>`;

        // Limpar tabela de histórico
        const tHistorico = document.getElementById('tabelaHistoricoFaturamentosCorpo');
        if (tHistorico) {
            tHistorico.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-4">Selecione um pedreiro para ver o histórico.</td></tr>`;
        }

        return;
    }

    tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4"><div class="spinner-border text-primary"></div></td></tr>';

    // 🔴 BUGFIX: Gatilho corrigido para disparar a renderização do histórico
    carregarHistoricoFaturamentos(pedreiroId);

    try {
        const res = await fetchWithAuth(`/api/pedreiros/${pedreiroId}/pendentes`);
        const data = await res.json();

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4"><i class="bi bi-info-circle fs-3 d-block mb-2"></i>  Nenhuma obra pendente de faturamento encontrada para este pedreiro.</td></tr>`;
            return;
        }

        let html = '';
        data.forEach(item => {
            // Format dates simply
            let dataStr = '-';
            if (item.data_conclusao) {
                try { const [y, m, d] = item.data_conclusao.split('-'); dataStr = `${d}/${m}/${y}`; } catch (e) { }
            }

            const valorSugerido = item.valor_sugerido || 1000.00;

            html += `
                <tr>
                    <td class="text-center">
                        <input class="form-check-input chk-faturar border-secondary" type="checkbox" value="${item.id}" data-valor="${valorSugerido}" onchange="calcularLoteFaturamento()">
                    </td>
                    <td><span class="badge bg-light text-dark border">#${item.id}</span></td>
                    <td class="fw-bold">${item.nome_completo}</td>
                    <td>${item.comunidade || '-'} / ${item.municipio || '-'}</td>
                    <td class="text-center">${dataStr}</td>
                    <td class="text-end text-success fw-bold">R$ ${valorSugerido.toFixed(2).replace('.', ',')}</td>
                </tr>
            `;
        });

        tbody.innerHTML = html;
    } catch (e) {
        console.error(e);
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-4">Erro ao buscar dados.</td></tr>`;
    }
}

window.toggleTodosFaturamento = function () {
    const isChecked = document.getElementById('checkTodosFaturamento').checked;
    const checkboxes = document.querySelectorAll('.chk-faturar');
    checkboxes.forEach(chk => chk.checked = isChecked);
    calcularLoteFaturamento();
}

window.calcularLoteFaturamento = function () {
    const checkboxes = document.querySelectorAll('.chk-faturar:checked');
    let totalBruto = 0;

    checkboxes.forEach(chk => {
        totalBruto += parseFloat(chk.dataset.valor || 0);
    });

    const retencaoDam = totalBruto * 0.05;
    const liquido = totalBruto - retencaoDam;

    document.getElementById('vlrTotalBruto').innerText = `R$ ${totalBruto.toFixed(2).replace('.', ',')}`;
    document.getElementById('vlrRetencaoDam').innerText = `R$ ${retencaoDam.toFixed(2).replace('.', ',')}`;
    document.getElementById('vlrLiquido').innerText = `R$ ${liquido.toFixed(2).replace('.', ',')}`;

    const btnGerar = document.getElementById('btnGerarLote');
    if (checkboxes.length > 0) {
        btnGerar.disabled = false;
        btnGerar.innerHTML = `<i class="bi bi-check2-circle me-1"></i> Gerar Faturamento (${checkboxes.length})`;
    } else {
        btnGerar.disabled = true;
        btnGerar.innerHTML = `<i class="bi bi-check2-circle me-1"></i> Gerar Faturamento`;
    }

    // Atualiza master checkbox state se todos ou nenhum individual foi clicado
    const checkTodos = document.getElementById('checkTodosFaturamento');
    const allCheckboxes = document.querySelectorAll('.chk-faturar');
    if (allCheckboxes.length > 0) {
        checkTodos.checked = checkboxes.length === allCheckboxes.length;
    }
}

window.lotesHistoricoCache = [];

window.carregarHistoricoFaturamentos = async function (pedreiroId) {
    console.log('Buscando histórico para o ID:', pedreiroId);

    const tbody = document.getElementById('tabelaHistoricoFaturamentosCorpo');
    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4"><div class="spinner-border text-secondary"></div></td></tr>';

    try {
        const res = await fetchWithAuth(`/api/pedreiros/${pedreiroId}/faturamentos`);
        const data = await res.json();

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-4">Nenhum lote faturado encontrado.</td></tr>`;
            return;
        }

        window.lotesHistoricoCache = data;

        let html = '';
        data.forEach(item => {
            // Formatar Data
            let dataGeral = new Date(item.data_criacao).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });

            const btnNF = item.arquivo_nf
                ? `<a href="/${item.arquivo_nf}" target="_blank" class="btn btn-sm btn-outline-success border-0 px-2 my-1" title="Visualizar NF"><i class="bi bi-file-earmark-text"></i> Ver NF</a>
                   <button class="btn btn-sm btn-light text-muted border-0 px-2 my-1" onclick="document.getElementById('nf_upload_${item.id}').click()" title="Substituir"><i class="bi bi-upload"></i></button>`
                : `<button class="btn btn-sm btn-outline-secondary border-0 px-2 my-1" onclick="document.getElementById('nf_upload_${item.id}').click()"><i class="bi bi-upload"></i> Anexar NF</button>`;

            const btnDAM = item.arquivo_dam
                ? `<a href="/${item.arquivo_dam}" target="_blank" class="btn btn-sm btn-outline-danger border-0 px-2 my-1" title="Visualizar DAM"><i class="bi bi-file-earmark-pdf"></i> Ver DAM</a>
                   <button class="btn btn-sm btn-light text-muted border-0 px-2 my-1" onclick="document.getElementById('dam_upload_${item.id}').click()" title="Substituir"><i class="bi bi-upload"></i></button>`
                : `<button class="btn btn-sm btn-outline-secondary border-0 px-2 my-1" onclick="document.getElementById('dam_upload_${item.id}').click()"><i class="bi bi-upload"></i> Anexar DAM</button>`;

            html += `
                <tr>
                    <td class="text-center fw-bold text-secondary"># ${item.id}</td>
                    <td>${dataGeral}</td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-outline-info border-0 rounded-pill px-3 fw-bold" onclick="verObrasLote(${item.id})">
                            <i class="bi bi-eye"></i> ${item.qtd_obras} Obras
                        </button>
                    </td>
                    <td class="text-end fw-bold">R$ ${(item.valor_total || 0).toFixed(2).replace('.', ',')}</td>
                    <td class="text-end text-danger fw-bold">R$ ${(item.valor_dam || 0).toFixed(2).replace('.', ',')}</td>
                    <td class="text-center">
                        <div class="d-flex flex-wrap justify-content-center gap-1">
                            ${btnNF}
                            <input type="file" id="nf_upload_${item.id}" class="d-none" accept=".pdf,image/*" onchange="uploadDocumentoFinanceiro(${item.id}, 'nf', this)">
                            
                            ${btnDAM}
                            <input type="file" id="dam_upload_${item.id}" class="d-none" accept=".pdf,image/*" onchange="uploadDocumentoFinanceiro(${item.id}, 'dam', this)">
                        </div>
                    </td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-outline-danger border-0" onclick="cancelarLoteFaturamento(${item.id})" title="Estornar Lote">
                            <i class="bi bi-trash"></i> Cancelar
                        </button>
                    </td>
                </tr>
            `;
        });
        tbody.innerHTML = html;

    } catch (e) {
        console.error(e);
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-4">Erro ao buscar histórico.</td></tr>`;
    }
}

window.uploadDocumentoFinanceiro = async function (faturamentoId, tipo, inputElement) {
    if (!inputElement.files || inputElement.files.length === 0) return;

    const file = inputElement.files[0];
    const formData = new FormData();
    formData.append('arquivo', file);

    const pedreiroId = document.getElementById('selectPedreiroFaturamento').value;

    try {
        Swal.showLoading();
        const res = await fetchWithAuth(`/api/pedreiros/faturamentos/${faturamentoId}/upload-${tipo}`, {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            ui.feedbackSucesso('Documento salvo!', () => {
                if (pedreiroId) carregarHistoricoFaturamentos(pedreiroId);
            });
        } else {
            const err = await res.json().catch(() => ({ detail: 'Falha desconhecida.' }));
            ui.feedbackErro(err.detail);
        }
    } catch (e) {
        console.error(e);
        ui.feedbackErro('Erro ao processar o arquivo.');
    } finally {
        inputElement.value = ''; // Reset input
    }
}

window.gerarLoteFaturamento = async function () {
    const pedreiroId = document.getElementById('selectPedreiroFaturamento').value;
    const checkboxes = document.querySelectorAll('.chk-faturar:checked');
    const ids = Array.from(checkboxes).map(chk => parseInt(chk.value));

    // Calcula valores (reutilizando a lógica da tela)
    let totalBruto = 0;
    checkboxes.forEach(chk => {
        totalBruto += parseFloat(chk.dataset.valor || 0);
    });
    const retencaoDam = totalBruto * 0.05;

    if (!pedreiroId || ids.length === 0) return;

    ui.confirmar(
        'Gerar Lote de Faturamento?',
        `Confirma a geração de faturamento para ${ids.length} obras totalizando R$ ${totalBruto.toFixed(2).replace('.', ',')}?`,
        async () => {
            try {
                Swal.showLoading();
                const payload = {
                    pedreiro_id: parseInt(pedreiroId),
                    beneficiarios_ids: ids,
                    valor_total: totalBruto,
                    valor_dam: retencaoDam
                };

                const res = await fetchWithAuth('/api/pedreiros/faturamentos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (res.ok) {
                    ui.feedbackSucesso('Faturamento gerado com sucesso!', () => {
                        // Fecha o modal
                        const modalEl = document.getElementById('modalPedreiroFaturamento');
                        if (modalEl) {
                            const modal = bootstrap.Modal.getInstance(modalEl);
                            if (modal) modal.hide();
                        }

                        // Recarrega as duas grids
                        if (window.dataTable) dataTable.ajax.reload(null, false);
                        carregarPendentesFaturamento();
                    });
                } else {
                    const err = await res.json().catch(() => ({ detail: 'Erro desconhecido.' }));
                    ui.feedbackErro(`Falha ao faturar: ${err.detail}`);
                }
            } catch (error) {
                console.error(error);
                ui.feedbackErro('Erro de conexão ao gerar lote.');
            }
        },
        'Confirmar Faturamento'
    );
}

window.cancelarLoteFaturamento = async function (faturamentoId) {
    ui.confirmar(
        'Estornar Lote?',
        'As obras deste lote retornarão ao status Pendente e este documento será apagado. Continuar?',
        async () => {
            try {
                Swal.showLoading();
                const res = await fetchWithAuth(`/api/pedreiros/faturamentos/${faturamentoId}`, {
                    method: 'DELETE'
                });

                if (res.ok) {
                    ui.feedbackSucesso('Lote estornado com sucesso!', () => {
                        const pedreiroId = document.getElementById('selectPedreiroFaturamento').value;
                        if (pedreiroId) carregarHistoricoFaturamentos(pedreiroId);
                        carregarPendentesFaturamento();
                    });
                } else {
                    const err = await res.json().catch(() => ({ detail: 'Falha desconhecida.' }));
                    ui.feedbackErro(`Falha ao estornar: ${err.detail}`);
                }
            } catch (error) {
                console.error(error);
                ui.feedbackErro('Erro de rede ao estornar o lote.');
            }
        },
        'Atenção (Ação Irreversível)'
    );
}

window.verObrasLote = function (loteId) {
    const lote = window.lotesHistoricoCache.find(l => l.id === loteId);
    if (!lote) return;

    const lista = document.getElementById('listaBeneficiariosLote');
    lista.innerHTML = '';

    if (!lote.obras || lote.obras.length === 0) {
        lista.innerHTML = `<li class="list-group-item text-center text-muted py-4">Nenhuma obra localizada neste lote.</li>`;
    } else {
        lote.obras.forEach(obra => {
            lista.innerHTML += `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <i class="bi bi-person text-secondary me-2"></i><strong>${obra.nome}</strong>
                        <div class="small text-muted ms-4"><i class="bi bi-geo-alt me-1"></i>${obra.local || '-'}</div>
                    </div>
                </li>
            `;
        });
    }

    const modal = new bootstrap.Modal(document.getElementById('modalObrasLote'));
    modal.show();
}
