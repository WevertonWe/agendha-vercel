// static/js/pages/conferencia.js

let listaMestraGlobal = [];
let sortCol = 'status'; // Default sort
let sortAsc = true;

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-conferencia');
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('input-excel');
    const fileInfo = document.getElementById('file-info');
    const btnVerificar = document.getElementById('btn-verificar');
    const loadingSpinner = document.getElementById('loading-spinner');
    const areaResultados = document.getElementById('area-resultados');
    const statsContainer = document.getElementById('stats-container');
    const selectMunicipio = document.getElementById('select-municipio');

    // Carrega histórico ao iniciar
    carregarHistorico();

    // --- Lógica de Drag and Drop ---
    dropArea.addEventListener('dragover', (e) => { e.preventDefault(); dropArea.classList.add('highlight'); });
    dropArea.addEventListener('dragleave', () => { dropArea.classList.remove('highlight'); });
    dropArea.addEventListener('drop', (e) => {
        e.preventDefault(); dropArea.classList.remove('highlight');
        const files = e.dataTransfer.files;
        if (files.length > 0) { fileInput.files = files; updateFileInfo(files[0]); }
    });
    dropArea.addEventListener('click', (e) => { if (e.target.tagName === 'LABEL') fileInput.click(); });
    fileInput.addEventListener('change', () => { if (fileInput.files.length > 0) updateFileInfo(fileInput.files[0]); });

    function updateFileInfo(file) {
        fileInfo.textContent = file ? `Ficheiro selecionado: ${file.name} (${(file.size / 1024).toFixed(2)} KB)` : '';
    }

    // --- Submissão do Formulário ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const municipioId = selectMunicipio.value;
        if (!municipioId) { alert('Por favor, selecione o Município.'); selectMunicipio.focus(); return; }
        if (fileInput.files.length === 0) { alert('Por favor, selecione um ficheiro Excel.'); return; }

        const formData = new FormData();
        formData.append('arquivo_excel', fileInput.files[0]);
        formData.append('municipio_id', municipioId);

        btnVerificar.disabled = true;
        const municipioNome = selectMunicipio.options[selectMunicipio.selectedIndex].text;
        btnVerificar.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Verificando ${municipioNome}...`;
        loadingSpinner.classList.remove('d-none');
        areaResultados.innerHTML = `<div class="text-center py-5"><div class="spinner-border text-primary"></div><p class="mt-2 text-muted">A processar dados de ${municipioNome}...</p></div>`;
        statsContainer.innerHTML = '';

        try {
            const response = await fetchWithAuth('/api/conferencia/verificar', { method: 'POST', body: formData });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Erro desconhecido.' }));
                const msg = typeof errorData.detail === 'object' ? JSON.stringify(errorData.detail) : errorData.detail;
                throw new Error(msg);
            }
            const data = await response.json();
            renderizarResultados(data);
            carregarHistorico(); // Atualiza lista lateral
        } catch (error) {
            areaResultados.innerHTML = `<div class="alert alert-danger"><b>Erro:</b> ${error.message}</div>`;
        } finally {
            btnVerificar.disabled = false;
            btnVerificar.innerHTML = '<i class="bi bi-search"></i> Iniciar Verificação';
            loadingSpinner.classList.add('d-none');
        }
    });

    /**
     * @descrição Listener para botões "Corrigir" na tabela de divergências.
     * @comportamento
     *  1. Intercepta clique em .btn-atualizar-nome.
     *  2. Exibe confirmação visual (ui.confirmar).
     *  3. Envia PUT para /api/beneficiarios/{id} com novo nome.
     *  4. Atualiza a célula da tabela localmente em caso de sucesso.
     */
    areaResultados.addEventListener('click', async (e) => {
        const target = e.target.closest('.btn-atualizar-nome');
        if (!target) return;
        const id = target.dataset.id;
        const nomeNovo = unescape(target.dataset.nomeNovo);

        ui.confirmar(
            'Confirmar Correção',
            `Atualizar nome para "${nomeNovo}"?`,
            async () => {
                target.disabled = true; target.innerHTML = '...';
                try {
                    const res = await fetchWithAuth(`/api/beneficiarios/${id}`, {
                        method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nome_completo: nomeNovo })
                    });
                    if (!res.ok) throw new Error();
                    target.innerHTML = '<i class="bi bi-check"></i>';
                    target.classList.replace('btn-outline-warning', 'btn-success');
                    const row = document.getElementById(`row-${id}`);
                    if (row) { row.querySelector('.agendha-name').textContent = nomeNovo; }
                    ui.feedbackSucesso('Nome atualizado!');
                } catch {
                    ui.feedbackErro('Erro ao atualizar.');
                    target.disabled = false;
                }
            },
            'Sim, corrigir'
        );
    });
});

// --- Funções Globais (Window) ---

/**
 * @descrição Renderiza o Dashboard (Barras de Progresso e Cards) e chama a renderização da tabela.
 * @param {Object} data - Payload contendo {meta, estatisticas, lista_mestra}.
 */
function renderizarResultados(data) {
    const { meta, estatisticas, lista_mestra } = data;
    listaMestraGlobal = lista_mestra; // Atualiza global para ordenação

    // Dashboard
    const percentual = meta > 0 ? ((estatisticas.total_ok / meta) * 100).toFixed(1) : 0;
    const width = Math.min(percentual, 100);

    const statsContainer = document.getElementById('stats-container');
    statsContainer.innerHTML = `
        <div class="row g-3 mb-4">
            <div class="col-12">
                <div class="card bg-light border-0">
                    <div class="card-body py-3">
                         <div class="d-flex justify-content-between align-items-center mb-1">
                            <strong>Progresso da Meta (${meta})</strong>
                            <span class="badge bg-primary">${percentual}%</span>
                        </div>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-success" style="width: ${width}%"></div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-4">
                <div class="card border-success text-center h-100">
                    <div class="card-body py-2">
                        <h3 class="text-success mb-0">${estatisticas.total_ok}</h3>
                        <small class="text-muted">OK / No Sistema</small>
                    </div>
                </div>
            </div>
            <div class="col-4">
                <div class="card border-warning text-center h-100">
                    <div class="card-body py-2">
                        <h3 class="text-warning mb-0">${estatisticas.total_falta_gov}</h3>
                        <small class="text-muted">Enviar p/ Gov</small>
                    </div>
                </div>
            </div>
            <div class="col-4">
                 <div class="card border-danger text-center h-100">
                    <div class="card-body py-2">
                        <h3 class="text-danger mb-0">${estatisticas.pendentes_com_erro_grh}</h3>
                        <small class="text-muted">Erro: Sem GRH</small>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Tabela
    atualizarTabelaHTML();
}

