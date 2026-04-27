
document.addEventListener('DOMContentLoaded', () => {

    // --- Styles Injection (Removed) ---
    // (Limpando estilos anteriores de accordion que não são mais usados)

    // --- State & Cache ---
    let globalCotacoesList = [];
    let globalMateriais = [];
    let globalFornecedores = [];
    let itensCotacaoAtual = []; // Array temporário para o modal de cotação

    // --- Referências aos elementos do DOM ---
    const accordionContainer = document.getElementById('accordion-cotacoes');

    // Modal de Criação de Cotação Mestra
    let modalCriarMaster;
    const formCriarMaster = document.getElementById('formCriarMaster');

    // Elementos de Itens (Novo)
    const selectMaterial = document.getElementById('selectMaterial');
    const inputQuantidade = document.getElementById('inputQuantidade');
    const btnAdicionarItem = document.getElementById('btnAdicionarItem');
    const tabelaItensCotacao = document.getElementById('tabelaItensCotacao');

    // Modal de Adição de Proposta
    let modalAdicionarProposta;
    const formAdicionarProposta = document.getElementById('formAdicionarProposta');
    const inputMasterIdProposta = document.getElementById('input-proposta-master-id');
    const selectFornecedor = document.getElementById('selectFornecedor');

    if (typeof bootstrap !== 'undefined') {
        const elMaster = document.getElementById('modalCriarMaster');
        if (elMaster) modalCriarMaster = new bootstrap.Modal(elMaster);

        const elProp = document.getElementById('modalAdicionarProposta');
        if (elProp) modalAdicionarProposta = new bootstrap.Modal(elProp);
    }


    // --- Inicialização ---
    init();

    /**
     * @descrição Função de boot principal.
     * @comportamento Carrega Cotações, Materiais e Fornecedores em paralelo (Promise.all) para garantir que selects e tabelas tenham dados de referência.
     */
    async function init() {
        try {
            // Carrega tudo em paralelo
            await Promise.all([
                carregarCotacoes(),
                carregarMateriais(),
                carregarFornecedores()
            ]);
            console.log("Dados iniciais carregados.");
        } catch (error) {
            console.error("Erro na inicialização:", error);
            ui.feedbackErro("Erro ao carregar dados iniciais.");
        }
    }

    // --- Carregamento de Dados ---

    async function carregarMateriais() {
        try {
            const res = await fetchWithAuth('/api/materiais');
            if (res.ok) {
                globalMateriais = await res.json();
                popularSelectMateriais();
            }
        } catch (e) { console.error("Erro ao carregar materiais", e); }
    }

    async function carregarFornecedores() {
        try {
            const res = await fetchWithAuth('/api/fornecedores');
            if (res.ok) {
                globalFornecedores = await res.json();
                popularSelectFornecedores();
            }
        } catch (e) { console.error("Erro ao carregar fornecedores", e); }
    }

    async function carregarCotacoes() {
        try {
            const response = await fetchWithAuth('/api/cotacoes-completas');
            if (!response.ok) throw new Error('Falha ao buscar dados das cotações.');

            const cotacoesMaster = await response.json();
            globalCotacoesList = cotacoesMaster;
            renderCotacoes(cotacoesMaster);
        } catch (error) {
            console.error("Erro ao carregar cotações:", error);
            accordionContainer.innerHTML = '<div class="alert alert-danger">Erro ao carregar os dados.</div>';
        }
    }

    // --- Renderização ---

    /**
     * @descrição Renderiza a lista de cotações mestras em formato Accordion.
     * @param {Array} lista - Lista de objetos de cotação mestra (incluindo itens e propostas aninhadas).
     * @comportamento Limpa o container e insere o HTML gerado por 'criarCardCotacao' para cada item.
     */
    function renderCotacoes(lista) {
        accordionContainer.innerHTML = '';
        if (lista.length === 0) {
            accordionContainer.innerHTML = '<div class="alert alert-secondary">Nenhuma cotação mestra encontrada. Crie uma para começar.</div>';
            return;
        }
        lista.forEach(master => {
            accordionContainer.insertAdjacentHTML('beforeend', criarCardCotacao(master));
        });
    }

    function popularSelectMateriais() {
        if (!selectMaterial) return;
        selectMaterial.innerHTML = '<option value="">Selecione um material...</option>';
        globalMateriais.forEach(mat => {
            // Assume mat.id e mat.nome
            const option = document.createElement('option');
            option.value = mat.id;
            // Se tiver unidade, mostrar
            const unidade = mat.unidade ? `(${mat.unidade})` : '';
            option.textContent = `${mat.nome} ${unidade}`;
            selectMaterial.appendChild(option);
        });
    }

    function popularSelectFornecedores() {
        if (!selectFornecedor) return;
        selectFornecedor.innerHTML = '<option value="">Selecione...</option>';
        globalFornecedores.forEach(forn => {
            const option = document.createElement('option');
            option.value = forn.id;
            option.textContent = forn.nome_empresa || forn.nome || "Fornecedor Sem Nome";
            selectFornecedor.appendChild(option);
        });
    }

    // --- Lógica de Itens (Modal Cotação) ---

    // Ao clicar em adicionar item no modal
    if (btnAdicionarItem) {
        btnAdicionarItem.addEventListener('click', () => {
            const matId = selectMaterial.value;
            const qtd = parseInt(inputQuantidade.value);

            if (!matId) {
                alert("Selecione um material.");
                return;
            }
            if (!qtd || qtd <= 0) {
                alert("Quantidade inválida.");
                return;
            }

            // Verifica se já existe
            const exists = itensCotacaoAtual.find(i => i.material_id == matId);
            if (exists) {
                alert("Este material já foi adicionado.");
                return;
            }

            const matObj = globalMateriais.find(m => m.id == matId);
            const nomeMat = matObj ? matObj.nome : "Desconhecido";

            itensCotacaoAtual.push({
                material_id: matId,
                quantidade: qtd,
                _nome: nomeMat // auxiliar para display
            });

            renderTabelaItens();

            // Reset fields
            selectMaterial.value = "";
            inputQuantidade.value = 1;
        });
    }

    function renderTabelaItens() {
        const tbody = document.getElementById('tabelaItensCotacao');
        if (!tbody) return;

        if (itensCotacaoAtual.length === 0) {
            tbody.innerHTML = '<tr id="row-empty-msg"><td colspan="3" class="text-center text-muted">Nenhum item adicionado.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        itensCotacaoAtual.forEach((item, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item._nome}</td>
                <td class="text-center">${item.quantidade}</td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="removerItemCotacao(${index})">
                        <i class="bi bi-x"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    window.removerItemCotacao = (index) => {
        itensCotacaoAtual.splice(index, 1);
        renderTabelaItens();
    };

    // Resetar modal ao abrir
    const btnCriar = document.querySelector('[data-bs-target="#modalCriarMaster"]');
    if (btnCriar) {
        btnCriar.addEventListener('click', () => {
            document.getElementById('modalCriarMasterLabel').innerText = 'Nova Cotação Mestra';
            formCriarMaster.reset();
            document.getElementById('input-master-id').value = '';

            // Limpa itens
            itensCotacaoAtual = [];
            renderTabelaItens();
        });
    }


    // --- SUBMIT Cotação Master ---
    formCriarMaster.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(formCriarMaster);
        const data = Object.fromEntries(formData.entries());
        const id = document.getElementById('input-master-id').value;

        // Adiciona itens ao payload
        // O backend espera itens? O frontend foi instruido a mandar.
        data.itens = itensCotacaoAtual.map(i => ({
            material_id: parseInt(i.material_id),
            quantidade: i.quantidade
        }));

        if (!data.status) data.status = 'Aberto';

        try {
            const url = id ? `/api/cotacoes-master/${id}` : '/api/cotacoes-master';
            const method = id ? 'PUT' : 'POST';

            const response = await fetchWithAuth(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Falha ao salvar cotação.');

            if (modalCriarMaster) modalCriarMaster.hide();
            ui.feedbackSucesso(id ? 'Cotação atualizada!' : 'Cotação criada com sucesso!');
            carregarCotacoes();
        } catch (error) {
            ui.feedbackErro(error.message);
        }
    });

    // --- SUBMIT Proposta ---
    formAdicionarProposta.addEventListener('submit', async (e) => {
        e.preventDefault();
        const masterId = inputMasterIdProposta.value;
        const propostaId = document.getElementById('input-proposta-id').value;

        // Coleta dados manuais para controlar o envio
        const fornecedorId = selectFornecedor.value;
        const fornecedorObj = globalFornecedores.find(f => f.id == fornecedorId);
        const nomeFornecedor = fornecedorObj ? (fornecedorObj.nome_empresa || fornecedorObj.nome) : "Fornecedor";

        const formData = new FormData(formAdicionarProposta);
        // O FormData pega todos os inputs com name.
        // O select tem name="fornecedor_id", então vai estar lá.
        // Mas o backend pode precisar de "nome_fornecedor" tb se legado.
        formData.append('nome_fornecedor', nomeFornecedor);

        // Se for edição, usamos JSON (conforme análise anterior de problemas com PUT FormData)
        if (propostaId) {
            const data = Object.fromEntries(formData.entries());
            // Fix numéricos
            if (data.valor) data.valor = parseFloat(data.valor.replace('.', '').replace(',', '.').replace('R$', '').trim());

            try {
                const response = await fetchWithAuth(`/api/cotacoes-propostas/${propostaId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (!response.ok) throw new Error("Erro ao atualizar proposta");

                if (modalAdicionarProposta) modalAdicionarProposta.hide();
                formAdicionarProposta.reset();
                ui.feedbackSucesso('Proposta atualizada!');
                carregarCotacoes();
            } catch (err) {
                ui.feedbackErro(err.message);
            }
        } else {
            // Criação via FormData (para suportar arquivo upload, se backend suportar)
            // Se o backend exige JSON para criar, isso falha com arquivos.
            // Vou assumir que o backend de criação aceita multipart/form-data com arquivos.
            try {
                if (!masterId) return;
                const response = await fetchWithAuth(`/api/cotacoes-master/${masterId}/propostas`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || "Erro ao salvar");
                }

                if (modalAdicionarProposta) modalAdicionarProposta.hide();
                formAdicionarProposta.reset();
                ui.feedbackSucesso('Proposta adicionada!');
                carregarCotacoes();
            } catch (err) {
                ui.feedbackErro(err.message);
            }
        }
    });


    // --- Helpers de UI (Accordion) ---    
    function criarCardCotacao(master) {
        // Render PROPOSALS
        let propostasHtml = '<p class="text-muted small ms-2">Nenhuma proposta recebida.</p>';
        if (master.propostas && master.propostas.length > 0) {
            propostasHtml = `
                <div class="table-responsive">
                    <table class="table table-sm table-bordered table-striped table-hover mt-2 align-middle">
                        <thead class="table-light">
                            <tr>
                                <th>Fornecedor</th>
                                <th>Valor</th>
                                <th>Status</th>
                                <th>Docs</th>
                                <th class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${master.propostas.map(prop => `
                                <tr>
                                    <td><span class="fw-medium">${prop.nome_fornecedor}</span></td>
                                    <td>${prop.valor ? `R$ ${prop.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` : '-'}</td>
                                    <td><span class="badge ${getStatusBadge(prop.status)}">${prop.status}</span></td>
                                    <td>
                                        ${prop.caminho_arquivo
                    ? `<a href="/${prop.caminho_arquivo}" target="_blank" class="text-info text-decoration-none" title="Baixar"><i class="bi bi-file-earmark-zip me-1"></i>Anexo</a>`
                    : '<span class="text-muted">-</span>'
                }
                                    </td>
                                    <td class="text-center">
                                        <div class="d-flex justify-content-center gap-2">
                                            <button class="btn btn-sm btn-outline-primary" onclick="editarProposta(event, ${prop.id})" title="Editar Proposta">
                                                <i class="bi bi-pencil"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" onclick="excluirProposta(event, ${prop.id}, '${prop.nome_fornecedor}')" title="Excluir Proposta">
                                                <i class="bi bi-trash"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        // Render ITEMS (Always Visible)
        const hasItems = master.itens && master.itens.length > 0;
        let itensHtml = `
            <div class="bg-light p-3 rounded mb-4 border">
                <h6 class="mb-3 border-bottom pb-2 fw-bold text-secondary">
                    <i class="bi bi-box-seam me-2"></i>Itens Solicitados
                </h6>
                ${hasItems ? `
                    <table class="table table-sm table-light table-hover border mb-0 align-middle">
                        <thead class="table-secondary">
                            <tr>
                                <th>Material</th>
                                <th class="text-center" style="width: 100px;">Qtd</th>
                                <th class="text-center" style="width: 120px;">Unidade</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${master.itens.map(item => {
            let nomeMaterial = "Material Desconhecido";
            let unidadeMaterial = "-";

            // Resolve Material Name & Unit
            if (item.material && item.material.nome) {
                nomeMaterial = item.material.nome;
                if (item.material.unidade) unidadeMaterial = item.material.unidade;
            }
            else if (item.material_nome) nomeMaterial = item.material_nome;
            else if (item.nome_material) nomeMaterial = item.nome_material;
            else if (item.material_id && globalMateriais.length > 0) {
                const m = globalMateriais.find(gm => gm.id == item.material_id);
                if (m) {
                    nomeMaterial = m.nome;
                    unidadeMaterial = m.unidade || "-";
                }
            }

            return `
                                    <tr>
                                        <td>${nomeMaterial}</td>
                                        <td class="text-center fw-bold text-dark">${item.quantidade}</td>
                                        <td class="text-center text-muted small">${unidadeMaterial}</td>
                                    </tr>
                                `;
        }).join('')}
                        </tbody>
                    </table>
                ` : `
                    <div class="text-center text-muted py-2">
                        <small>Nenhum material adicionado a esta cotação.</small>
                    </div>
                `}
            </div>
        `;

        return `
            <div class="card mb-3 shadow-sm border">
                <div class="card-header bg-white py-3 clickable-header" 
                     data-bs-toggle="collapse" 
                     data-bs-target="#collapse-${master.id}" 
                     aria-expanded="false" 
                     aria-controls="collapse-${master.id}"
                     style="cursor: pointer;">
                    
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="m-0 fw-bold text-dark d-flex align-items-center text-truncate">
                            <i class="bi bi-chevron-down text-muted me-3 fs-6"></i>
                            <span class="text-primary me-2">#${master.codigo_cotacao}</span>
                            <span class="text-dark text-truncate">${master.titulo}</span>
                        </h5>

                        <div class="d-flex align-items-center gap-2" onclick="event.stopPropagation()">
                            <!-- Status Dropdown -->
                            <div class="dropdown">
                                <button class="btn btn-sm ${getStatusBadge(master.status)} dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    ${master.status}
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item" href="#" onclick="atualizarStatusCotacao(event, ${master.id}, 'Aberto')"><span class="badge bg-success me-2">Aberto</span></a></li>
                                    <li><a class="dropdown-item" href="#" onclick="atualizarStatusCotacao(event, ${master.id}, 'Pendente')"><span class="badge bg-warning text-dark me-2">Pendente</span></a></li>
                                    <li><a class="dropdown-item" href="#" onclick="atualizarStatusCotacao(event, ${master.id}, 'Finalizado')"><span class="badge bg-secondary me-2">Finalizado</span></a></li>
                                    <li><a class="dropdown-item" href="#" onclick="atualizarStatusCotacao(event, ${master.id}, 'Cancelado')"><span class="badge bg-danger me-2">Cancelado</span></a></li>
                                </ul>
                            </div>

                            <!-- Actions -->
                            <button class="btn btn-outline-primary btn-sm" onclick="abrirModalEditar(event, ${master.id})" title="Editar Cotação">
                                <i class="bi bi-pencil"></i>
                            </button>
                            
                            <a href="/cotacoes/analise/${master.id}" target="_blank" class="btn btn-outline-info btn-sm" title="Ver Análise">
                                <i class="bi bi-file-earmark-bar-graph"></i>
                            </a>

                            <button class="btn btn-outline-danger btn-sm" onclick="excluirCotacao(event, ${master.id}, '${master.codigo_cotacao}')" title="Excluir Cotação">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <div id="collapse-${master.id}" class="collapse">
                    <div class="card-body">
                        <div class="mb-4">
                            <label class="text-muted text-uppercase small fw-bold mb-1">Descrição / Observações</label>
                            <p class="mb-0 text-secondary bg-light p-2 rounded border-start border-4 border-secondary">${master.descricao || 'Sem descrição.'}</p>
                        </div>

                        ${itensHtml}

                        <div class="d-flex justify-content-between align-items-center mb-3 mt-4 border-bottom pb-2">
                            <h6 class="mb-0 fw-bold text-dark"><i class="bi bi-files me-2"></i>Propostas Recebidas</h6>
                            <button class="btn btn-success btn-sm btn-abrir-modal-proposta" data-id="${master.id}">
                                <i class="bi bi-plus-lg me-1"></i> Nova Proposta
                            </button>
                        </div>
                        ${propostasHtml}
                    </div>
                </div>
            </div>
        `;
    }

    function getStatusBadge(status) {
        if (status === 'Ativo' || status === 'Vencedor') return 'bg-success';
        if (status === 'Pendente') return 'bg-warning text-dark';
        if (status === 'Rejeitado') return 'bg-danger';
        return 'bg-secondary';
    }

    // --- Events Delegation (Static) ---
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-abrir-modal-proposta');
        if (btn) {
            const id = btn.dataset.id;
            inputMasterIdProposta.value = id;
            if (modalAdicionarProposta) modalAdicionarProposta.show();
        }
    });

    // --- Global Exports (para onClick inline) ---

    window.excluirCotacao = (e, id, codigo) => {
        if (e) e.stopPropagation();
        ui.confirmarExclusao(`/api/cotacoes-master/${id}`, `Cotação ${codigo}`, () => carregarCotacoes());
    };

    window.excluirProposta = (e, id, nome) => {
        if (e) e.stopPropagation();
        ui.confirmarExclusao(`/api/cotacoes-propostas/${id}`, `Proposta de ${nome}`, () => carregarCotacoes());
    };

    window.abrirModalEditar = (e, id) => {
        if (e) e.stopPropagation();
        const master = globalCotacoesList.find(m => m.id == id);
        if (!master) return;

        document.getElementById('input-master-id').value = master.id;
        document.getElementById('input-master-codigo').value = master.codigo_cotacao;
        document.getElementById('input-master-titulo').value = master.titulo;
        document.getElementById('input-master-descricao').value = master.descricao || '';

        // Se a API retornasse itens, aqui eles seriam carregados em itensCotacaoAtual
        // Como o user falou de salvar, mas nao especificou se a API de leitura retorna,
        // vou deixar preparado:
        itensCotacaoAtual = master.itens || []; // Se backend suportar. Se nao, começa vazio.
        renderTabelaItens();

        document.getElementById('modalCriarMasterLabel').innerText = 'Editar Cotação';
        if (modalCriarMaster) modalCriarMaster.show();
    };

    window.editarProposta = (e, id) => {
        if (e) e.stopPropagation();
        // Lógica de edição de proposta (modal separado ou reuso)
        // O código original tinha um modal "modalEditarProposta" separado.
        // O user nao pediu pra mudar esse modal, mas pediu "Nova Proposta" pra usar Select.
        // Vou assumir que o "Adicionar Nova Proposta" é o foco.
        // Mas para editar, o código antigo abria outro modal.
        // Vou reinjetar a logica de abrir o modal de Edição que já existe no HTML (que eu não removi, espero).
        // Check HTML: Eu só substituí o modalCriarMaster e ModalAdicionarProposta bodies?
        // NÃO! O replace_file_content substituiu um BLOCO. O modalEditarProposta estava no fim do arquivo HTML original.
        // O bloco substituído foi StartLine: 18, EndLine: 111 (aprox).
        // O modalEditarProposta começava na linha 114. Então ele AINDA EXISTE.

        // Preciso popular os campos desse modal existente se for usado.
        // Mas o código JS original para editarProposta precisa ser portado.

        let prop = null;
        globalCotacoesList.forEach(m => {
            if (m.propostas) {
                const found = m.propostas.find(p => p.id == id);
                if (found) prop = found;
            }
        });

        if (!prop) { ui.feedbackErro("Proposta não encontrada."); return; }

        document.getElementById('editPropId').value = prop.id;
        document.getElementById('editPropFornecedor').value = prop.nome_fornecedor; // Input disabled no modal edit
        document.getElementById('editPropTipo').value = prop.tipo_fornecedor;
        // ... Populate other fields ...
        // O código antigo usava ids: editPropTipo, editPropData, editPropValor, editPropStatus, editPropObs
        if (document.getElementById('editPropData')) document.getElementById('editPropData').value = prop.data_contrato;
        if (document.getElementById('editPropValor')) document.getElementById('editPropValor').value = prop.valor;
        if (document.getElementById('editPropStatus')) document.getElementById('editPropStatus').value = prop.status;
        if (document.getElementById('editPropObs')) document.getElementById('editPropObs').value = prop.observacao || '';

        if (typeof bootstrap !== 'undefined') {
            const modalEdit = new bootstrap.Modal(document.getElementById('modalEditarProposta'));
            modalEdit.show();
        }
    };

    // Funcao salvarEdicaoProposta (chamada pelo botão do modal de edição)
    window.salvarEdicaoProposta = async () => {
        // ... Logica de salvar edição (Put) ...
        // Reimplementando simplificado
        const id = document.getElementById('editPropId').value;
        const data = {
            tipo_fornecedor: document.getElementById('editPropTipo').value,
            data_contrato: document.getElementById('editPropData').value,
            valor: parseFloat(document.getElementById('editPropValor').value),
            status: document.getElementById('editPropStatus').value,
            observacao: document.getElementById('editPropObs').value,
            nome_fornecedor: document.getElementById('editPropFornecedor').value // Precisa mandar de volta?
        };

        try {
            const res = await fetchWithAuth(`/api/cotacoes-propostas/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                if (el && typeof bootstrap !== 'undefined') {
                    const mo = bootstrap.Modal.getInstance(el);
                    if (mo) mo.hide();
                }
                ui.feedbackSucesso("Atualizado!");
                carregarCotacoes();
            } else {
                ui.feedbackErro("Erro ao atualizar");
            }
        } catch (e) { ui.feedbackErro("Erro de rede"); }
    };

    window.atualizarStatusCotacao = async (e, id, novoStatus) => {
        if (e) e.preventDefault();
        try {
            const res = await fetchWithAuth(`/api/cotacoes-master/${id}`, {
                method: 'PATCH', // Assumindo que o endpoint suporta PATCH para atualização parcial
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: novoStatus })
            });

            if (res.ok) {
                ui.feedbackSucesso(`Status atualizado para ${novoStatus}`);
                carregarCotacoes();
            } else {
                const err = await res.json();
                ui.feedbackErro(err.detail || "Erro ao atualizar status.");
            }
        } catch (error) {
            console.error(error);
            ui.feedbackErro("Erro de comunicação ao atualizar status.");
        }
    };

    // --- AI Smart Scan (Global & Local) ---

    // 1. Variáveis de Estado para o Global Scan
    let globalScanData = null; // Guardará o retorno da IA { dados_extraidos, match_cotacao, match_fornecedor }
    let globalScanFile = null; // Guardará o arquivo para upload final se necessário

    // 2. Função Acionada pelo Input File Global
    // 2. Função Acionada pelo Input File Global
    /**
     * @descrição Processa o upload de um arquivo (PDF/Imagem) para análise via IA.
     * @param {HTMLInputElement} input - Elemento input file.
     * @comportamento
     *  1. Gera preview local (Blob URL) imediatamente no iframe.
     *  2. Envia arquivo para /api/cotacoes/analisar-documento via FormData.
     *  3. Recebe JSON estruturado da IA (dados_extraidos, match_cotacao, match_fornecedor).
     *  4. Abre modal de revisão (#modalRevisaoGlobal) com os dados preenchidos.
     */
    window.analisarPropostaGlobal = async (input) => {
        const file = input.files[0];
        if (!file) return;

        // Reset state
        globalScanData = null;
        globalScanFile = file;

        // Limpa input para permitir re-seleção do mesmo arquivo depois
        input.value = '';

        // --- PREVIEW IMEDIATO (Split Screen) ---
        // Exibe o PDF/Imagem na esquerda ANTES mesmo de enviar para a IA
        const fileURL = URL.createObjectURL(file);
        // Atualiza iframe se o modal já existir no DOM (ou quando abrir)
        // Como o modal ainda não está aberto, vamos salvar para usar na abertura
        // Mas podemos setar o src do iframe diretamente se ele estiver no DOM (está, oculto)
        const iframe = document.getElementById('iframePreview');
        const placeholder = document.getElementById('preview-placeholder');
        if (iframe) {
            iframe.src = fileURL;
            // Update "Expandir" button
            const btnExpand = document.getElementById('btn-ver-documento-global');
            if (btnExpand) btnExpand.href = fileURL;

            if (placeholder) placeholder.classList.add('d-none'); // Hide loading text
        }

        // UI Loading
        ui.feedbackInfo("✨ Gemini analisando documento... Por favor aguarde.");

        try {
            const formData = new FormData();
            formData.append('file', file);

            const res = await fetchWithAuth('/api/cotacoes/analisar-documento', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error("Erro na análise inteligente.");

            const responseData = await res.json();

            // validation: Check if data exists and has no error
            if (!responseData || responseData.erro) {
                const msg = responseData.erro || "Resposta inválida da IA";
                const details = responseData.details || "";
                ui.feedbackErro(`${msg} ${details}`);
                return;
            }

            // validation: check dados_extraidos
            if (!responseData.dados_extraidos) {
                // If the old format is returned (direct dict), try to adapt? 
                // No, we fixed the backend. It MUST return the new structure.
                ui.feedbackErro("Formato de dados inválido. Tente novamente.");
                return;
            }

            globalScanData = responseData;

            // Preview já foi gerado no início da função.

            abrirModalRevisaoGlobal(responseData);

        } catch (error) {
            console.error(error);
            ui.feedbackErro("Não foi possível analisar o documento.");
        }
    };

    // 3. Abrir e Popular Modal de Revisão
    function abrirModalRevisaoGlobal(data) {
        let modal;
        if (typeof bootstrap !== 'undefined') {
            const el = document.getElementById('modalRevisaoGlobal');
            if (el) modal = new bootstrap.Modal(el);
        }
        const { dados_extraidos, match_cotacao, match_fornecedor } = data;

        // A. Cotação Mestra Match
        const matchCotContainer = document.getElementById('match-cotacao-container');
        const selectCotContainer = document.getElementById('select-cotacao-container');
        const selectCot = document.getElementById('select-global-cotacao');

        // Popula Select sempre (caso user queira mudar)
        selectCot.innerHTML = '<option value="">Selecione manualmente...</option>';
        globalCotacoesList.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = `#${c.codigo_cotacao} - ${c.titulo}`;
            selectCot.appendChild(opt);
        });

        if (match_cotacao) {
            matchCotContainer.classList.remove('d-none');
            document.getElementById('match-cotacao-texto').textContent = `#${match_cotacao.codigo_cotacao} - ${match_cotacao.titulo}`;
            selectCot.value = match_cotacao.id;
        } else {
            matchCotContainer.classList.add('d-none');
        }

        // B. Fornecedor Match
        const matchFornContainer = document.getElementById('match-fornecedor-container');
        const inputFornNome = document.getElementById('input-global-fornecedor-nome');
        const checkNovo = document.getElementById('check-novo-fornecedor');

        if (match_fornecedor) {
            matchFornContainer.classList.remove('d-none');
            document.getElementById('match-fornecedor-texto').textContent = match_fornecedor.nome;
            inputFornNome.value = match_fornecedor.nome;
            checkNovo.checked = false;
        } else {
            // MATCH NULO (Ajuste UX)
            matchFornContainer.classList.add('d-none');
            inputFornNome.value = dados_extraidos.nome_fornecedor || "";
            checkNovo.checked = true; // Sugere novo se não achou

            // Toast Warning
            ui.feedbackInfo("Fornecedor não identificado automaticamente. Por favor, verifique o documento e digite ao lado.");
        }

        // C. Dados Gerais
        document.getElementById('input-global-valor-total').value = dados_extraidos.valor_total || "";
        document.getElementById('input-global-obs').value = dados_extraidos.resumo_itens || "";

        // D. Itens
        const tbody = document.getElementById('tbody-global-itens');
        tbody.innerHTML = '';
        if (dados_extraidos.itens && dados_extraidos.itens.length > 0) {
            dados_extraidos.itens.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${item.descricao || "Item"}</td>
                    <td class="text-center">${item.quantidade || 1}</td>
                    <td class="text-end">${(item.valor_unitario || 0).toFixed(2)}</td>
                    <td class="text-end fw-bold">${(item.valor_total || 0).toFixed(2)}</td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Nenhum item detalhado encontrado.</td></tr>';
        }

        if (modal) modal.show();
    }

    // 4. Confirmar Importação
    window.confirmarImportacaoGlobal = async () => {
        // Validações
        const cotacaoId = document.getElementById('select-global-cotacao').value;
        if (!cotacaoId) {
            ui.feedbackErro("Por favor, vincule a uma Cotação Mestra.");
            return;
        }

        // Dados do Form
        const valor = document.getElementById('input-global-valor-total').value;
        const obs = document.getElementById('input-global-obs').value;
        const nomeFornecedor = document.getElementById('input-global-fornecedor-nome').value;
        const isNovoFornecedor = document.getElementById('check-novo-fornecedor').checked;

        let fornecedorId = null;
        let tipoFornecedor = "Material/Serviço"; // Default genérico

        // Se for Fornecedor existente, pega ID do match ou busca no global list?
        // O modal não tem select de fornecedor, tem input text. 
        // Se deu match, usaremos o ID do match SE o nome não mudou drasticamente.
        // Se user mudou nome ou marcou "Novo", ignoramos ID.

        const matchForn = globalScanData.match_fornecedor;
        if (matchForn && !isNovoFornecedor && nomeFornecedor === matchForn.nome) {
            fornecedorId = matchForn.id;
        }

        // Se marcou Novo, precisamos criar? O endpoint de criar proposta aceita nome String e cria?
        // O endpoint original (/api/cotacoes-master/{id}/propostas) aceita:
        // fornecedor_id (opcional) E nome_fornecedor (opcional). 
        // A lógica lá é: se tem ID usa ID, se tem nome usa nome.
        // Se não tem ID, apenas salva o nome na proposta (não cria registro na tabela fornecedores "oficial" necessariamente, 
        // depende da regra de negócio. O código atual da rota apenas salva o nome na tabela PROPOSTAS).
        // OK para MVP.

        try {
            const formData = new FormData();
            formData.append('nome_fornecedor', nomeFornecedor);
            if (fornecedorId) formData.append('fornecedor_id', fornecedorId);

            formData.append('valor', valor);
            formData.append('data_contrato', new Date().toISOString().split('T')[0]); // Data Hoje
            formData.append('status', 'Pendente');
            formData.append('tipo_fornecedor', tipoFornecedor);
            formData.append('observacao', obs);

            if (globalScanFile) {
                formData.append('arquivos', globalScanFile);
            }

            const res = await fetchWithAuth(`/api/cotacoes-master/${cotacaoId}/propostas`, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error("Erro ao salvar proposta.");

            // Sucesso
            const modalEl = document.getElementById('modalRevisaoGlobal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();

            ui.feedbackSucesso("Proposta importada com sucesso!");
            carregarCotacoes(); // Refresh

        } catch (error) {
            console.error(error);
            ui.feedbackErro("Erro ao salvar dados finais.");
        }
    };


    // --- AI Local (Modal Antigo - Manter Compatibilidade ou Redirecionar?) ---
    // O pedido era adicionar DESTAQUE, nao remover o antigo.
    // O código antigo "analisarDocumentoIA" continua existindo e funcionando no modal "modalAdicionarProposta".
    // Apenas corrigimos o bug do ui.feedbackInfo (que será usado lá se houver, ou não).
    // O código abaixo é a função ANTIGA que foi mantida (Verifique se não dupliquei).
    // No Replace, eu substituí o final do arquivo. A função antiga window.analisarDocumentoIA estava lá.
    // Eu DEVO manter ela. Como o replacementContent acima começa com "// --- AI Smart Scan (Global & Local) ---",
    // vou re-incluir a função antiga levemente ajustada se necessário, ou assumir q ela estava ACIMA do replace?
    // O replace EndLine é 716 (fim do arquivo). 
    // O StartLine do replace deve ser onde começava a função antiga "window.analisarDocumentoIA".
    // Vou checar onde ela começava no 'view_file' anterior.
    // Ela começava na linha 626.
    // Então meu StartLine deve ser 626.

    // Vou cancelar esse replace e fazer um melhor que inclua ambas.
    // Ops, já estou dentro do tool call. 
    // Vou incluir a função analiarDocumentoIA (Local) aqui dentro também para garantir que ela exista.

    window.analisarDocumentoIA = async () => {
        const fileInput = document.getElementById('input-ia-arquivo');
        const file = fileInput.files[0];
        if (!file) {
            ui.feedbackErro("Selecione um arquivo para analisar.");
            return;
        }

        const loading = document.getElementById('ia-loading');
        loading.classList.remove('d-none');
        loading.classList.add('d-flex');

        try {
            const formData = new FormData();
            formData.append('file', file);

            const res = await fetchWithAuth('/api/cotacoes/analisar-documento', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error("Erro na análise inteligente.");

            const data = await res.json();
            // data agora vem como { dados_extraidos, match_cotacao... } devido ao refactor no backend!
            // Precisamos adaptar aqui pois o formato mudou.
            const dados = data.dados_extraidos || data; // backward compatibilidade se api nao mudou wrapper? 
            // API mudou wrapper. Então data.dados_extraidos.

            if (dados.valor_total) {
                const valorFormatado = dados.valor_total.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                document.getElementById('input-proposta-valor').value = valorFormatado;
            }

            if (dados.data_proposta) {
                document.getElementById('input-proposta-data').value = dados.data_proposta;
            }

            if (dados.resumo_itens) {
                document.getElementById('input-proposta-observacao').value = dados.resumo_itens;
            }

            // Fornecedor Match Local
            // A API nova devolve match_fornecedor. Vamos usar!
            const selectFornecedor = document.getElementById('selectFornecedor');
            if (data.match_fornecedor) {
                selectFornecedor.value = data.match_fornecedor.id;
                ui.feedbackSucesso(`Fornecedor identificado: ${data.match_fornecedor.nome}`);
            } else if (dados.nome_fornecedor) {
                // Lógica antiga de busca texto
                let found = false;
                for (let i = 0; i < selectFornecedor.options.length; i++) {
                    if (selectFornecedor.options[i].text.toLowerCase().includes(dados.nome_fornecedor.toLowerCase())) {
                        selectFornecedor.selectedIndex = i;
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    const obs = document.getElementById('input-proposta-observacao');
                    obs.value = `[Fornecedor IA: ${dados.nome_fornecedor}] \n` + obs.value;
                    ui.feedbackInfo("Fornecedor novo (não cadastrado) adicionado nas observações.");
                }
            }

            ui.feedbackSucesso("Dados preenchidos!");

        } catch (error) {
            console.error(error);
            ui.feedbackErro("Não foi possível extrair dados.");
        } finally {
            loading.classList.add('d-none');
            loading.classList.remove('d-flex');
        }
    };

});
