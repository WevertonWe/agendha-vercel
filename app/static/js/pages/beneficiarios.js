// Cache Busting: Force Update 2026-01-29 v1
import { API_BENEFICIARIOS_URL } from '../shared/api.js';
// import * as ui from '../shared/ui_utils.js'; // REMOVED: Using global window.ui

let dataTable;
// Global State for Import Curation
let currentTriagemData = [];
let currentSelectedIndex = -1;

/**
 * Retorna a classe de cor do Bootstrap com base no texto do status.
 * @param {string} status - O texto do status vindo da API.
 * @returns {string} A classe CSS para o background do badge.
 */
function getStatusBadgeClass(status) {
    const statusLower = status ? String(status).toLowerCase() : '';
    if (statusLower.includes('importado')) return 'bg-primary'; // Blue for Imported
    if (statusLower.includes('cadastrado')) return 'bg-success';
    if (statusLower.includes('em cadastro')) return 'bg-warning text-dark';
    if (statusLower.includes('invalido') || statusLower.includes('inválido')) return 'bg-danger';
    if (statusLower.includes('a construir')) return 'bg-info text-dark';
    return 'bg-secondary';
}

/**
 * Carrega os botões de filtro rápido por município.
 */
/**
 * @descrição Carrega os botões de filtro rápido por município na parte superior da página.
 * @parâmetros Nenhum.
 * @comportamento Faz uma chamada API para buscar o total consolidado por município e gera botões dinâmicos. O botão selecionado fica destacado.
 */