function atualizarTabelaHTML() {
    const area = document.getElementById('area-resultados');
    const lista = listaMestraGlobal;

    // Ordenação
    lista.sort((a, b) => {
        let valA = a[sortCol] || '';
        let valB = b[sortCol] || '';
        if (valA === valB) return 0;
        if (sortAsc) return valA > valB ? 1 : -1;
        return valA < valB ? 1 : -1;
    });

    const getIcon = (col) => sortCol === col ? (sortAsc ? '<i class="bi bi-sort-down"></i>' : '<i class="bi bi-sort-up"></i>') : '';

    let html = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <h5 class="m-0"><i class="bi bi-table"></i> Tabela Mestra</h5>
            <input type="text" id="filtro-tabela" class="form-control form-control-sm w-50" placeholder="Filtrar por nome, CPF ou status..." onkeyup="filtrarNaTela(this)">
        </div>
        <div class="table-responsive" style="max-height: 65vh; overflow-y: auto;">
            <table class="table table-sm table-hover table-bordered align-middle small mb-0" id="tabela-mestra">
                <thead class="table-light sticky-top" style="top:0; z-index:2;">
                    <tr>
                        <th class="text-center" style="width: 50px;">#</th>
                        <th style="cursor: pointer" onclick="ordenarTabela('status')">Status ${getIcon('status')}</th>
                        <th style="cursor: pointer" onclick="ordenarTabela('cpf')">CPF ${getIcon('cpf')}</th>
                        <th style="cursor: pointer" onclick="ordenarTabela('nome_agendha')">Nome (AGENDHA) ${getIcon('nome_agendha')}</th>
                        <th>Nome (Excel)</th>
                        <th style="cursor: pointer" onclick="ordenarTabela('grh')">GRH ${getIcon('grh')}</th>
                        <th class="text-center">Ação</th>
                    </tr>
                </thead>
                <tbody>
    `;

    lista.forEach((item, index) => {
        let statusBadge = '';
        let rowClass = '';

        switch (item.status) {
            case 'OK': statusBadge = '<span class="badge bg-success">OK</span>'; break;
            case 'Falta no Gov':
                if (item.erro_grh) {
                    statusBadge = '<span class="badge bg-danger">GRH Obrigatório</span>'; rowClass = 'table-danger';
                } else {
                    statusBadge = '<span class="badge bg-warning text-dark">Enviar</span>';
                }
                break;
            case 'Falta no AGENDHA': statusBadge = '<span class="badge bg-info text-dark">Falta AGENDHA</span>'; break;
            case 'Divergência': statusBadge = '<span class="badge bg-secondary">Divergência</span>'; break;
        }

        let acao = item.status === 'Divergência' ?
            `<button class="btn btn-sm btn-outline-warning btn-atualizar-nome" data-id="${item.id_agendha}" data-nome-novo="${escape(item.nome_excel)}">Corrigir</button>` :
            `<span class="text-muted">${item.acao_sugerida}</span>`;

        html += `
            <tr class="${rowClass}" id="row-${item.id_agendha}">
                <td class="text-center text-muted">${index + 1}</td>
                <td>${statusBadge}</td>
                <td>${item.cpf}</td>
                <td class="agendha-name">${item.nome_agendha || '-'}</td>
                <td class="text-muted">${item.nome_excel || '-'}</td>
                <td>${item.grh || '-'}</td>
                <td class="text-center">${acao}</td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';

    // Se o elemento stats-container não estiver vazio (dashboard renderizado), injeta a tabela abaixo
    // Caso contrário injeta tudo. Como a div area-resultados é separada, ok.
    if (area) area.innerHTML = html;
}

