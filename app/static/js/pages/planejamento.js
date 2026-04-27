document.addEventListener('DOMContentLoaded', () => {

    const municipios = ["Glória", "Paulo Afonso", "Macururé", "Chorrochó", "Abaré", "Rodelas"];
    let currentMunicipio = municipios[0];

    // DOM Elements
    const filtrosContainer = document.getElementById('filtros-municipios-cronograma');
    const tbody = document.getElementById('tbody-quantidades');
    const btnAdicionar = document.getElementById('btn-adicionar-linha');
    const btnLimpar = document.getElementById('btn-limpar-tudo');
    const municipioTitulo = document.getElementById('municipio-selecionado-titulo');

    // Totals
    const totalQuantEl = document.getElementById('total-quant');
    const totalMetaEl = document.getElementById('total-meta');
    const totalExecEl = document.getElementById('total-exec');
    const totalSaldoEl = document.getElementById('total-saldo');

    // --- 1. Inicializar Filtros ---
    municipios.forEach(mun => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-sm btn-outline-primary m-1';
        btn.textContent = mun;
        btn.dataset.municipio = mun;

        if (mun === currentMunicipio) {
            btn.classList.add('active', 'btn-primary');
            btn.classList.remove('btn-outline-primary');
        }

        btn.addEventListener('click', () => {
            // Update UI buttons
            document.querySelectorAll('#filtros-municipios-cronograma button').forEach(b => {
                b.classList.remove('active', 'btn-primary');
                b.classList.add('btn-outline-primary');
            });
            btn.classList.add('active', 'btn-primary');
            btn.classList.remove('btn-outline-primary');

            currentMunicipio = mun;
            carregarCronograma(mun);
        });
        filtrosContainer.appendChild(btn);
    });

    // --- 2. Button Adicionar Linha ---
    if (btnAdicionar) {
        btnAdicionar.addEventListener('click', async () => {
            try {
                const today = new Date().toISOString().split('T')[0];
                const token = localStorage.getItem('access_token');

                const payload = {
                    municipio: currentMunicipio,
                    semana_referencia: today,
                    quant_cisternas: 0,
                    meta_planejada: 0,
                    qtd_executada: 0
                };

                const res = await fetch('/api/planejamento/item', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(payload)
                });

                if (!res.ok) throw new Error("Erro ao criar item");

                // Reload to show new item
                carregarCronograma(currentMunicipio);

            } catch (e) {
                console.error(e);
                ui.feedbackErro("Erro ao adicionar linha: " + e.message);
            }
        });
    }

    // --- 2b. Button Limpar Tudo ---
    if (btnLimpar) {
        btnLimpar.addEventListener('click', () => {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: `Limpar tudo de ${currentMunicipio}?`,
                    text: "Isso vai apagar todas as linhas deste cronograma. Não tem volta!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#d33',
                    confirmButtonText: 'Sim, apagar tudo!'
                }).then(async (result) => {
                    if (result.isConfirmed) {
                        try {
                            const token = localStorage.getItem('access_token');
                            const res = await fetch(`/api/planejamento/limpar-tudo/${currentMunicipio}`, {
                                method: 'DELETE',
                                headers: token ? { 'Authorization': `Bearer ${token}` } : {}
                            });

                            if (!res.ok) throw new Error("Erro ao limpar data.");

                            ui.feedbackSucesso("Tabela zerada!", () => carregarCronograma(currentMunicipio));
                        } catch (e) {
                            console.error(e);
                            ui.feedbackErro("Erro ao limpar dados.");
                        }
                    }
                });
            }
        });
    }

    // --- 3. Carregar Dados ---
    /**
     * @descrição Busca dados do cronograma do município selecionado e inicia a renderização.
     * @param {string} mun - Nome do município (Ex: 'Abaré').
     * @comportamento Exibe spinner na tabela, chama API /api/planejamento/{mun}, e chama renderizarTabela() com o JSON retornado.
     */
    async function carregarCronograma(mun) {
        municipioTitulo.innerText = mun;
        tbody.innerHTML = '<tr><td colspan="7" class="text-center"><div class="spinner-border spinner-border-sm"></div> Carregando...</td></tr>';

        try {
            const token = localStorage.getItem('access_token');
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
            const res = await fetch(`/api/planejamento/${mun}`, { headers });

            if (!res.ok) throw new Error('Falha ao buscar dados');
            const dados = await res.json();

            renderizarTabela(dados);
        } catch (error) {
            console.error(error);
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">Erro: ${error.message}</td></tr>`;
        }
    }

    // --- 4. Renderizar Tabela ---
    /**
     * @descrição Constrói o HTML da tabela de cronograma e calcula os totais (Físico/Financeiro).
     * @param {Array} dados - Lista de objetos de itens do cronograma.
     * @comportamento 
     *  1. Itera sobre os itens criando linhas <tr>.
     *  2. Calcula saldo semanal e saldo acumulado (cascata).
     *  3. Renderiza badges de beneficiários vinculados.
     *  4. Atualiza os cards de totais no topo da página.
     */
    function renderizarTabela(dados) {
        tbody.innerHTML = '';
        let sQuant = 0, sMeta = 0, sExec = 0, sSaldo = 0;
        let acumulado = 0; // Variável para rastrear o saldo acumulado (Cascata)

        if (dados.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Nenhum registro. Clique em "+ Adicionar Linha".</td></tr>';
            atualizarTotais(0, 0, 0, 0);
            return;
        }

        dados.forEach(item => {
            const tr = document.createElement('tr');

            // Cálculos da Linha
            const quant = item.quant_cisternas || 0;
            const meta = item.meta_planejada || 0;
            const exec = item.qtd_executada || 0;

            // Saldo da linha
            const saldoSemanal = exec - meta;

            // Saldo ACUMULADO (Cascata)
            acumulado += saldoSemanal;

            // Totais Gerais
            sQuant += quant;
            sMeta += meta;
            sExec += exec;
            // sSaldo será o acumulado final
            sSaldo = acumulado;

            // Visualização do Saldo Acumulado
            const corSaldo = acumulado >= 0 ? 'text-success fw-bold' : 'text-danger fw-bold';
            const textoSaldo = acumulado > 0 ? `+${acumulado}` : acumulado;

            // Ícone de Status baseado no ACUMULADO
            const iconStatus = acumulado >= 0
                ? '<i class="bi bi-check-circle-fill text-success fs-5" title="No Prazo"></i>'
                : '<i class="bi bi-exclamation-circle-fill text-danger fs-5" title="Atrasado"></i>';

            // HTML Beneficiários
            let htmlBeneficiarios = '';
            if (item.beneficiarios && item.beneficiarios.length > 0) {
                htmlBeneficiarios = item.beneficiarios.map(b => {
                    const badgeColor = b.status === 'CONSTRUÍDA' ? 'bg-success' : 'bg-warning';

                    let iconDoc = '';
                    if (b.caminho_documento || b.arquivo_caminho) {
                        iconDoc = '<i class="bi bi-file-earmark-text-fill ms-1 text-white-50" title="Documento Anexado"></i>';
                    }

                    // Onclick chama função de detalhes (Modal)
                    return `
                        <span class="badge ${badgeColor} text-dark border d-flex align-items-center gap-1 shadow-sm clickable-badge" 
                              onclick="verDetalhesBeneficiario(${b.id})" style="cursor: pointer;">
                            <i class="bi bi-person-fill"></i>
                            <span>${b.nome_completo || 'Sem Nome'}</span>
                            ${iconDoc}
                            <i class="bi bi-x ms-2 text-danger bg-white rounded-circle" style="padding: 1px;" 
                               onclick="event.stopPropagation(); removerBeneficiario(${item.id}, ${b.id})" title="Desvincular"></i>
                        </span>`;
                }).join('');
            }

            // Render Row
            tr.innerHTML = `
                <td class="p-0">
                    <input type="date" class="form-control border-0 input-editable text-center" 
                           value="${item.semana_referencia}" 
                           data-id="${item.id}" data-field="semana_referencia">
                </td>
                <td class="p-0">
                    <input type="number" class="form-control border-0 text-center input-editable" 
                           value="${quant}" 
                           data-id="${item.id}" data-field="quant_cisternas">
                </td>
                <td class="p-0">
                    <input type="number" class="form-control border-0 text-center input-editable fw-bold text-secondary" 
                           value="${meta}" 
                           data-id="${item.id}" data-field="meta_planejada">
                </td>
                <td class="p-0">
                    <input type="number" class="form-control border-0 text-center input-editable fw-bold text-primary" 
                           data-id="${item.id}" data-field="qtd_executada" value="${exec}">
                </td>
                
                <td class="align-middle">
                    <div class="d-flex flex-wrap gap-1 align-items-center justify-content-center">
                        ${htmlBeneficiarios}
                        <button class="btn btn-xs btn-outline-secondary rounded-circle border-dashed" 
                                onclick="abrirModalVincular(${item.id})" title="Vincular Beneficiário">
                            <i class="bi bi-plus"></i>
                        </button>
                    </div>
                </td>

                <td class="text-center fw-bold align-middle ${corSaldo} bg-light">
                    ${textoSaldo}
                </td>
                <td class="text-center align-middle">${iconStatus}</td>
                <td class="text-center align-middle">
                    <button class="btn btn-sm btn-link text-danger p-0 btn-excluir" data-id="${item.id}" title="Excluir Linha">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        atualizarTotais(sQuant, sMeta, sExec, sSaldo);
        setupEvents();
    }

    function atualizarTotais(quant, meta, exec, saldo) {
        totalQuantEl.innerText = quant;
        totalMetaEl.innerText = meta;
        totalExecEl.innerText = exec;
        totalSaldoEl.innerText = saldo > 0 ? `+${saldo}` : saldo;
        totalSaldoEl.className = 'text-center fw-bold ' + (saldo < 0 ? 'text-danger' : 'text-success');
    }

    // --- 5. Eventos (Edit + Delete) ---
    function setupEvents() {
        // Edit Blur/Enter
        const inputs = document.querySelectorAll('.input-editable');
        inputs.forEach(input => {
            input.addEventListener('blur', (e) => salvarItem(e.target));
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') e.target.blur();
            });
            input.addEventListener('focus', (e) => e.target.select());
        });

        // Delete Buttons
        const btnsExcluir = document.querySelectorAll('.btn-excluir');
        btnsExcluir.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                // Use ui.confirmarExclusao if available, else standard confirm
                if (window.ui && window.ui.confirmarExclusao) {
                    ui.confirmarExclusao(
                        `/api/planejamento/item/${id}`,
                        'este item do cronograma',
                        () => carregarCronograma(currentMunicipio)
                    );
                } else {
                    if (confirm("Excluir item?")) {
                        // Fallback manual... but ui should be there
                    }
                }
            });
        });
    }

    async function salvarItem(input) {
        const id = input.dataset.id;
        const field = input.dataset.field;
        let value = input.value;

        // Converter numeros
        if (field !== 'semana_referencia') {
            value = parseInt(value) || 0;
        }

        const payload = {};
        payload[field] = value;

        try {
            const token = localStorage.getItem('access_token');
            const res = await fetch(`/api/planejamento/item/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error("Erro ao salvar");

            // Recarregar tabela para atualizar saldos acumulados
            // Otimização: Poderia não recarregar se for input que não afeta saldo, mas todos afetam a ordem ou saldo.
            carregarCronograma(currentMunicipio);

        } catch (e) {
            console.error(e);
            ui.feedbackErro("Erro ao salvar alteração.");
        }
    }

    // Start
    carregarCronograma(currentMunicipio);

    // --- 6. Funções Globais (Modal Geração) ---
    /**
     * @descrição Abre o modal para gerar cronograma automático.
     * @uso Botão "Gerar Automático" na UI.
     */
    window.abrirModalGerar = function () {
        if (typeof bootstrap !== 'undefined') {
            const modal = new bootstrap.Modal(document.getElementById('modalGerarCronograma'));
            modal.show();
        }
    };

    window.enviarGeracaoAutomatica = function () {
        // currentMunicipio is scoped, how to access? It's inside DOMContentLoaded but defined at top. 
        // Oh wait, window functions are outside the scope if I put them here? No, 'currentMunicipio' is accessible if I define window function INSIDE this closure.
        // Yes, defining window.func inside ensures access to closure variables if needed.

        // But better is to just read from the active tab if we want to be safe, but 'currentMunicipio' var is reliable.

        const payload = {
            data_inicio: document.getElementById('genDataInicio').value,
            total_cisternas: parseInt(document.getElementById('genTotal').value),
            meta_semanal: parseInt(document.getElementById('genMeta').value)
        };

        if (!payload.data_inicio || !payload.total_cisternas || !payload.meta_semanal) {
            ui.feedbackErro("Preencha todos os campos!");
            return;
        }

        const token = localStorage.getItem('access_token');
        fetch(`/api/planejamento/gerar-automatico/${currentMunicipio}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {})
            },
            body: JSON.stringify(payload)
        }).then(async res => {
            if (res.ok) {
                // Close Modal
                const modalEl = document.getElementById('modalGerarCronograma');
                if (modalEl && typeof bootstrap !== 'undefined') {
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }

                ui.feedbackSucesso(`Cronograma gerado para ${currentMunicipio}!`, () => {
                    carregarCronograma(currentMunicipio);
                });
            } else {
                const erro = await res.json();
                ui.feedbackErro(erro.detail || "Erro ao gerar.");
            }
        }).catch(err => {
            console.error(err);
            ui.feedbackErro("Erro de conexão.");
        });
    };

    // --- 7. Vínculo de Beneficiários ---

    // --- 7. Vínculo de Beneficiários (Modo Avançado) ---

    // Cache de Pedreiros (para não buscar toda vez)
    let cachePedreiros = null;

    window.abrirModalVincular = async function (cronogramaId) {
        /**
         * @descrição Inicia o fluxo de vínculo de beneficiário a uma semana do cronograma.
         * @param {int} cronogramaId - ID da linha do cronograma alvo.
         * @comportamento
         *  1. Abre modal #modalVincularBeneficiario.
         *  2. Carrega lista de pedreiros (com cache simples).
         *  3. Reseta campos de busca de beneficiário.
         */
        document.getElementById('vincularCronogramaId').value = cronogramaId;

        // Reset UI
        const inputBusca = document.getElementById('buscaBeneficiarioInput');
        inputBusca.value = '';
        inputBusca.disabled = false;

        const listDiv = document.getElementById('listaResultadosBeneficiarios');
        listDiv.innerHTML = '';
        listDiv.classList.add('d-none');

        limparSelecaoBeneficiario();

        // Data Default = Hoje
        document.getElementById('dataExecucao').value = new Date().toISOString().split('T')[0];

        // 1. Label Município
        document.getElementById('lblMunicipioVinculo').innerText = currentMunicipio;

        // 2. Load Pedreiros
        const selectPedreiro = document.getElementById('selectPedreiro');
        if (!cachePedreiros) {
            try {
                selectPedreiro.innerHTML = '<option>Carregando...</option>';
                const res = await fetch('/api/pedreiros'); // Filtro status=Ativo pode ser feito no back ou filter aqui
                const data = await res.json();
                cachePedreiros = data.filter(p => !p.status || p.status === 'Ativo'); // Client-side filter fallback
            } catch (e) {
                console.error("Erro carrega pedreiros", e);
                selectPedreiro.innerHTML = '<option value="">Erro ao carregar</option>';
            }
        }

        // Render Options
        selectPedreiro.innerHTML = '<option value="">Selecione...</option>';
        if (cachePedreiros) {
            cachePedreiros.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.nome_completo;
                selectPedreiro.appendChild(opt);
            });
        }

        if (typeof bootstrap !== 'undefined') {
            new bootstrap.Modal(document.getElementById('modalVincularBeneficiario')).show();
        }
    };

    // --- DEBOUNCED AUTOCOMPLETE ---
    let searchTimeout = null;
    const inputBusca = document.getElementById('buscaBeneficiarioInput');
    const listDiv = document.getElementById('listaResultadosBeneficiarios');

    // Fechar dropdown ao clicar fora com setTimeout para evitar race condition
    document.addEventListener('click', (e) => {
        if (!inputBusca.contains(e.target) && !listDiv.contains(e.target)) {
            setTimeout(() => {
                listDiv.classList.add('d-none');
            }, 200);
        }
    });

    // Reabrir ao focar e tiver valor
    inputBusca.addEventListener('focus', (e) => {
        if (e.target.value.trim().length >= 3 && listDiv.children.length > 0) {
            listDiv.classList.remove('d-none');
        }
    });

    inputBusca.addEventListener('input', function (e) {
        clearTimeout(searchTimeout);
        const q = e.target.value.trim();

        if (q.length < 3) {
            listDiv.innerHTML = '';
            listDiv.classList.add('d-none');
            return;
        }

        listDiv.classList.remove('d-none');
        listDiv.innerHTML = `<div class="list-group-item text-center text-muted small p-2"><div class="spinner-border spinner-border-sm"></div> Buscando em ${currentMunicipio}...</div>`;

        searchTimeout = setTimeout(async () => {
            try {
                const res = await fetch(`/api/planejamento/beneficiarios/busca?q=${encodeURIComponent(q)}&municipio=${encodeURIComponent(currentMunicipio)}`);
                const data = await res.json();

                listDiv.innerHTML = '';
                if (data.length === 0) {
                    listDiv.innerHTML = '<div class="list-group-item text-center text-muted small p-2">Nenhum beneficiário encontrado neste município.</div>';
                    return;
                }

                let itemsHtml = '';
                data.forEach(p => {
                    itemsHtml += `
                        <a href="#" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center autocomp-item"
                           data-id="${p.id}" 
                           data-nome="${(p.nome_completo || '').replace(/"/g, '&quot;')}" 
                           data-cpf="${p.cpf || ''}">
                            <div>
                                <strong class="d-block text-dark lh-sm">${p.nome_completo || 'Sem Nome'}</strong>
                                <div class="small text-secondary"><i class="bi bi-person-vcard"></i> CPF: ${p.cpf || '-'}</div>
                            </div>
                        </a>
                    `;
                });
                listDiv.innerHTML = itemsHtml;
            } catch (err) {
                console.error(err);
                listDiv.innerHTML = '<div class="list-group-item text-danger text-center small p-2">Erro na busca.</div>';
            }
        }, 400); // Debounce de 400ms
    });

    // --- EVENT DELEGATION: Delegação segura de mousedown para priorizar antes do blur ---
    listDiv.addEventListener('mousedown', (e) => {
        const item = e.target.closest('.autocomp-item');
        if (!item) return;

        // Previne qualquer blur side-effect
        e.preventDefault();

        const b = {
            id: item.dataset.id,
            nome_completo: item.dataset.nome,
            cpf: item.dataset.cpf
        };
        selecionarBeneficiario(b);
    });

    window.selecionarBeneficiario = function (p) {
        // UI Logic
        document.getElementById('selBenefId').value = p.id;
        document.getElementById('selBenefNome').innerText = p.nome_completo;
        document.getElementById('selBenefCpf').innerText = p.cpf;

        document.getElementById('beneficiarioSelecionadoCard').classList.remove('d-none');

        listDiv.innerHTML = '';
        listDiv.classList.add('d-none');

        inputBusca.value = '';
        inputBusca.disabled = true; // Impede buscar novo até deselecionar
    };

    window.limparSelecaoBeneficiario = function () {
        document.getElementById('selBenefId').value = '';
        document.getElementById('beneficiarioSelecionadoCard').classList.add('d-none');

        inputBusca.disabled = false;
        inputBusca.focus();
    };

    window.confirmarVinculoEtapaFinal = async function () {
        // Validation
        const cronogramaId = document.getElementById('vincularCronogramaId').value;
        const benefId = document.getElementById('selBenefId').value;
        const pedreiroId = document.getElementById('selectPedreiro').value;
        const dataExec = document.getElementById('dataExecucao').value;

        if (!benefId) {
            ui.feedbackErro("Selecione um beneficiário (Etapa 1).");
            return;
        }
        if (!pedreiroId) {
            ui.feedbackErro("Selecione o pedreiro responsável (Etapa 2).");
            return;
        }
        if (!dataExec) {
            ui.feedbackErro("Informe a data de conclusão (Etapa 3).");
            return;
        }

        const token = localStorage.getItem('access_token');
        try {
            const res = await fetch('/api/planejamento/vincular', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                },
                body: JSON.stringify({
                    cronograma_id: cronogramaId,
                    beneficiario_id: benefId,
                    pedreiro_id: pedreiroId,
                    data_execucao: dataExec
                })
            });

            const result = await res.json();
            if (res.ok) {
                // Close Modal
                // Close Modal
                const modalEl = document.getElementById('modalVincularBeneficiario');
                if (modalEl && typeof bootstrap !== 'undefined') {
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }

                ui.feedbackSucesso("Execução Registrada!", () => carregarCronograma(currentMunicipio));
            } else {
                ui.feedbackErro(result.detail || result.message || "Erro ao salvar.");
            }
        } catch (e) {
            console.error(e);
            ui.feedbackErro("Erro de conexão.");
        }
    };

    window.removerBeneficiario = async function (cronogramaId, beneficiarioId) {
        const token = localStorage.getItem('access_token');

        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: 'Desvincular?',
                text: "Remover este beneficiário desta semana?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sim, remover'
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        const res = await fetch(`/api/planejamento/desvincular?cronograma_id=${cronogramaId}&beneficiario_id=${beneficiarioId}`, {
                            method: 'DELETE',
                            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
                        });

                        if (res.ok) {
                            ui.feedbackSucesso("Removido.", () => carregarCronograma(currentMunicipio));
                        } else {
                            ui.feedbackErro("Erro ao remover.");
                        }
                    } catch (e) {
                        console.error(e);
                    }
                }
            });
        }
    };

    // --- 8. Detalhes do Beneficiário (Modal) ---
    window.verDetalhesBeneficiario = async function (id) {
        // Show Modal Loading state
        const modalEl = document.getElementById('modalDetalhesBeneficiario');
        if (!modalEl) return;

        if (typeof bootstrap !== 'undefined') {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        }

        // Reset fields
        document.getElementById('detalheNome').innerText = 'Carregando...';
        document.getElementById('detalheCpf').innerText = '-';
        document.getElementById('detalheNis').innerText = '-';
        document.getElementById('detalheMunicipio').innerText = '-';
        document.getElementById('detalheComunidade').innerText = '-';
        document.getElementById('detalheStatus').innerText = '-';
        document.getElementById('areaDocumento').innerHTML = '<div class="spinner-border spinner-border-sm text-primary"></div> Buscando...';
        document.getElementById('btnVerCompleto').href = '#';

        try {
            const token = localStorage.getItem('access_token');
            const res = await fetch(`/api/beneficiarios/${id}`, {
                headers: token ? { 'Authorization': `Bearer ${token}` } : {}
            });

            if (!res.ok) throw new Error("Erro ao buscar detalhes");
            const data = await res.json();

            // Populate Fields
            document.getElementById('detalheNome').innerText = data.nome_completo || 'Sem Nome';
            document.getElementById('detalheCpf').innerText = data.cpf || '-';
            document.getElementById('detalheNis').innerText = data.nis || '-';
            document.getElementById('detalheMunicipio').innerText = data.municipio || '-';
            document.getElementById('detalheComunidade').innerText = data.comunidade || '-';

            // Status styling
            const badgeStatus = document.getElementById('detalheStatus');
            badgeStatus.innerText = data.status || 'NI';
            badgeStatus.className = 'badge ' + (data.status === 'CONSTRUÍDA' ? 'bg-success' : 'bg-warning');

            // Link completo
            document.getElementById('btnVerCompleto').href = `/beneficiarios/perfil/${data.id}`;

            // Documents Logic
            const areaDoc = document.getElementById('areaDocumento');
            if (data.caminho_documento || data.arquivo_caminho || data.doc_status && data.doc_status.startsWith('uploads/')) {
                const docPath = data.caminho_documento || data.arquivo_caminho || data.doc_status;
                // Adjust path if needed (if it's relative to static or uploads)
                // Usually serving via /uploads or similar route. Assuming /uploads/ works if set in FastAPI static mounts.
                // If doc_status is just "OK", we might not have a link unless another field has it.
                // Based on router code: `caminho_web_relativo` is stored in `doc_status`? No, doc_status stores the path!

                const link = docPath.startsWith('http') ? docPath : `/${docPath}`;

                areaDoc.innerHTML = `
                    <div class="d-flex align-items-center justify-content-between">
                        <div class="text-start">
                            <span class="d-block fw-bold text-dark">Documento.pdf</span>
                            <small class="text-muted">Anexo do Beneficiário</small>
                        </div>
                        <a href="${link}" target="_blank" class="btn btn-danger btn-sm rounded-pill px-3">
                            <i class="bi bi-file-earmark-pdf-fill me-1"></i> Visualizar
                        </a>
                    </div>
                `;
            } else {
                areaDoc.innerHTML = '<span class="text-muted small"><i class="bi bi-info-circle me-1"></i> Nenhum documento digitalizado.</span>';
            }

        } catch (e) {
            console.error(e);
            document.getElementById('detalheNome').innerText = 'Erro ao carregar';
            ui.feedbackErro("Não foi possível carregar os detalhes.");
        }
    };

});