async function carregarFiltrosDeMunicipio() {
    const container = document.getElementById('filtros-rapidos-municipios');
    if (!container) return;
    try {
        const response = await fetchWithAuth('/api/beneficiarios/consolidado/atividades');
        if (!response.ok) throw new Error('Falha ao buscar dados consolidados');
        const dadosConsolidados = await response.json();
        container.innerHTML = ''; // nosec
        const urlParams = new URLSearchParams(window.location.search);
        const municipioFiltroAtivo = urlParams.get('municipio');
        const todosLink = document.createElement('a');
        todosLink.href = '/beneficiarios';
        todosLink.className = !municipioFiltroAtivo ? 'btn btn-primary btn-sm rounded-pill px-3 fw-bold' : 'btn btn-outline-secondary btn-sm rounded-pill px-3';
        todosLink.textContent = 'Todos';
        container.appendChild(todosLink);
        dadosConsolidados.forEach(item => {
            if (item.municipio) {
                const link = document.createElement('a');
                link.href = `/beneficiarios?municipio=${encodeURIComponent(item.municipio)}`;
                link.className = (item.municipio === municipioFiltroAtivo) ? 'btn btn-primary btn-sm rounded-pill px-3 fw-bold' : 'btn btn-outline-secondary btn-sm rounded-pill px-3';
                link.textContent = `${item.municipio} (${item.total_beneficiarios})`;
                container.appendChild(link);
            }
        });
    } catch (error) {
        console.error("Erro ao carregar filtros de município:", error);
        if (error instanceof TypeError && error.message.includes('fetchWithAuth')) {
            console.error("Parece que fetchWithAuth não está definido. Verifique a ordem dos scripts.");
        }
        container.innerHTML = `<span class="text-danger">Erro ao carregar filtros: ${error.message}</span>`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    carregarFiltrosDeMunicipio();

    // --- Referências para os Modais ---
    let modalEdicao;
    if (typeof bootstrap !== 'undefined') {
        const el = document.getElementById('modalEditarPadrao');
        if (el) modalEdicao = new bootstrap.Modal(el);
    }
    const formEdicao = document.getElementById('formEditarPadrao');

    const urlParams = new URLSearchParams(window.location.search);
    const municipioFiltro = urlParams.get('municipio');
    let ajaxUrl = API_BENEFICIARIOS_URL;
    if (municipioFiltro) {
        ajaxUrl = `${API_BENEFICIARIOS_URL}?municipio=${encodeURIComponent(municipioFiltro)}`;
    }

    // --- Verificação de Permissões (Admin) ---
    let isAdmin = false;
    const token = localStorage.getItem('access_token');
    if (token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            if (payload.role === 'admin') {
                isAdmin = true;
            }
        } catch (e) {
            console.error("Erro ao verificar permissões de admin:", e);
        }
    }

    // --- Inicialização da Tabela ---
    /**
     * @descrição Inicializa a tabela DataTables com as colunas e renderizações customizadas.
     * @parâmetros Nenhum (Usa variável global 'ajaxUrl').
     * @comportamento Destrói instância anterior, configura colunas (ID, Nome, CPF, etc.), formatação de Badges de Status, e botões de ação (Editar/Excluir).
     */
    function inicializarTabela() {
        if ($.fn.DataTable.isDataTable('#tabela')) {
            $('#tabela').DataTable().destroy();
        }

        dataTable = $('#tabela').DataTable({
            ajax: { url: ajaxUrl, dataSrc: "" },
            columns: [
                { "data": "id" }, { "data": "nome_tecnico" }, { "data": "cpf_tecnico" },
                { "data": "municipio" }, { "data": "comunidade" }, { "data": "latitude" },
                { "data": "longitude" }, { "data": "data_atividade" }, { "data": "nome_familiar" },
                { "data": "cpf_familiar" }, { "data": "nis" }, { "data": "renda_media" },
                { "data": "status" }, { "data": "tecnico_agua_que_alimenta" }, { "data": "doc_status" },
                { "data": "grh" }, { "data": "verificado_bsf" }, { "data": null }
            ],
            columnDefs: [
                // Center Align: 0 (ID), 2 (CPF Tec), 5-7 (Loc/Data), 9-17 (Data/Status/Actions)
                { "targets": [0, 2, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16], "className": "text-center" },
                // Left Align: 1 (Nome Tec), 3 (Munic), 4 (Comun), 8 (Nome Fam)
                { "targets": [1, 3, 4], "className": "text-start px-3" },
                {
                    "targets": 8,
                    "className": "text-start px-3",
                    "render": function (data, type, row) {
                        return data || row.nome_completo || row.nome || 'Sem Nome';
                    }
                },

                { "targets": 0, "width": "20px", "searchable": false, "orderable": false, "render": (data, type, row, meta) => meta.row + meta.settings._iDisplayStart + 1 },
                { "targets": [2, 9], "render": (data) => data && String(data).length >= 11 ? String(data).replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4') : data },
                { "targets": 12, "render": function (data, type) { if (type === 'display' && data) { return `<span class="badge rounded-pill ${getStatusBadgeClass(data)}">${data}</span>`; } return data; } },
                { "targets": 14, "render": function (data, type) { 
                    if (type === 'display') {
                        if (data && data !== 'OK' && typeof data === 'string' && data.includes('/')) { 
                            return '<a href="/' + data + '" target="_blank" class="btn btn-sm btn-light border" title="Ver Documento"><i class="fas fa-file-pdf text-danger fa-lg"></i></a>'; 
                        } else if (data === 'OK' || data) { 
                            return '<span class="badge bg-success"><i class="fas fa-check"></i> OK</span>'; 
                        }
                        return '-';
                    }
                    return data || '-';
                } },
                {
                    "targets": 17,
                    "visible": isAdmin,
                    "orderable": false,
                    "searchable": false,
                    "width": "80px",
                    "className": "text-center",
                    "render": function(data, type, row) {
                        const btnEdit = `<button type="button" class="btn btn-sm btn-outline-warning mx-1 js-btn-edit" data-id="${row.id}" title="Editar"><i class="fas fa-pencil-alt"></i></button>`;
                        const btnDel = `<button type="button" class="btn btn-sm btn-outline-danger btn-delete-row" data-id="${row.id}" title="Excluir"><i class="fas fa-trash"></i></button>`;
                        return btnEdit + btnDel;
                    }
                }
            ],
            scrollX: false, paging: true, searching: true, info: true,
            lengthChange: true, pageLength: 25,
            language: {
                emptyTable: "A carregar dados do servidor...", zeroRecords: "Nenhum registo encontrado com o filtro aplicado",
                search: "_INPUT_", searchPlaceholder: "Pesquisa Rápida...",
                paginate: { previous: "Anterior", next: "Próximo" }, info: "Mostrando _START_ a _END_ de _TOTAL_ registos",
                lengthMenu: "Mostrar _MENU_ registos por página"
            }
        });
    }

    // --- INICIALIZAÇÃO IMEDIATA ---
    inicializarTabela();


    // 2. EDIÇÃO (MODAL)
    $('#tabela tbody').on('click', '.js-btn-edit', async function() {
        const row = dataTable.row($(this).parents('tr'));
        const rowData = row.data();

        try {
            const response = await fetchWithAuth(`/api/beneficiarios/${rowData.id}`);
            if (!response.ok) throw new Error('Falha ao buscar dados do beneficiário.');
            const data = await response.json();

            $('#edit-id').val(data.id);
            $('#edit-nome_completo').val(data.nome_completo || data.nome_familiar || '');
            $('#edit-cpf').val(data.cpf || data.cpf_familiar || '');
            $('#edit-sexo').val(data.sexo || '');
            $('#edit-data_nascimento').val(data.data_nascimento || '');
            $('#edit-municipio').val(data.municipio || '');
            $('#edit-comunidade').val(data.comunidade || '');
            $('#edit-nis').val(data.nis || '');
            $('#edit-grh').val(data.grh || '');
            $('#edit-status').val(data.status || '');
            $('#edit-latitude').val(data.latitude || '');
            $('#edit-longitude').val(data.longitude || '');
            
            const infoArquivo = $('#edit-arquivo-existente-info');
            if (data.doc_status && (String(data.doc_status).includes('.pdf') || String(data.doc_status).includes('uploads'))) {
                infoArquivo.html(`Arquivo atual: <a href="/${data.doc_status}" target="_blank">Ver Documento</a>`);
            } else {
                infoArquivo.html('Nenhum documento anexado.');
            }

            modalEdicao.show();
        } catch (error) {
            console.error("Erro ao preparar edição:", error);
            ui.feedbackErro("Não foi possível carregar os dados para edição.");
        }
    });

    // --- Lógica para Salvar o Formulário de Edição (COM DEPURACÃO) ---
    // --- Lógica para Salvar o Formulário de Edição (COM TOASTS) ---
    formEdicao.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = $('#edit-id').val();
        if (!id) return;

        const formData = new FormData(formEdicao);
        const dadosAtualizados = Object.fromEntries(formData.entries());

        try {
            // ETAPA 1: Salvar os dados de TEXTO
            const textResponse = await fetchWithAuth(`/api/beneficiarios/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dadosAtualizados)
            });
            if (!textResponse.ok) throw new Error('Falha ao salvar os dados do beneficiário.');
            let finalUpdatedData = await textResponse.json();

            // ETAPA 2: Se houver um arquivo, fazer o upload
            const fileInput = document.getElementById('edit-arquivo');
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const fileData = new FormData();
                fileData.append('arquivo', file);

                try {
                    const fileResponse = await fetchWithAuth(`/api/beneficiarios/${id}/documento`, {
                        method: 'POST',
                        body: fileData
                        // FormData não precisa de Content-Type manual, o navegador decide o boundary
                    });

                    if (!fileResponse.ok) {
                        const errorDetail = await fileResponse.json().catch(() => ({ detail: 'Erro desconhecido no servidor.' }));
                        throw new Error(errorDetail.detail);
                    }
                    finalUpdatedData = await fileResponse.json();

                } catch (fileError) {
                    console.error("ERRO no upload do ficheiro:", fileError);
                    throw fileError;
                }
            }

            modalEdicao.hide();
            formEdicao.reset();
            fileInput.value = '';
            dataTable.ajax.reload(null, false);
            ui.feedbackSucesso('Beneficiário atualizado com sucesso!');

        } catch (error) {
            console.error("ERRO FINAL CAPTURADO:", error);
            ui.feedbackErro(`Ocorreu um erro: ${error.message}`);
        }
    });

    // --- Lógica para os Filtros Dinâmicos ---
    const searchInput = document.getElementById('searchInput');
    const columnSelect = document.getElementById('columnSelect');
    const clearButton = document.getElementById('clearFilterButton');

    function aplicarFiltroDinamico() {
        if (!dataTable) return;
        const termo = searchInput.value;
        const colunaIdx = parseInt(columnSelect.value, 10);
        dataTable.search('').columns().search('');
        if (colunaIdx === 0) {
            dataTable.search(termo).draw();
        } else {
            dataTable.column(colunaIdx - 1).search(termo).draw();
        }
    }

    if (searchInput) searchInput.addEventListener('keyup', aplicarFiltroDinamico);
    if (columnSelect) columnSelect.addEventListener('change', aplicarFiltroDinamico);
    if (clearButton) {
        clearButton.addEventListener('click', () => {
            if (searchInput) searchInput.value = "";
            if (columnSelect) columnSelect.value = "0";
            if (dataTable) dataTable.search("").columns().search("").draw();
        });
    }
});

    const btnGerarRelatorio = document.getElementById('btnGerarRelatorio');
    if (btnGerarRelatorio) {
        btnGerarRelatorio.addEventListener('click', () => {
            const modalEl = document.getElementById('modalGerarRelatorio');
            if (typeof bootstrap !== 'undefined') {
                const modal = new bootstrap.Modal(modalEl);
                modal.show();
                // Reset UI state
                document.getElementById('resultadoIAContainer').style.display = 'none';
                document.getElementById('textoIA').innerHTML = '';
            }
        });
    }

    const btnExportarKML = document.getElementById('btnExportarKML');
    if (btnExportarKML) {
        btnExportarKML.addEventListener('click', () => {
            // Reset defaults
            $('#filtroMapaMunicipio').val('ABARE');
            $('#filtroMapaStatus').val('IMPORTADO');
            $('#filtroMapaComunidade').val('');

            const modalEl = document.getElementById('modalFiltrosMapa');
            if (typeof bootstrap !== 'undefined' && modalEl) {
                const modal = new bootstrap.Modal(modalEl);
                modal.show();
            } else {
                console.error("Bootstrap ou Modal de Mapa não encontrado");
            }
        });
    }

    // --- Lógica do Novo Gerador de Relatórios ---
    const btnBaixarExcel = document.getElementById('btnBaixarExcel');
    const btnAnalisarIA = document.getElementById('btnAnalisarIA');

    if (btnBaixarExcel) {
        btnBaixarExcel.addEventListener('click', async () => {
            const ids = dataTable.rows({ search: 'applied' }).data().toArray().map(row => row.id);
            const colunas = Array.from(document.querySelectorAll('#formGerarRelatorio .form-check-input:checked')).map(cb => cb.value);

            const payload = { ids, colunas };
            console.log("[DEBUG] Payload Gerar Excel:", payload);

            if (ids.length === 0) {
                ui.feedbackErro("Nenhum dado filtrado para exportar.");
                return;
            }

            btnBaixarExcel.disabled = true;
            btnBaixarExcel.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Gerando...';

            try {
                const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;
                const response = await fetcher('/api/relatorios/excel', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ids, colunas })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: "Erro desconhecido" }));
                    throw new Error(errorData.detail || "Erro ao gerar planilha.");
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Relatorio_Beneficiarios_${new Date().toISOString().slice(0,10)}.xlsx`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                ui.feedbackSucesso("Planilha baixada com sucesso!");
            } catch (error) {
                console.error(error);
                ui.feedbackErro("Falha ao baixar planilha: " + error.message);
            } finally {
                btnBaixarExcel.disabled = false;
                btnBaixarExcel.innerHTML = '<i class="bi bi-download me-2"></i>Baixar Planilha (.xlsx)';
            }
        });
    }

    if (btnAnalisarIA) {
        btnAnalisarIA.addEventListener('click', async () => {
            const ids = dataTable.rows({ search: 'applied' }).data().toArray().map(row => row.id);
            const colunas = Array.from(document.querySelectorAll('#formGerarRelatorio .form-check-input:checked')).map(cb => cb.value);
            const email = document.getElementById('relatorioEmail').value;

            const payload = { ids, colunas, email };
            console.log("[DEBUG] Payload Analisar IA:", payload);

            if (ids.length === 0) {
                ui.feedbackErro("Nenhum dado filtrado para análise.");
                return;
            }

            // UI Feedback
            document.getElementById('resultadoIAContainer').style.display = 'block';
            document.getElementById('loadingIA').style.display = 'block';
            document.getElementById('textoIA').innerHTML = '';
            btnAnalisarIA.disabled = true;

            try {
                const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;
                const response = await fetcher('/api/relatorios/analise', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ids, colunas, email })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: "Erro desconhecido" }));
                    throw new Error(errorData.detail || "Erro na análise IA.");
                }

                const result = await response.json();
                document.getElementById('loadingIA').style.display = 'none';
                
                // Simples conversor de Markdown (Negrito e quebras de linha básicas)
                const text = result.analise || "Sem retorno da IA.";
                const htmlFormatted = text
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\n/g, '<br>');
                
                document.getElementById('textoIA').innerHTML = htmlFormatted;
                ui.feedbackSucesso("Análise concluída!");

                // --- DOWNLOAD AUTOMÁTICO DA ANÁLISE (FORÇADO) ---
                try {
                    const blob = new Blob([text], { type: 'text/markdown' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `analise_ia_agendha.md`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } catch (e) {
                    console.error("Erro ao baixar arquivo da IA:", e);
                }
            } catch (error) {
                console.error(error);
                ui.feedbackErro("Falha na análise IA: " + error.message);
                document.getElementById('resultadoIAContainer').style.display = 'none';
            } finally {
                btnAnalisarIA.disabled = false;
            }
        });
    }

    // Mantendo Sincronização com Mapa (OPCIONAL: Agora acessível apenas via código ou se o usuário adicionar outro botão)
    // No beneficiarios.html original ele era o btnExportarKML. 
    // Como trocamos o ID, essa função window.enviarParaMapa ainda existe mas o disparador mudou.

