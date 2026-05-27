const API_URL = '/api/admin/dispositivos';
let currentDevicesList = [];

// ==========================================
// 1. CARREGAMENTO E RENDERIZAÇÃO
// ==========================================

async function carregarDispositivos() {
    try {
        const response = await fetchWithAuth(API_URL);
        if (!response.ok) throw new Error('Falha ao carregar dispositivos do inventário');
        currentDevicesList = await response.json();

        renderizarTabela();
        atualizarKPIs();
    } catch (error) {
        console.error(error);
        if (window.ui) ui.feedbackErro('Erro ao carregar inventário: ' + error.message);
    }
}

function renderizarTabela(filtroText = '') {
    const tbody = document.getElementById('tbody-dispositivos');
    if (!tbody) return;

    tbody.innerHTML = '';

    const textNormalized = filtroText.toLowerCase().trim();
    const filtrados = currentDevicesList.filter(disp => {
        if (!textNormalized) return true;
        return (
            disp.tipo.toLowerCase().includes(textNormalized) ||
            disp.marca_modelo.toLowerCase().includes(textNormalized) ||
            disp.numero_serie_imei.toLowerCase().includes(textNormalized) ||
            (disp.responsavel_atual && disp.responsavel_atual.toLowerCase().includes(textNormalized)) ||
            disp.status.toLowerCase().includes(textNormalized)
        );
    });

    if (filtrados.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">Nenhum dispositivo encontrado${filtroText ? ' correspondente ao filtro' : ''}.</td></tr>`;
        return;
    }

    filtrados.forEach(disp => {
        const tr = document.createElement('tr');

        // Ícone baseado no tipo de dispositivo
        let tipoIcon = 'bi-cpu';
        const tipoLower = disp.tipo.toLowerCase();
        if (tipoLower.includes('notebook')) tipoIcon = 'bi-laptop';
        else if (tipoLower.includes('desktop') || tipoLower.includes('computador')) tipoIcon = 'bi-pc-display';
        else if (tipoLower.includes('monitor')) tipoIcon = 'bi-display';
        else if (tipoLower.includes('celular') || tipoLower.includes('smartphone') || tipoLower.includes('fone')) tipoIcon = 'bi-phone';
        else if (tipoLower.includes('tablet')) tipoIcon = 'bi-tablet';
        else if (tipoLower.includes('impressora')) tipoIcon = 'bi-printer';

        // Badge de Status colorida
        let statusBadge = `<span class="badge bg-secondary">${disp.status}</span>`;
        if (disp.status === 'Disponível') {
            statusBadge = `<span class="badge bg-success">Disponível</span>`;
        } else if (disp.status === 'Em Uso') {
            statusBadge = `<span class="badge bg-primary">Em Uso</span>`;
        } else if (disp.status === 'Manutenção') {
            statusBadge = `<span class="badge bg-warning text-dark">Manutenção</span>`;
        } else if (disp.status === 'Descartado') {
            statusBadge = `<span class="badge bg-danger">Descartado</span>`;
        }

        // Render da coluna de Termo de Responsabilidade
        let termoCol = '';
        if (disp.url_termo_pdf) {
            termoCol = `
                <div class="d-flex align-items-center justify-content-center gap-2">
                    <button class="btn btn-sm btn-light border text-danger fw-bold shadow-sm d-flex align-items-center py-1 px-2" onclick="visualizarTermo('${disp.id}')" title="Visualizar Termo Assinado">
                        <i class="bi bi-file-earmark-pdf-fill me-1"></i> Termo
                    </button>
                    <button class="btn btn-sm btn-outline-secondary p-1" onclick="dispararUpload('${disp.id}')" title="Atualizar Termo PDF">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                </div>
            `;
        } else {
            termoCol = `
                <div class="d-flex align-items-center justify-content-center gap-2">
                    <span class="badge bg-light text-secondary border">Sem Termo</span>
                    <button class="btn btn-sm btn-outline-primary py-1 px-2 shadow-sm d-flex align-items-center" onclick="dispararUpload('${disp.id}')" title="Fazer Upload do Termo PDF">
                        <i class="bi bi-upload me-1 small"></i> Upload
                    </button>
                </div>
            `;
        }

        // Inputs invisíveis para upload individual de arquivo
        const inputUploadOculto = `<input type="file" id="file-upload-${disp.id}" class="d-none" accept=".pdf" onchange="uploadTermoPDF('${disp.id}')">`;

        tr.innerHTML = `
            <td class="fw-bold text-dark">
                <i class="bi ${tipoIcon} text-primary me-2"></i>${disp.marca_modelo}
                <div class="small text-muted fw-normal ps-4">${disp.tipo}</div>
            </td>
            <td class="fw-mono small">${disp.numero_serie_imei}</td>
            <td>${disp.responsavel_atual || '<span class="text-muted small">-</span>'}</td>
            <td class="text-center">${termoCol}${inputUploadOculto}</td>
            <td class="text-center">${statusBadge}</td>
            <td class="text-center">
                <button class="btn btn-warning btn-sm shadow-sm me-1" onclick="editarDispositivo('${disp.id}')" title="Editar">
                    <i class="bi bi-pencil-square"></i>
                </button>
                <button class="btn btn-danger btn-sm shadow-sm" onclick="deletarDispositivo('${disp.id}')" title="Excluir">
                    <i class="bi bi-trash-fill"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function atualizarKPIs() {
    const kpiTotal = document.getElementById('kpi-total');
    const kpiDisponivel = document.getElementById('kpi-disponivel');
    const kpiEmUso = document.getElementById('kpi-em-uso');
    const kpiSemTermo = document.getElementById('kpi-sem-termo');

    if (!kpiTotal) return;

    const total = currentDevicesList.length;
    const disponiveis = currentDevicesList.filter(d => d.status === 'Disponível').length;
    const emUso = currentDevicesList.filter(d => d.status === 'Em Uso').length;
    const semTermo = currentDevicesList.filter(d => !d.url_termo_pdf).length;

    kpiTotal.textContent = total;
    kpiDisponivel.textContent = disponiveis;
    kpiEmUso.textContent = emUso;
    kpiSemTermo.textContent = semTermo;
}

// ==========================================
// 2. OPERAÇÕES CRUD (DISPOSITIVO)
// ==========================================

window.editarDispositivo = function(id) {
    const disp = currentDevicesList.find(d => String(d.id) === String(id));
    if (!disp) return;

    // Preencher formulário lateral
    document.getElementById('dispositivo_id').value = disp.id;
    document.getElementById('tipo').value = disp.tipo;
    document.getElementById('marca_modelo').value = disp.marca_modelo;
    document.getElementById('numero_serie_imei').value = disp.numero_serie_imei;
    document.getElementById('responsavel_atual').value = disp.responsavel_atual || '';
    document.getElementById('status').value = disp.status;

    // Ajustar Layout e UX para Edição
    document.getElementById('form-titulo').innerHTML = '<i class="bi bi-pencil-square me-1"></i> Editar Dispositivo';
    const btnCancel = document.getElementById('btn-cancelar-edicao');
    if (btnCancel) btnCancel.classList.remove('d-none');

    // Rolar suavemente até o formulário no mobile
    const formEl = document.getElementById('form-dispositivo');
    if (formEl) {
        formEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

window.cancelarEdicao = function() {
    const form = document.getElementById('form-dispositivo');
    if (!form) return;

    form.reset();
    form.classList.remove('was-validated');
    document.getElementById('dispositivo_id').value = '';

    document.getElementById('form-titulo').innerHTML = '<i class="bi bi-plus-circle-fill me-1"></i> Cadastrar Dispositivo';
    const btnCancel = document.getElementById('btn-cancelar-edicao');
    if (btnCancel) btnCancel.classList.add('d-none');
}

window.deletarDispositivo = function(id) {
    if (window.ui) {
        ui.confirmarExclusao(
            `${API_URL}/${id}`,
            `Equipamento`,
            () => carregarDispositivos()
        );
    }
}

// ==========================================
// 3. UPLOAD E DOWNLOAD ASSINADO (TERMOS)
// ==========================================

window.dispararUpload = function(id) {
    const input = document.getElementById(`file-upload-${id}`);
    if (input) input.click();
}

window.uploadTermoPDF = async function(id) {
    const input = document.getElementById(`file-upload-${id}`);
    if (!input || input.files.length === 0) return;

    const file = input.files[0];
    
    // Validação de tipo (apenas PDF)
    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
        ui.feedbackErro('Apenas arquivos PDF são aceitos para Termos de Responsabilidade.');
        input.value = ''; // Limpa
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        if (window.ui && window.Swal) Swal.showLoading();

        // fetchWithAuth envia tokens automaticamente, mas por ser multipart, deixamos o browser definir os boundary headers corretos.
        const token = localStorage.getItem('access_token');
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetch(`${API_URL}/${id}/upload-termo`, {
            method: 'POST',
            headers: headers,
            body: formData
        });

        if (response.ok) {
            ui.feedbackSucesso('Termo de Responsabilidade anexado com sucesso!', () => {
                carregarDispositivos();
            });
        } else {
            const err = await response.json();
            ui.feedbackErro('Erro ao carregar arquivo: ' + (err.detail || 'Falha no upload.'));
            input.value = '';
        }
    } catch (error) {
        console.error(error);
        ui.feedbackErro('Erro de conexão ao realizar o upload do arquivo.');
        input.value = '';
    }
}

window.visualizarTermo = async function(id) {
    try {
        if (window.ui && window.Swal) Swal.showLoading();

        const response = await fetchWithAuth(`${API_URL}/${id}/termo-url`);
        if (!response.ok) throw new Error('Não foi possível gerar a URL de visualização.');
        
        const data = await response.json();
        
        if (window.Swal) Swal.close();
        
        if (data.url) {
            // Abre o PDF assinado temporariamente em uma nova aba
            window.open(data.url, '_blank');
        } else {
            ui.feedbackErro('URL de termo inválida ou não encontrada.');
        }
    } catch (error) {
        console.error(error);
        ui.feedbackErro('Erro ao recuperar termo assinado: ' + error.message);
    }
}

// ==========================================
// 4. INICIALIZAÇÃO
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    carregarDispositivos();

    // Filtro de Pesquisa em Tempo Real
    const filtroInput = document.getElementById('filtro-pesquisa');
    if (filtroInput) {
        filtroInput.addEventListener('input', (e) => {
            renderizarTabela(e.target.value);
        });
    }

    // Botão Cancelar Edição
    const btnCancel = document.getElementById('btn-cancelar-edicao');
    if (btnCancel) {
        btnCancel.addEventListener('click', cancelarEdicao);
    }

    // Submit do Form de Dispositivos
    const form = document.getElementById('form-dispositivo');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!form.checkValidity()) {
                e.stopPropagation();
                form.classList.add('was-validated');
                return;
            }

            const id = document.getElementById('dispositivo_id').value;
            const tipo = document.getElementById('tipo').value;
            const marca_modelo = document.getElementById('marca_modelo').value;
            const numero_serie_imei = document.getElementById('numero_serie_imei').value;
            const responsavel_atual = document.getElementById('responsavel_atual').value || null;
            const status = document.getElementById('status').value;

            const isEdit = !!id;
            const payload = { tipo, marca_modelo, numero_serie_imei, responsavel_atual, status };

            const url = isEdit ? `${API_URL}/${id}` : API_URL;
            const method = isEdit ? 'PUT' : 'POST';

            try {
                if (window.ui && window.Swal) Swal.showLoading();

                const response = await fetchWithAuth(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    ui.feedbackSucesso(
                        isEdit ? 'Equipamento atualizado com sucesso!' : 'Equipamento cadastrado com sucesso!',
                        () => {
                            cancelarEdicao();
                            carregarDispositivos();
                        }
                    );
                } else {
                    const err = await response.json();
                    ui.feedbackErro('Erro ao salvar: ' + (err.detail || 'Falha ao salvar. Verifique se o Nº Série/IMEI já existe.'));
                }
            } catch (error) {
                console.error(error);
                ui.feedbackErro('Erro de conexão ao salvar equipamento.');
            }
        });
    }
});
