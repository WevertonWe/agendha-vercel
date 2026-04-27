// Define a URL base da nossa API de documentos
const API_URL = '/api/documentos';
let listagemDocumentosCache = []; // Cache local para evitar request extra no editar

/**
 * Função principal para carregar e exibir todos os documentos na tabela.
 */
async function carregarDocumentos() {
    try {
        const response = await fetchWithAuth(API_URL);
        if (!response.ok) {
            throw new Error('Falha ao buscar documentos da API.');
        }
        const documentos = await response.json();
        listagemDocumentosCache = documentos; // Salva no cache

        const tbody = document.getElementById('tbody-documentos');
        if (!tbody) return;

        tbody.innerHTML = ''; // Limpa a tabela

        if (documentos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted fst-italic py-4">Nenhum documento encontrado.</td></tr>';
            return;
        }

        documentos.forEach(doc => {
            const tr = document.createElement('tr');

            // Formata a data
            const dataUpload = new Date(doc.data_upload).toLocaleString('pt-BR');
            // Corrige caminho para web (windows \\ -> /)
            const caminhoArquivoWeb = doc.caminho_arquivo ? doc.caminho_arquivo.replace(/\\/g, '/') : '#';

            tr.innerHTML = `
                <td class="text-center fw-bold text-muted">${doc.id}</td>
                <td class="fw-bold text-dark">${doc.nome_documento || 'Sem Título'}</td>
                <td>
                    <div class="text-truncate" style="max-width: 250px;" title="${doc.descricao || ''}">
                        ${doc.descricao || '-'}
                    </div>
                </td>
                <td>
                    <a href="/${caminhoArquivoWeb}" target="_blank" class="btn btn-outline-primary btn-sm py-0" title="Baixar/Visualizar">
                        <i class="bi bi-file-earmark-arrow-down me-1"></i> Ver Ficheiro
                    </a>
                </td>
                <td class="text-muted">${dataUpload}</td>
                <td class="text-center text-nowrap">
                    <button class="btn btn-warning btn-sm shadow-sm me-1" onclick="editarDocumento(${doc.id})" title="Editar">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button class="btn btn-danger btn-sm shadow-sm btn-deletar" data-id="${doc.id}" title="Deletar">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error("Erro ao carregar documentos:", error);
        const tbody = document.getElementById('tbody-documentos');
        if (tbody) tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Erro ao carregar os dados.</td></tr>';
    }
}

// Global functions need to be on window for onclick events
/**
 * @descrição Prepara o modal para edição de um documento existente.
 * @param {int} id - ID do documento.
 * @comportamento
 *  1. Busca documento no cache local.
 *  2. Preenche formulário.
 *  3. Remove obrigatoriedade do arquivo (upload opcional na edição).
 *  4. Abre modal.
 */
window.editarDocumento = function (id) {
    const doc = listagemDocumentosCache.find(d => d.id === id);
    if (!doc) return;

    // Preenche o formulário
    const idEl = document.getElementById('documento_id');
    const nomeEl = document.getElementById('nome_documento');
    const descEl = document.getElementById('descricao');
    const inputArquivo = document.getElementById('arquivo'); // Arquivo é opcional na edição se não quiser trocar

    if (idEl) idEl.value = doc.id;
    if (nomeEl) nomeEl.value = doc.nome_documento;
    if (descEl) descEl.value = doc.descricao || '';

    // Na edição, o arquivo não é obrigatório se já existir
    if (inputArquivo) inputArquivo.removeAttribute('required');

    // Atualiza Título do Modal
    const modalTitulo = document.getElementById('modalTitulo');
    if (modalTitulo) modalTitulo.innerHTML = '<i class="bi bi-pencil-square me-2"></i><span>Editar Documento</span>';

    // Abre Modal
    const modalEl = document.getElementById('modalDocumento');
    if (modalEl && typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
};

window.limparFormulario = function () {
    const form = document.getElementById('form-documento');
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }
    const idEl = document.getElementById('documento_id');
    if (idEl) idEl.value = '';

    // Arquivo é obrigatório na criação
    const inputArquivo = document.getElementById('arquivo');
    if (inputArquivo) inputArquivo.setAttribute('required', 'required');

    const modalTitulo = document.getElementById('modalTitulo');
    if (modalTitulo) modalTitulo.innerHTML = '<i class="bi bi-cloud-upload-fill me-2"></i><span>Novo Documento</span>';
}

// Aguarda o carregamento completo do DOM
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-documento');
    const tbody = document.getElementById('tbody-documentos');
    const modalEl = document.getElementById('modalDocumento');

    // Resetar form ao fechar modal
    if (modalEl) {
        modalEl.addEventListener('hidden.bs.modal', () => {
            window.limparFormulario();
        });
    }

    // --- LÓGICA DE SALVAR (POST/PUT) ---
    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();

            if (!form.checkValidity()) {
                event.stopPropagation();
                form.classList.add('was-validated');
                return;
            }

            const formData = new FormData(form);
            const id = document.getElementById('documento_id').value;

            // Decide método e URL
            const method = id ? 'PUT' : 'POST';
            const url = id ? `${API_URL}/${id}` : API_URL;

            try {
                if (window.ui && window.Swal) Swal.showLoading();

                // Se for PUT e não tiver arquivo novo, o backend deve tratar
                const response = await fetchWithAuth(url, {
                    method: method,
                    body: formData,
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || 'Falha ao salvar o documento.');
                }

                if (modalEl && typeof bootstrap !== 'undefined') {
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }

                ui.feedbackSucesso(id ? 'Documento atualizado!' : 'Documento salvo!');
                carregarDocumentos();

            } catch (error) {
                console.error('Erro ao salvar:', error);
                ui.feedbackErro(error.message);
            }
        });
    }

    // --- LÓGICA DE DELEÇÃO ---
    if (tbody) {
        tbody.addEventListener('click', async (event) => {
            const deleteButton = event.target.closest('.btn-deletar');

            if (deleteButton) {
                const docId = deleteButton.dataset.id;
                ui.confirmarExclusao(
                    `${API_URL}/${docId}`,
                    `Documento ID ${docId}`,
                    () => carregarDocumentos()
                );
            }
        });
    }

    // Inicialização
    carregarDocumentos();
});