// --- FUNÇÃO GLOBAL PARA GERAR KML ---
// --- FUNÇÃO GLOBAL PARA SINCRONIZAR COM MAPA ---
// --- FUNÇÃO GLOBAL PARA SINCRONIZAR COM MAPA ---
/**
 * @descrição Sincroniza os beneficiários filtrados atualmete com o Mapa de Projetos.
 * @parâmetros Nenhum (Lê os valores dos inputs do Modal #modalFiltrosMapa).
 * @comportamento 
 *  1. Valida se Município e Status foram selecionados.
 *  2. Ativa estado de "Carregando" no botão.
 *  3. Envia requisição POST para /api/mapa/sincronizar-beneficiarios.
 *  4. Exibe alerta com resultado (Novos inseridos vs Duplicados).
 *  5. Redireciona para o Mapa Geral em caso de sucesso.
 */
window.enviarParaMapa = async function () {
    const municipio = $('#filtroMapaMunicipio').val();
    const status = $('#filtroMapaStatus').val();
    const comunidade = $('#filtroMapaComunidade').val();
    const btn = document.getElementById('btnEnviarMapa');

    // Basic Validation
    if (!municipio || !status) {
        ui.feedbackErro("Selecione Município e Status.");
        return;
    }

    // Loading State
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sincronizando...';

    try {
        // Call Backend
        // Using global fetchWithAuth if available, else fetch
        const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;

        const response = await fetcher('/api/mapa/sincronizar-beneficiarios', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                municipio: municipio,
                status: status,
                comunidade: comunidade
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || result.message || "Erro desconhecido ao sincronizar.");
        }

        // Success Feedback
        if (result.synced > 0) {
            ui.feedbackSucesso(`Sucesso! ${result.synced} novos pontos adicionados ao mapa.`);
        } else if (result.duplicates_skipped > 0) {
            ui.feedbackSucesso(`Sincronização concluída. Nenhum novo ponto (todos os ${result.duplicates_skipped} já existiam).`);
        } else {
            ui.feedbackErro("Nenhum beneficiário encontrado com estes filtros.");
        }

        // Redirect to Map
        window.location.href = '/api/mapa/geral';

    } catch (error) {
        console.error("Erro Sync:", error);
        ui.feedbackErro(`Falha na sincronização: ${error.message}`);
        // Restore Button
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
};