window.filtrarNaTela = function (input) {
    const termo = input.value.toLowerCase();
    const rows = document.querySelectorAll('#tabela-mestra tbody tr');
    rows.forEach(row => {
        row.style.display = row.innerText.toLowerCase().includes(termo) ? '' : 'none';
    });
}

window.ordenarTabela = function (col) {
    if (sortCol === col) sortAsc = !sortAsc;
    else { sortCol = col; sortAsc = true; }
    atualizarTabelaHTML();
}

window.carregarHistorico = async function () {
    const lista = document.getElementById('lista-historico');
    lista.innerHTML = '<div class="text-center py-2"><span class="spinner-border spinner-border-sm"></span></div>';

    try {
        const res = await fetchWithAuth('/api/conferencia/historico');
        const dados = await res.json();

        if (dados.length === 0) {
            lista.innerHTML = '<div class="text-muted text-center p-2">Nenhum histórico.</div>';
            return;
        }

        lista.innerHTML = '';
        dados.forEach(d => {
            const data = new Date(d.data_criacao).toLocaleString();
            const ok = d.resumo_metas?.total_ok || 0;

            const item = document.createElement('div');
            item.className = 'list-group-item list-group-item-action py-2';
            item.style.cursor = 'pointer';
            item.onclick = () => verDetalheHistorico(d.id);

            item.innerHTML = `
                <div class="d-flex w-100 justify-content-between align-items-center">
                    <div>
                        <strong class="mb-1 d-block">${d.municipio}</strong>
                        <small class="text-muted"><i class="bi bi-calendar"></i> ${data}</small>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-success mb-1">${ok} OK</span><br>
                        <button class="btn btn-outline-danger btn-sm border-0 p-0 fs-5" title="Excluir" onclick="excluirHistorico(event, ${d.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            lista.appendChild(item);
        });
    } catch (e) {
        lista.innerHTML = '<div class="text-danger small text-center">Erro ao carregar.</div>';
    }
}

window.excluirHistorico = function (event, id) {
    event.stopPropagation(); // Impede abrir o detalhe ao clicar na lixeira
    ui.confirmar(
        'Limpar Histórico?',
        'Tem certeza que deseja apagar este histórico?',
        async () => {
            try {
                const res = await fetchWithAuth(`/api/conferencia/historico/${id}`, { method: 'DELETE' });
                if (res.ok) {
                    carregarHistorico(); // Recarrega a lista
                    ui.feedbackSucesso('Histórico apagado.');
                } else {
                    ui.feedbackErro('Erro ao excluir.');
                }
            } catch (e) {
                console.error(e);
                ui.feedbackErro('Falha de conexão.');
            }
        },
        'Sim, excluir'
    );
}

/**
 * @descrição Carrega detalhes de um item do histórico e restaura a visualização.
 * @param {int} id - ID do registro no histórico.
 * @comportamento
 *  1. Busca dados do backend.
 *  2. Realiza Parser Robusto do JSON (tratando strings aninhadas/escapadas do SQLite).
 *  3. Normaliza estatísticas (fallback se faltar chaves).
 *  4. Chama renderizarResultados(dados).
 */
window.verDetalheHistorico = async function (id) {
    const area = document.getElementById('area-resultados');
    area.innerHTML = '<div class="text-center py-5"><span class="spinner-border"></span><p>Restaurando conferência...</p></div>';

    try {
        const res = await fetchWithAuth(`/api/conferencia/historico/${id}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();

        // --- Bloco de Tratamento Robusto de Histórico ---
        console.log("1. Payload Bruto Recebido:", data);

        let dadosParaRenderizar = data;

        // Passo A: Desembrulhar se estiver dentro de uma chave de transporte do banco
        if (data.json_resumo) {
            dadosParaRenderizar = data.json_resumo;
        } else if (data.dados) {
            dadosParaRenderizar = data.dados;
        }

        // Passo B: Detecção de String
        if (typeof dadosParaRenderizar === 'string') {
            try {
                console.log("2. Detectado string, fazendo parse...");
                dadosParaRenderizar = JSON.parse(dadosParaRenderizar);
                if (typeof dadosParaRenderizar === 'string') {
                    dadosParaRenderizar = JSON.parse(dadosParaRenderizar);
                }
            } catch (e) {
                console.error("ERRO CRÍTICO no Parse JSON:", e);
                throw new Error("Falha ao processar dados salvos (JSON inválido).");
            }
        }

        console.log("3. Objeto Final para Render:", dadosParaRenderizar);

        // Passo D: Validação de Estrutura Mínima
        if (!dadosParaRenderizar.estatisticas && !dadosParaRenderizar.stats) {
            dadosParaRenderizar.estatisticas = { total_ok: 0, total_falta_gov: 0, pendentes_com_erro_grh: 0 }; // Fallback
            // throw new Error("O histórico salvo não contém estatísticas válidas."); // Evitar quebrar tudo
        }

        // Normalização de chaves
        if (dadosParaRenderizar.stats && !dadosParaRenderizar.estatisticas) {
            dadosParaRenderizar.estatisticas = dadosParaRenderizar.stats;
        }

        renderizarResultados(dadosParaRenderizar);

        // Atualiza select
        try {
            const munId = dadosParaRenderizar.lista_mestra?.[0]?.municipio_id || dadosParaRenderizar.municipio_id || '';
            const select = document.getElementById('select-municipio');
            if (munId && [...select.options].some(o => o.value === munId)) {
                select.value = munId;
            }
        } catch (e) { console.warn("Auto-select falhou", e); }

    } catch (error) {
        console.error("Erro detalhado JS:", error);
        area.innerHTML = `<div class="alert alert-danger"><b>Erro ao restaurar:</b> <small>${error.message}</small></div>`;
    }
}
