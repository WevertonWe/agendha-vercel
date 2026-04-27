// admin_auditoria.js

let currentOffset = 0;
const LIMIT = 20;
let isLoading = false;

document.addEventListener('DOMContentLoaded', () => {
    loadAuditLogs();

    document.getElementById('loadMoreBtn').addEventListener('click', () => {
        loadAuditLogs();
    });

    document.getElementById('auditSearch').addEventListener('input', debounce(() => {
        currentOffset = 0;
        document.getElementById('auditTimeline').innerHTML = ''; // Clear // nosec
        loadAuditLogs();
    }, 500));
});

function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

/**
 * @descrição Carrega logs de auditoria do servidor com paginação e busca.
 * @uso Init e Botão "Carregar Mais".
 * @param {string} search - Filtro de texto (obtido do input).
 * @comportamento
 *  1. Bloqueia botão para evitar duplo clique.
 *  2. Busca GET /admin/auditoria/dados.
 *  3. Se offset=0, limpa container (nova busca).
 *  4. Appenda cards de timeline via 'createTimelineItem'.
 */
async function loadAuditLogs() {
    if (isLoading) return;
    isLoading = true;

    const search = document.getElementById('auditSearch').value;
    const btn = document.getElementById('loadMoreBtn');
    btn.disabled = true;
    btn.textContent = 'Carregando...';

    try {
        const response = await fetch(`/admin/auditoria/dados?limit=${LIMIT}&offset=${currentOffset}&search=${encodeURIComponent(search)}`);

        if (!response.ok) {
            errorToast('Falha na comunicação com o servidor.');
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        const container = document.getElementById('auditTimeline');

        // Remove loading spinner if initial load
        if (currentOffset === 0 && container.querySelector('.spinner-border')) {
            container.innerHTML = ''; // nosec
        }

        if (result.data.length === 0) {
            if (currentOffset === 0) container.innerHTML = '<div class="text-center p-4 text-muted">Nenhum registro encontrado.</div>'; // nosec
            btn.style.display = 'none';
        } else {
            result.data.forEach(log => {
                const item = createTimelineItem(log);
                container.appendChild(item);
            });
            currentOffset += result.data.length;
            btn.style.display = 'inline-block';
        }

    } catch (error) {
        console.error('Erro ao carregar logs:', error);
        errorToast('Erro ao carregar dados. Tente novamente.');
    } finally {
        isLoading = false;
        btn.disabled = false;
        btn.textContent = 'Carregando Mais';
    }
}

function errorToast(msg) {
    // Simple toast fallback or use UI library if available
    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 p-3';
    toast.style.zIndex = '1100';
    toast.innerHTML = ` // nosec
        <div class="toast show align-items-center text-white bg-danger border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                   <i class="bi bi-exclamation-triangle-fill me-2"></i> ${msg}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close" onclick="this.closest('.toast').remove()"></button>
            </div>
        </div>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

/**
 * @descrição Cria elemento HTML para um item da timeline.
 * @param {Object} log - Objeto de log (data, operacao, usuario, detalhes).
 * @returns {HTMLElement} Div formatada com ícones e cores conforme 'operacao'.
 */
function createTimelineItem(log) {
    // Determine Style based on Operation
    let iconClass = 'bg-secondary';
    let icon = 'bi-circle';
    let badgeClass = 'text-bg-secondary';
    let rowClass = '';

    if (log.operacao === 'UPDATE') {
        iconClass = 'bg-warning text-dark';
        icon = 'bi-pencil-fill'; // Heroicon equiv: pencil
        badgeClass = 'text-bg-warning';
    } else if (log.operacao === 'INSERT') {
        iconClass = 'bg-success text-white';
        icon = 'bi-plus-lg'; // Heroicon equiv: plus
        badgeClass = 'text-bg-success';
    } else if (log.operacao === 'DELETE') {
        iconClass = 'bg-danger text-white';
        icon = 'bi-trash'; // Heroicon equiv: trash
        badgeClass = 'text-bg-danger';
    } else if (log.operacao === 'ACESSO') {
        iconClass = 'bg-info text-white';
        icon = 'bi-eye'; // Heroicon equiv: eye
        badgeClass = 'text-bg-info';
        rowClass = 'border-start border-info border-3';
    }

    const div = document.createElement('div');
    // Determine Border Class
    const isSystem = log.usuario === 'SYSTEM' || log.usuario === 'Anônimo';
    const borderClass = isSystem ? 'system-border' : 'user-border';

    div.className = `list-group-item list-group-item-action border-0 mb-3 rounded-3 shadow-sm d-flex gap-3 align-items-start ${rowClass} ${borderClass}`;
    div.style.cursor = 'pointer';
    div.style.transition = 'transform 0.1s';
    div.onmouseover = () => div.style.transform = 'scale(1.005)';
    div.onmouseout = () => div.style.transform = 'scale(1)';


    // Parse Date
    const data = new Date(log.data).toLocaleString();

    div.innerHTML = ` // nosec
        <div class="timeline-icon ${iconClass} rounded-circle d-flex align-items-center justify-content-center shadow-sm" style="width:40px; height:40px;">
            <i class="bi ${icon} fs-5"></i>
        </div>
        <div class="flex-grow-1">
            <div class="d-flex w-100 justify-content-between align-items-center mb-1">
                <h6 class="mb-0 fw-bold text-dark text-capitalize">
                    ${log.tabela !== 'N/A' ? log.tabela : 'Navegação'} 
                    <span class="badge ${badgeClass} small ms-2 rounded-pill px-2 custom-badge">${log.operacao}</span>
                </h6>
                <small class="text-muted text-end bg-light px-2 py-1 rounded">
                    <i class="bi bi-clock me-1"></i>${data}
                </small>
            </div>
            <div class="d-flex justify-content-between align-items-center">
                 <p class="mb-1 text-secondary text-truncate small" style="max-width: 450px;">${log.detalhes || 'Sem detalhes.'}</p>
                 <small class="text-primary fw-bold"><i class="bi bi-person-circle me-1"></i>${log.usuario}</small>
            </div>
        </div>
    `;

    div.addEventListener('click', () => {
        // Highlight active
        document.querySelectorAll('.list-group-item').forEach(el => {
            el.classList.remove('active-item', 'bg-light-subtle');
            // Remove inline style since class handles it, but keep class logic
        });
        div.classList.add('bg-light-subtle');
        // div.style.borderLeft = "4px solid #0d6efd"; // Handled by class now

        showDetails(log);
    });

    return div;
}

function showDetails(log) {
    const detailPanel = document.getElementById('detailPanel');

    let oldVal = safeJsonParse(log.valor_antigo);
    let newVal = safeJsonParse(log.valor_novo);

    // Simple Diff Logic
    let diffHtml = '';
    let actionBtn = '';

    if (log.operacao === 'ACESSO') {
        diffHtml = `<div class="p-3 bg-white rounded border border-light shadow-sm text-center">
            <i class="bi bi-geo-alt fs-1 text-info mb-3 d-block"></i>
            <h6 class="text-muted">Usuário navegou para:</h6>
            <code class="fs-5 text-dark bg-light px-3 py-1 rounded">${log.detalhes.replace('Acessou: ', '')}</code>
        </div>`;
    } else {
        if (log.operacao === 'UPDATE') {
            diffHtml = generateDiff(oldVal, newVal);
        } else if (log.operacao === 'INSERT') {
            diffHtml = `<pre class="text-success small bg-success-subtle p-3 rounded">${JSON.stringify(newVal, null, 2)}</pre>`;
        } else if (log.operacao === 'DELETE') {
            diffHtml = `<pre class="text-danger small bg-danger-subtle p-3 rounded">${JSON.stringify(oldVal, null, 2)}</pre>`;
        }

        actionBtn = `
        <div class="d-grid mt-4">
             <button class="btn btn-outline-danger btn-lg rounded-pill shadow-sm" onclick="undoAction(${log.id})">
                <i class="bi bi-arrow-counterclockwise me-2"></i>Reverter Esta Ação
             </button>
             <div class="text-center mt-2">
                <small class="text-muted" style="font-size: 0.75rem;">
                    <i class="bi bi-shield-exclamation me-1"></i>A ação será registrada no log.
                </small>
             </div>
        </div>`;
    }

    detailPanel.innerHTML = ` // nosec
        <div class="text-center border-bottom pb-4 mb-3">
             <div class="d-inline-block p-3 rounded-circle bg-light mb-3 shadow-sm">
                <i class="bi bi-file-earmark-text fs-2 text-primary"></i>
             </div>
             <h5 class="fw-bold text-dark mb-1">Registro #${log.id}</h5>
             <span class="badge bg-dark rounded-pill px-3 py-1">${log.operacao}</span>
        </div>
        
        <div class="d-flex justify-content-between mb-3 px-2">
            <small class="text-muted">Usuário</small>
            <span class="fw-bold text-dark">${log.usuario}</span>
        </div>
        <div class="d-flex justify-content-between mb-4 px-2">
            <small class="text-muted">Data</small>
            <span class="text-dark">${new Date(log.data).toLocaleString()}</span>
        </div>

        <h6 class="fw-bold text-secondary mb-3"><i class="bi bi-code-square me-2"></i>Detalhes da Operação</h6>
        <div class="bg-white p-2 rounded-3 border mb-3 diff-container shadow-inner" style="max-height: 350px; overflow-y: auto;">
            ${diffHtml}
        </div>

        ${actionBtn}
    `;
}

function safeJsonParse(str) {
    try {
        return str ? JSON.parse(str) : {};
    } catch {
        return {};
    }
}

function generateDiff(obj1, obj2) {
    let html = '<ul class="list-group list-group-flush">';
    const allKeys = new Set([...Object.keys(obj1), ...Object.keys(obj2)]);

    allKeys.forEach(key => {
        const val1 = obj1[key];
        const val2 = obj2[key];

        if (JSON.stringify(val1) !== JSON.stringify(val2)) {
            html += `<li class="list-group-item d-flex justify-content-between align-items-start bg-transparent">
                <div class="ms-2 me-auto">
                    <div class="fw-bold text-dark small mb-1">${key}</div>
                    ${val1 !== undefined ? `<div class="text-decoration-line-through text-danger small bg-danger-subtle px-1 rounded d-inline-block mb-1">${val1}</div>` : ''}
                    ${val2 !== undefined ? `<div class="text-success small bg-success-subtle px-1 rounded d-inline-block fw-bold">${val2}</div>` : ''}
                </div>
            </li>`;
        }
    });

    if (html === '<ul class="list-group list-group-flush">') {
        return '<p class="text-muted text-center py-3">Nenhuma alteração direta detectada nos campos rastreados.</p>';
    }

    return html + '</ul>';
}

window.undoAction = async (id) => {
    // Custom Modal using Bootstrap
    const modalHtml = `
    <div class="modal fade" id="confirmUndoModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content rounded-4 border-0 shadow-lg">
                <div class="modal-body text-center p-5">
                    <div class="text-danger mb-4">
                        <i class="bi bi-exclamation-circle-fill display-1"></i>
                    </div>
                    <h3 class="fw-bold mb-3">Confirmar Reversão?</h3>
                    <p class="text-muted fs-5 mb-4">Você está prestes a desfazer permanentemente a ação <strong>#${id}</strong>. Isso pode afetar dados dependentes.</p>
                    <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
                        <button type="button" class="btn btn-light btn-lg rounded-pill px-4 fw-bold" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-danger btn-lg rounded-pill px-4 fw-bold" id="btnConfirmUndo">Sim, Reverter</button>
                    </div>
                </div>
            </div>
        </div>
    </div>`;

    // Append modal to body
    const modalWrapper = document.createElement('div');
    modalWrapper.innerHTML = modalHtml; // nosec
    document.body.appendChild(modalWrapper);

    const modalEl = document.getElementById('confirmUndoModal');
    let modal;
    if (typeof bootstrap !== 'undefined') {
        modal = new bootstrap.Modal(modalEl);
        modal.show();
    }

    // Handle Confirm
    document.getElementById('btnConfirmUndo').onclick = async () => {
        if (modal) modal.hide();
        // Remove from DOM after hide
        modalEl.addEventListener('hidden.bs.modal', () => modalWrapper.remove());

        try {
            const res = await fetch(`/admin/auditoria/undo/${id}`, { method: 'POST' });
            const data = await res.json();

            if (res.ok) {
                showSuccessModal(data.message);
            } else {
                errorToast(`Erro: ${data.detail}`);
            }
        } catch (e) {
            errorToast("Erro de conexão ao tentar reverter.");
            console.error(e);
        }
    };
};

function showSuccessModal(msg) {
    const modalEl = document.getElementById('modalSucessoAudit');
    document.getElementById('modalSucessoMsg').textContent = msg;
    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }

    // Refresh on close
    modalEl.addEventListener('hidden.bs.modal', () => {
        document.getElementById('auditTimeline').innerHTML = ''; // nosec
        currentOffset = 0;
        loadAuditLogs();
        document.getElementById('detailPanel').innerHTML = '<div class="text-center py-5 text-muted">Atualizado. Selecione outro item.</div>'; // nosec
    }, { once: true });
}