// --- Lógica do Scanner GRH (Adicionado via Debugger) ---
document.addEventListener("DOMContentLoaded", () => {
    const btnScanGRH = document.getElementById('btnScanGRH');
    const inputScanGRH = document.getElementById('inputScanGRH');
    const modalScanGRH_El = document.getElementById('modalScanGRH');

    if (btnScanGRH && inputScanGRH && modalScanGRH_El) {
        let modalScanGRH;
        if (typeof bootstrap !== 'undefined') {
            modalScanGRH = new bootstrap.Modal(modalScanGRH_El);
        }
        const iframePreview = document.getElementById('iframePreviewGRH');
        const placeholder = document.getElementById('preview-placeholder-grh');
        const tbody = document.getElementById('tbody-scan-grh');

        // Helper de Debounce para validação
        function debounce(func, wait) {
            let timeout;
            return function (...args) {
                const context = this;
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(context, args), wait);
            };
        }

        // Listener de Validação em Tempo Real (Delegado)
        if (tbody) {
            tbody.addEventListener('input', debounce(async (e) => {
                const target = e.target;
                if (!target.classList.contains('js-live-validation')) return;

                const tr = target.closest('tr');
                if (!tr) return;

                const inputNome = tr.querySelector('.js-input-nome');
                const inputCpf = tr.querySelector('.js-input-cpf');
                const badgeCell = tr.cells[2]; // Ajuste conforme índice
                const actionCell = tr.cells[3];

                const nome = inputNome ? inputNome.value.trim() : "";
                const cpf = inputCpf ? inputCpf.value.trim() : "";

                // Feedback visual de "buscando"
                badgeCell.innerHTML = '<span class="spinner-border spinner-border-sm text-secondary"></span>';

                try {
                    const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;
                    const response = await fetcher('/api/grh/match-manual', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ nome, cpf })
                    });

                    const resultado = await response.json();

                    if (response.ok && resultado.encontrado) {
                        // MATCH ENCONTRADO
                        tr.dataset.idBeneficiario = resultado.id;
                        badgeCell.innerHTML = '<span class="badge bg-success">Encontrado</span>';
                        actionCell.innerHTML = `<button class="btn btn-sm btn-outline-secondary" disabled>Vinculado</button>`;

                        // Atualiza inputs com dados oficiais (opcional, pode ser irritante pro usuário se mudar o que ele digita)
                        // Vamos manter o que o usuário digitou, mas talvez mostrar tooltip?
                        // Por enquanto, apenas atualiza o estado.
                        tr.classList.add('table-success'); // Highlight row
                        setTimeout(() => tr.classList.remove('table-success'), 1000);

                    } else {
                        // NÃO ENCONTRADO
                        delete tr.dataset.idBeneficiario;
                        badgeCell.innerHTML = '<span class="badge bg-secondary">Novo</span>';
                        actionCell.innerHTML = `<a href="/processar?nome=${encodeURIComponent(nome)}&cpf=${encodeURIComponent(cpf)}" class="btn btn-sm btn-primary">Cadastrar</a>`;
                    }

                } catch (err) {
                    console.error("Erro na validação em tempo real:", err);
                    badgeCell.innerHTML = '<span class="badge bg-danger">Erro</span>';
                }

            }, 500)); // 500ms delay
        }

        btnScanGRH.addEventListener('click', (e) => {
            e.preventDefault();
            inputScanGRH.value = ''; // Reset para permitir re-seleção do mesmo arquivo
            inputScanGRH.click();
        });

        inputScanGRH.addEventListener('change', async (e) => {
            if (!e.target.files || e.target.files.length === 0) return;
            const file = e.target.files[0];

            // Reset e Exibe Modal
            if (iframePreview) {
                iframePreview.src = "";
                iframePreview.style.display = 'none';
            }
            if (placeholder) placeholder.style.display = 'block';
            if (tbody) tbody.innerHTML = '<tr><td colspan="4" class="text-center py-4"><span class="spinner-border text-primary spinner-border-sm me-2"></span>✨ Gemini analisando documento...</td></tr>';

            modalScanGRH.show();

            // Preview Local
            const objectUrl = URL.createObjectURL(file);
            if (iframePreview) {
                iframePreview.src = objectUrl;
                iframePreview.onload = () => {
                    if (placeholder) placeholder.style.display = 'none';
                    iframePreview.style.display = 'block';
                };
            }

            // Envio para API
            const formData = new FormData();
            formData.append('file', file); // Alterado de 'arquivo' para 'file' para bater com o backend

            try {
                // Tenta usar global fetchWithAuth, fallback para fetch normal
                const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;

                const response = await fetcher('/api/grh/scan-lista', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    console.error("Scan Error Details:", await response.json().catch(() => "Sem detalhes JSON"));
                    ui.feedbackErro("Erro na análise: Verifique o console para detalhes técnicos.");
                }

                const data = await response.json();
                renderScanResults(data.beneficiarios_detectados || [], tbody);
            } catch (err) {
                console.error("Scan Error:", err);
                if (tbody) tbody.innerHTML = `<tr><td colspan="4" class="text-center text-danger py-3">Erro na análise: ${err.message}</td></tr>`;
            }
        });

        const btnSalvarGRH = document.getElementById('btnSalvarGRH');
        if (btnSalvarGRH) {
            btnSalvarGRH.addEventListener('click', async () => {
                const termo = document.getElementById('inputTextoGRH').value.trim();
                if (!termo) {
                    ui.feedbackErro("Por favor, digite o texto de referência do GRH (ex: GRH 05/2024).");
                    return;
                }

                // Coletar IDs validados (Encontrados/Vinculados)
                // Percorre as linhas da tabela em busca dos datasets
                const rows = tbody.querySelectorAll('tr');
                const idsParaVincular = [];

                rows.forEach(row => {
                    const idBeneficiario = row.dataset.idBeneficiario;
                    if (idBeneficiario) {
                        idsParaVincular.push(parseInt(idBeneficiario));
                    }
                });

                if (idsParaVincular.length === 0) {
                    ui.feedbackErro("Nenhum beneficiário 'Encontrado' na lista para vincular.");
                    return;
                }

                try {
                    const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;
                    const resp = await fetcher('/api/grh/vincular', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            termo_grh: termo,
                            ids_beneficiarios: idsParaVincular
                        })
                    });

                    if (!resp.ok) {
                        throw new Error("Erro ao salvar vínculos.");
                    }

                    const result = await resp.json();
                    ui.feedbackSucesso(`Sucesso! ${result.afetados} beneficiários foram atualizados.`);
                    modalScanGRH.hide();

                    // Atualiza a tabela principal
                    if (typeof dataTable !== 'undefined') {
                        dataTable.ajax.reload(null, false);
                    } else {
                        window.location.reload();
                    }

                } catch (e) {
                    console.error(e);
                    ui.feedbackErro("Erro ao gravar GRH: " + e.message);
                }
            });
        }
    }

    function renderScanResults(lista, tbody) {
        if (!tbody) return;
        tbody.innerHTML = '';
        if (lista.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center py-3">Nenhum nome identificado.</td></tr>';
            return;
        }

        lista.forEach((item, idx) => {
            const tr = document.createElement('tr');
            renderRowContent(tr, item, idx);
            tbody.appendChild(tr);
        });

        // Event Delegation para botões (Busca Manual e Exclusão)
        tbody.addEventListener('click', async (e) => {
            // --- Ação: Remover Linha ---
            const btnRemove = e.target.closest('.js-btn-remove-row');
            if (btnRemove) {
                const tr = btnRemove.closest('tr');
                if (tr) tr.remove();
                return;
            }

            // --- Ação: Busca Manual ---
            const btn = e.target.closest('.js-btn-manual-search');
            if (!btn) return;

            const tr = btn.closest('tr');
            const inputNome = tr.querySelector('.js-input-nome');
            const inputCpf = tr.querySelector('.js-input-cpf');

            const nomeDigitado = inputNome.value.trim();
            const cpfDigitado = inputCpf.value.trim();

            if (!nomeDigitado && !cpfDigitado) {
                ui.feedbackErro("Digite um nome ou CPF para buscar.");
                return;
            }

            // UI Feedback
            const originalIcon = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            btn.disabled = true;

            try {
                const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;
                const response = await fetcher('/api/grh/match-manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        nome: nomeDigitado,
                        cpf: cpfDigitado
                    })
                });

                const resultado = await response.json();

                if (response.ok && resultado.encontrado) {
                    // Atualiza o item localmente com os dados do match
                    const novoItem = {
                        encontrado: true,
                        id_beneficiario: resultado.id,
                        nome_extraido: resultado.nome,
                        cpf_extraido: resultado.cpf,
                        match_type: 'MANUAL'
                    };

                    // Re-renderiza a linha
                    const idx = Array.from(tbody.children).indexOf(tr);
                    renderRowContent(tr, novoItem, idx);

                    // Feedback Visual Extra
                    tr.classList.add('table-success');
                    setTimeout(() => tr.classList.remove('table-success'), 1000);

                } else {
                    ui.feedbackErro(resultado.mensagem || "Beneficiário não encontrado.");
                }

            } catch (error) {
                console.error("Erro na busca manual:", error);
                ui.feedbackErro("Erro ao buscar beneficiário. Veja o console.");
            } finally {
                btn.innerHTML = originalIcon;
                btn.disabled = false;
            }
        });

        // --- Lógica do Botão Gravar (Com Modal Clone) ---
        const btnSalvarGRH = document.getElementById('btnSalvarGRH');
        // Inicializa o modal de sucesso se ele existir no DOM
        const modalSucessoEl = document.getElementById('modalSucessoGRH');
        let modalSucessoGRH = null;
        if (modalSucessoEl && typeof bootstrap !== 'undefined') {
            modalSucessoGRH = new bootstrap.Modal(modalSucessoEl);
        }
        const msgSucessoGRH = document.getElementById('modalSucessoMsgGRH'); // ID Corrigido

        if (btnSalvarGRH) {
            // Remove listeners antigos
            const newBtn = btnSalvarGRH.cloneNode(true);
            btnSalvarGRH.parentNode.replaceChild(newBtn, btnSalvarGRH);

            newBtn.addEventListener('click', async () => {
                const termo = document.getElementById('inputTextoGRH').value.trim();
                if (!termo) {
                    ui.feedbackErro("Por favor, digite o texto de referência do GRH (ex: GRH 05/2024).");
                    return;
                }

                // Coletar IDs validados
                const rows = tbody.querySelectorAll('tr');
                const idsParaVincular = [];

                rows.forEach(row => {
                    const idBeneficiario = row.dataset.idBeneficiario;
                    if (idBeneficiario) {
                        idsParaVincular.push(parseInt(idBeneficiario));
                    }
                });

                if (idsParaVincular.length === 0) {
                    ui.feedbackErro("Nenhum beneficiário 'Encontrado' na lista para vincular.");
                    return;
                }

                try {
                    const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;
                    const resp = await fetcher('/api/grh/vincular', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            termo_grh: termo,
                            ids_beneficiarios: idsParaVincular
                        })
                    });

                    if (!resp.ok) {
                        throw new Error("Erro ao salvar vínculos.");
                    }

                    const result = await resp.json();

                    // Fecha modal do Scanner
                    if (modalScanGRH_El && typeof bootstrap !== 'undefined') {
                        const modalScan = bootstrap.Modal.getInstance(modalScanGRH_El);
                        if (modalScan) modalScan.hide();
                    }

                    ui.feedbackSucesso(`Sucesso! ${result.afetados} beneficiários foram atualizados com o GRH '${termo}'.`);

                    // Atualiza a tabela principal
                    if (typeof dataTable !== 'undefined') {
                        dataTable.ajax.reload(null, false);
                    } else {
                        window.location.reload();
                    }

                } catch (e) {
                    console.error(e);
                    ui.feedbackErro("Erro ao gravar GRH: " + e.message);
                }
            });
        }
    }

    function renderRowContent(tr, item, idx) {
        console.log("Inputs GRH Carregados para linha " + idx); // DEBUG LOG

        const encontrado = item.encontrado;

        if (encontrado && item.id_beneficiario) {
            tr.dataset.idBeneficiario = item.id_beneficiario;
        } else {
            delete tr.dataset.idBeneficiario;
        }

        const badge = encontrado
            ? '<span class="badge bg-success">Encontrado</span>'
            : '<span class="badge bg-secondary">Novo</span>';

        const acao = encontrado
            ? `<button class="btn btn-sm btn-outline-secondary" disabled>Vinculado</button>`
            : `<a href="/processar?nome=${encodeURIComponent(item.nome_extraido || '')}&cpf=${encodeURIComponent(item.cpf_extraido || '')}" class="btn btn-sm btn-primary">Cadastrar</a>`;

        // Botão de Excluir (Lixeira)
        const btnDelete = `
            <button class="btn btn-sm btn-outline-danger js-btn-remove-row border-0" title="Remover da lista">
                <i class="bi bi-trash"></i>
            </button>
        `;

        // FORÇANDO INPUTS DIRETOS
        tr.innerHTML = `
            <td>${idx + 1}</td>
            <td>
                <div class="mb-1">
                    <input type="text" class="form-control form-control-sm edit-nome js-input-nome fw-bold" 
                           value="${item.nome_extraido || ''}" 
                           placeholder="Nome"
                           style="border: none; background: transparent; width: 100%; box-shadow: none;"
                           autocomplete="off">
                </div>
                <div>
                     <input type="text" class="form-control form-control-sm edit-nome js-input-cpf font-monospace small text-muted" 
                           value="${item.cpf_extraido || ''}" 
                           placeholder="CPF"
                           style="border: none; background: transparent; width: 100%; box-shadow: none;"
                           autocomplete="off">
                </div>
            </td>
            <td>${badge}</td>
            <td class="text-end">${acao}</td>
            <td class="text-center">${btnDelete}</td>
        `;
    }
});

// --- Importação CSV (Comparator) ---
// --- Global State for Import Curation ---
// Removed local let declarations to ensure accessibility by selectTriagemItem
let currentFilterMode = 'all'; // all, novos, dups

function applyTriagemFilter() {
    const term = (document.getElementById('input-triagem-filter').value || '').toLowerCase();

    // Check Radio Buttons
    if (document.getElementById('filter-novos').checked) currentFilterMode = 'novos';
    else if (document.getElementById('filter-dups').checked) currentFilterMode = 'dups';
    else currentFilterMode = 'all';

    const filtered = currentTriagemData.filter(item => {
        // Name/CPF Search
        const matchesTerm = (item.nome && item.nome.toLowerCase().includes(term)) ||
            (item.cpf && item.cpf.includes(term));

        let matchesMode = true;
        if (currentFilterMode === 'novos') matchesMode = item.status_triagem === 'NOVO';
        if (currentFilterMode === 'dups') matchesMode = item.status_triagem === 'DUPLICADO';

        return matchesTerm && matchesMode;
    });

    renderTriagemList(filtered);
}

// --- Importação CSV (Comparator / Triagem) ---
document.addEventListener("DOMContentLoaded", () => {
    // Filter Listeners
    const inputFilter = document.getElementById('input-triagem-filter');
    if (inputFilter) {
        inputFilter.addEventListener('input', applyTriagemFilter);
        document.querySelectorAll('input[name="btnfilter"]').forEach(radio => {
            radio.addEventListener('change', applyTriagemFilter);
        });
    }

    // Input Validation & Auto-Save Listeners
    ['input-triagem-nome', 'input-triagem-cpf', 'input-triagem-status', 'input-triagem-nis',
        'input-triagem-comunidade', 'input-triagem-lat', 'input-triagem-lon'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', (e) => {
                    // Visual Validation for key fields
                    if (id.includes('nome') || id.includes('cpf')) {
                        if (!e.target.value.trim()) e.target.classList.add('is-invalid');
                        else e.target.classList.remove('is-invalid');
                    }

                    // Auto-Save to Temporary Data Model
                    if (currentSelectedIndex > -1 && currentTriagemData[currentSelectedIndex]) {
                        const item = currentTriagemData[currentSelectedIndex];
                        const val = e.target.value;

                        if (id.includes('nome')) item.nome = val;
                        if (id.includes('cpf')) item.cpf = val;
                        if (id.includes('status')) item.status = val;
                        if (id.includes('nis')) item.nis = val;
                        if (id.includes('comunidade')) item.comunidade = val;
                        if (id.includes('lat')) item.latitude = val;
                        if (id.includes('lon')) item.longitude = val;

                        // Re-render list item name if changed
                        if (id.includes('nome')) updateListItemName(currentSelectedIndex, val);
                    }
                });
            }
        });

    const inputImportCsv = document.getElementById('inputImportCsv');
    if (inputImportCsv) {
        inputImportCsv.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // Visual Feedback
            const btn = document.getElementById('btnImportarCsv');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> ✨ Gemini analisando...';
            btn.disabled = true;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;
                const response = await fetcher('/api/beneficiarios/import/comparar', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error("Falha na análise do CSV.");

                const data = await response.json();

                // 1. Store Data
                currentTriagemData = data.lista_triagem || [];

                // 2. Update Stats
                document.getElementById('triagem-total').textContent = data.resumo.total;
                document.getElementById('triagem-total-csv').textContent = data.resumo.total; // Total from CSV

                // 3. Render List
                applyTriagemFilter(); // Initial render with filters

                // 4. Show Modal
                new bootstrap.Modal(document.getElementById('modalImportCompare')).show();

                // Reset Selection
                selectTriagemItem(-1);

            } catch (err) {
                console.error(err);
                ui.feedbackErro("Erro ao processar arquivo: " + err.message);
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
                inputImportCsv.value = ''; // Reset input
            }
        });
    }

    // --- Toolbar Listeners ---
    // Listeners removidos: a lógica agora reside apenas nos onlick do HTML (window.confirmarImportacaoUnica / window.removerItemTriagem)
    // para evitar dupla execução e alertas nativos.


    // (Bloco btnRemoveSingle.addEventListener removido - substituído por window.removerItemTriagem)

    // --- Confirm Import Button Listener (Bulk) ---
    const btnConfirm = document.getElementById('btnConfirmarImportacao');
    if (btnConfirm) {
        btnConfirm.addEventListener('click', async () => {
            // Filter out already imported
            const itemsToImport = currentTriagemData.filter(i => !i.is_imported);

            if (itemsToImport.length === 0) {
                ui.feedbackErro("Todos os itens já foram importados ou não há dados.");
                return;
            }

            ui.confirmarGeneric(
                async () => {
                    // Loading State
                    const originalText = btnConfirm.innerHTML;
                    btnConfirm.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Salvando...';
                    btnConfirm.disabled = true;

                    try {
                        const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;
                        const response = await fetcher('/api/beneficiarios/import/confirmar', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(itemsToImport)
                        });

                        if (!response.ok) throw new Error("Erro ao salvar importação.");

                        const result = await response.json();

                        ui.feedbackSucesso(`Importação em Massa Concluída! Novos: ${result.novos}, Atualizados: ${result.atualizados}`);
                        setTimeout(() => window.location.reload(), 2000);

                    } catch (err) {
                        console.error(err);
                        ui.feedbackErro("Erro na importação: " + err.message);
                        btnConfirm.innerHTML = originalText;
                        btnConfirm.disabled = false;
                    }
                },
                "Confirmar Importação em Massa",
                `Confirma a importação dos <strong>${itemsToImport.length}</strong> registros restantes?`
            );
        });
    }
});

// Helper to filter data (extracted from applyTriagemFilter for reuse if needed, but applyTriagemFilter updates state directly)
function filterData() {
    const term = (document.getElementById('input-triagem-filter').value || '').toLowerCase();
    return currentTriagemData.filter(item => {
        const matchesTerm = (item.nome && item.nome.toLowerCase().includes(term)) ||
            (item.cpf && item.cpf.includes(term));
        let matchesMode = true;
        if (currentFilterMode === 'novos') matchesMode = item.status_triagem === 'NOVO';
        if (currentFilterMode === 'dups') matchesMode = item.status_triagem === 'DUPLICADO';
        return matchesTerm && matchesMode;
    });
}

function renderTriagemList(list) {
    const container = document.getElementById('triagem-list');
    const totalEl = document.getElementById('triagem-total');
    const totalCsvEl = document.getElementById('triagem-total-csv');

    if (!container) return; // Safety check

    container.innerHTML = '';

    if (!list || list.length === 0) {
        container.innerHTML = '<div class="p-3 text-center text-muted small">Nenhum item correspondente.</div>';
        // Reset totals if empty
        if (totalEl) totalEl.textContent = '0';
        if (totalCsvEl) totalCsvEl.textContent = '0';
        return;
    }

    let csvCount = 0;

    list.forEach((item, index) => {
        if (item.is_imported) csvCount++;

        // Ensure index is set (though list order might be filtered, we need original index if we want to sync with currentTriagemData?)
        // Actually, renderTriagemList receives the filtered list or the full list? 
        // Based on original code, it seems to just render what is passed. 
        // BUT, selectTriagemItem relies on `dataset.index`. 
        // If we pass a filtered list, the index might not match `currentTriagemData` if `list` is a subset.
        // However, the previous logic in `renderTriagemList` didn't seem to account for mapping back to original `currentTriagemData` index 
        // if `list` was filtered. Wait, usually `currentTriagemData` IS the list being rendered?
        // Let's assume `list` items correspond to `currentTriagemData` or have ID we can lookup.
        // `selectTriagemItem` uses `parseInt(elemento.dataset.index)`.
        // If `list` is filtered, `index` here is 0, 1, 2... but in `currentTriagemData` it might be 5, 8, 12.
        // We should probably rely on `item.id_temp` to find the item in `currentTriagemData` in `selectTriagemItem`.
        // BUT, for now let's keep `dataset.index` as `index` and assume `list` is the view.
        // Actually the `renderTriagemList` function implementation I saw earlier used `list.forEach((item) => ...`. 
        // It didn't seem to pass index usefully if it was filtered. 
        // Let's stick to the styling changes requested.

        let statusColor = 'text-secondary';
        let statusIcon = 'bi-circle';
        let opacityClass = '';

        if (item.is_imported) {
            statusColor = 'text-primary';
            statusIcon = 'bi-check-circle-fill';
            opacityClass = 'opacity-50 bg-light'; // Dim imported items
        } else if (item.status_triagem === 'NOVO') {
            statusColor = 'text-success';
            statusIcon = 'bi-plus-circle-fill';
        } else if (item.status_triagem === 'DUPLICADO') {
            statusColor = 'text-warning';
            statusIcon = 'bi-exclamation-triangle-fill';
        } else if (item.status_triagem === 'INVALIDO' || item.status_triagem === 'ATENCAO') {
            statusColor = 'text-danger';
            statusIcon = 'bi-x-circle-fill';
        }

        const el = document.createElement('a');
        el.href = '#';
        // NEW STYLE: Border start color instead of full border. Cleaner look.
        let borderClass = '';
        if (item.is_imported) borderClass = 'border-primary';
        else if (item.status_triagem === 'NOVO') borderClass = 'border-success';
        else if (item.status_triagem === 'DUPLICADO') borderClass = 'border-warning';
        else borderClass = 'border-danger';

        el.className = `list-group-item list-group-item-action d-flex align-items-center justify-content-between py-3 px-3 border-0 border-bottom border-start border-4 ${borderClass} triagem-item ${opacityClass}`;
        el.dataset.id = item.id_temp;
        // Search for the real index in the main data array to ensure compatibility
        const realIndex = currentTriagemData.findIndex(d => d.id_temp === item.id_temp);
        el.dataset.index = realIndex !== -1 ? realIndex : 0;

        let diffIndicator = '';
        if (item.diffs && item.diffs.length > 0 && !item.is_imported) {
            diffIndicator = '<i class="bi bi-exclamation-octagon-fill text-danger me-2" title="Diferenças encontradas"></i>';
        }

        // Compact Content
        el.innerHTML = `
            <div class="text-truncate me-2" style="max-width: 85%;">
                <h6 class="fw-bold text-dark text-truncate mb-0" id="lbl-name-${item.id_temp}">${item.nome || 'Sem Nome'}</h6>
                <small class="text-muted" style="font-size: 0.75rem;">CPF: ${item.cpf || 'N/A'}</small>
            </div>
            <div class="d-flex align-items-center gap-1">
                ${diffIndicator}
                <i class="bi ${statusIcon} ${statusColor} fs-5"></i>
            </div>
        `;

        el.onclick = (e) => {
            e.preventDefault();
            selectTriagemItem(el); // Pass the element itself
        };

        container.appendChild(el);
    });

    if (totalEl) totalEl.textContent = list.length;
    if (totalCsvEl) totalCsvEl.textContent = csvCount;
}

function selectTriagemItem(elemento) {
    // --- Hoisted Variable Declarations (GLOBAL SCOPE of Function) ---
    const formContainer = document.getElementById('triagem-detail-container');
    const emptyState = document.getElementById('triagem-empty-state');
    const badgeContainer = document.getElementById('triagem-badge-container');
    const diffContainer = document.getElementById('alert-diffs-container');
    const diffList = document.getElementById('list-diffs');
    const infoBanco = document.getElementById('info-triagem-banco');
    const toolbar = document.getElementById('triagem-toolbar');
    const btnSave = document.getElementById('btn-triagem-save-single');
    const btnRemove = document.getElementById('btn-triagem-remove');
    const btnSaveHeader = document.getElementById('btn-triagem-save-single'); // Redundant check in original, mapped to same

    // Clear previous highlights
    document.querySelectorAll('.triagem-item').forEach(el => {
        el.classList.remove('active', 'active-item', 'bg-light');
        const title = el.querySelector('h6');
        if (title) title.classList.remove('text-primary');
    });

    // --- CASE 1: Deselection or Invalid ---
    if (elemento === -1 || !elemento) {
        currentSelectedIndex = -1;

        if (formContainer) {
            formContainer.style.display = 'none';
            formContainer.classList.add('d-none');
        }
        if (emptyState) emptyState.style.display = 'flex';
        if (diffContainer) diffContainer.style.display = 'none';
        if (toolbar) toolbar.style.display = 'none';

        if (btnSave) btnSave.disabled = true;
        if (btnRemove) btnRemove.disabled = true;

        return;
    }

    // --- CASE 2: Index Passed (Recursion) ---
    if (typeof elemento === 'number') {
        const actualIndex = elemento;
        const item = currentTriagemData[actualIndex];
        if (item) {
            const el = document.querySelector(`.triagem-item[data-id="${item.id_temp}"]`);
            if (el) {
                selectTriagemItem(el); // Recurse with the actual element
                return;
            }
        }
        selectTriagemItem(-1);
        return;
    }

    // --- CASE 3: Valid Element Selection ---

    // Activate new selection
    elemento.classList.add('active-item', 'bg-light');
    const title = elemento.querySelector('h6');
    if (title) title.classList.add('text-primary');

    currentSelectedIndex = parseInt(elemento.dataset.index);
    const item = currentTriagemData[currentSelectedIndex];

    if (!item) {
        selectTriagemItem(-1);
        return;
    }

    // FIX: Robust check for container presence
    if (!formContainer) {
        console.warn("Detail container not found!");
        return;
    }

    // UI State Logic
    if (emptyState) emptyState.style.display = 'none';
    if (toolbar) toolbar.style.display = 'block';

    // Force Visibility
    formContainer.style.setProperty('display', 'block', 'important');
    if (formContainer.parentElement) formContainer.parentElement.style.display = 'block';
    formContainer.classList.remove('d-none');

    // Helper safely set value
    const setVal = (id, val) => {
        const input = document.getElementById(id);
        if (input) input.value = val || '';
    };

    // Grab Inputs (filtered)
    const inputs = [
        document.getElementById('input-triagem-nome'),
        document.getElementById('input-triagem-cpf'),
        document.getElementById('input-triagem-nis'),
        document.getElementById('input-triagem-comunidade'),
        document.getElementById('input-triagem-lat'),
        document.getElementById('input-triagem-lon'),
        document.getElementById('input-triagem-status')
    ].filter(el => el !== null);

    // Populate Fields
    setVal('input-triagem-nome', item.nome);
    setVal('input-triagem-cpf', item.cpf);
    setVal('input-triagem-nis', item.nis);
    setVal('input-triagem-comunidade', item.comunidade);
    setVal('input-triagem-lat', item.latitude);
    setVal('input-triagem-lon', item.longitude);
    setVal('input-triagem-status', item.status || 'EM CADASTRO');

    // Import State Logic
    const isImported = !!item.is_imported;
    inputs.forEach(inp => inp.disabled = isImported);

    if (btnSave) btnSave.disabled = isImported;
    if (btnRemove) btnRemove.disabled = isImported;

    // Badge Logic
    let badgeHtml = '';
    if (isImported) badgeHtml = '<span class="badge bg-primary fs-6"><i class="bi bi-check-circle-fill me-1"></i>Importação Concluída</span>';
    else if (item.status_triagem === 'NOVO') badgeHtml = '<span class="badge bg-success fs-6"><i class="bi bi-check-circle me-1"></i>Novo</span>';
    else if (item.status_triagem === 'DUPLICADO') {
        if (item.diffs && item.diffs.length > 0) badgeHtml = '<span class="badge bg-info text-dark fs-6"><i class="bi bi-info-circle me-1"></i>Atualiza</span>';
        else badgeHtml = '<span class="badge bg-warning text-dark fs-6"><i class="bi bi-exclamation-triangle me-1"></i>Duplicado</span>';
    }
    else badgeHtml = `<span class="badge bg-danger fs-6"><i class="bi bi-x-circle me-1"></i>${item.status_triagem}</span>`;

    if (badgeContainer) badgeContainer.innerHTML = badgeHtml;

    // Visual Validation (Class only)
    const inpNome = document.getElementById('input-triagem-nome');
    const inpCpf = document.getElementById('input-triagem-cpf');
    if (inpNome) inpNome.classList.toggle('is-invalid', !item.nome && !isImported);
    if (inpCpf) inpCpf.classList.toggle('is-invalid', !item.cpf && !isImported);

    // Banco Info
    if (item.dados_banco && infoBanco) {
        infoBanco.style.display = 'flex';
        const infoText = document.getElementById('text-triagem-banco-info');
        if (infoText) {
            infoText.innerHTML = `
                Nome: ${item.dados_banco.nome_completo}<br>
                Status: <strong>${item.dados_banco.status}</strong>
            `;
        }
    } else if (infoBanco) {
        infoBanco.style.display = 'none';
    }

    // Diff Logic
    if (diffContainer && diffList) {
        if (item.diffs && item.diffs.length > 0 && !isImported) {
            diffContainer.style.display = 'block';
            diffList.innerHTML = item.diffs.map(d => `<li><strong>${d.campo}:</strong> CSV [${d.novo}] vs Banco [${d.antigo || 'Vazio'}]</li>`).join('');
        } else {
            diffContainer.style.display = 'none';
        }
    }
}

function updateListItemName(index, newName) {
    const item = currentTriagemData[index];
    if (item) {
        const lbl = document.getElementById(`lbl-name-${item.id_temp}`);
        if (lbl) lbl.textContent = newName || 'Sem Nome';
    }
}

// =========================================================================
//              MODAL SYSTEM & GLOBAL ACTIONS (Force Injection)
// =========================================================================

// State for callbacks
let confirmCallback = null;
let successCallback = null;

/**
 * Exibe o Modal de Confirmação Genérico (Azul/Vermelho)
 * @param {string} title - Título do Modal
 * @param {string} message - Mensagem do Corpo
 * @param {string} variant - 'primary' (Azul) ou 'danger' (Vermelho)
 * @param {function} callback - Função a ser executada no "Sim"
 */


// Interaction Binding (One-time or Re-bound)



// --- GLOBAL ACTIONS (Linked to HTML OnClick) ---

/**
 * Ação: Importar Individualmente
 * - Valida
 * - Abre Modal Azul
 * - Envia POST
 * - Abre Modal Sucesso
 */
/**
 * @descrição Ação de Importação Individual (Triagem).
 * @parâmetros Nenhum (Usa índice global 'currentSelectedIndex' e inputs do DOM).
 * @comportamento
 *  1. Coleta dados do formulário de triagem.
 *  2. Valida campos obrigatórios (Nome, CPF).
 *  3. Exibe Modal de Confirmação (Azul).
 *  4. Se confirmado, envia POST para /api/beneficiarios/import/confirmar.
 *  5. Marca item como importado na lista local e atualiza UI.
 */
window.confirmarImportacaoUnica = async function () {
    if (currentSelectedIndex === -1 || !currentTriagemData[currentSelectedIndex]) return;
    const item = currentTriagemData[currentSelectedIndex];

    // Harvest Data
    item.nome = document.getElementById('input-triagem-nome').value;
    item.cpf = document.getElementById('input-triagem-cpf').value;
    item.nis = document.getElementById('input-triagem-nis').value;
    item.comunidade = document.getElementById('input-triagem-comunidade').value;
    item.latitude = document.getElementById('input-triagem-lat').value;
    item.longitude = document.getElementById('input-triagem-lon').value;
    item.status = document.getElementById('input-triagem-status').value;

    if (!item.nome || !item.cpf) {
        if (typeof ui !== 'undefined' && ui.feedbackErro) ui.feedbackErro("Nome e CPF são obrigatórios.");
        else alert("Nome e CPF são obrigatórios.");
        return;
    }

    ui.confirmarGeneric(
        async () => {
            // Execution Block
            const btn = document.getElementById('btn-triagem-save-single');
            const originalContent = btn ? btn.innerHTML : '';
            if (btn) {
                btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Salvando...';
                btn.disabled = true;
            }

            try {
                const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;
                const response = await fetcher('/api/beneficiarios/import/confirmar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(item)
                });

                if (!response.ok) throw new Error("Erro ao salvar.");

                // Success Logic
                item.is_imported = true;
                item.status_triagem = 'IMPORTADO';

                applyTriagemFilter();
                selectTriagemItem(currentSelectedIndex);
                ui.feedbackSucesso(`Importação de ${item.nome} confirmada.`);

                // Refresh main table background
                if (typeof dataTable !== 'undefined') {
                    dataTable.ajax.reload(null, false);
                }

            } catch (err) {
                console.error(err);
                ui.feedbackErro("Erro: " + err.message);
            } finally {
                if (btn) {
                    btn.innerHTML = originalContent;
                    if (!item.is_imported) btn.disabled = false;
                }
            }
        },
        "Confirmar Importação",
        `Deseja realmente importar <strong>${item.nome}</strong>?`
    );
};

/**
 * Ação: Remover Item
 * - Abre Modal Vermelho
 * - Remove do Array
 * - Abre Modal Sucesso
 */
window.removerItemTriagem = function () {
    if (currentSelectedIndex === -1) return;

    ui.confirmarGeneric(
        async () => {
            currentTriagemData.splice(currentSelectedIndex, 1);
            selectTriagemItem(-1);
            applyTriagemFilter();
            ui.feedbackSucesso("Item removido da triagem.");
        },
        "Excluir Item",
        "Tem certeza que deseja remover este item da lista de importação?",
        "Sim, Remover"
    );
};

// --- DELEGAÇÃO GLOBAL DE EVENTOS (REFATORADO) ---
$(document).on('click', '.btn-delete-row', function(e) {
    e.preventDefault();
    const rowId = $(this).attr('data-id');
    ui.confirmarExclusao(async function() {
        try {
            const fetcher = (typeof fetchWithAuth !== 'undefined') ? fetchWithAuth : fetch;
            const res = await fetcher('/api/beneficiarios/' + rowId, { method: 'DELETE' });
            if (res.ok) {
                if (typeof dataTable !== 'undefined') dataTable.ajax.reload(null, false);
                ui.feedbackSucesso('Beneficiário excluído com sucesso!');
            } else {
                ui.feedbackErro('Erro ao excluir o beneficiário.');
            }
        } catch (err) {
            ui.feedbackErro('Erro de conexão ao tentar excluir.');
        }
    }, 'Atenção', 'Tem certeza que deseja excluir?');
});