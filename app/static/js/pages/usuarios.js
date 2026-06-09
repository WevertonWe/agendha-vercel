const API_URL = '/api/users';
const PBI_API_URL = '/api/admin/powerbi';
let currentUserList = [];
let currentPowerBIList = [];

// ==========================================
// 1. GERENCIAMENTO DE USUÁRIOS
// ==========================================

async function carregarUsuarios() {
    try {
        const response = await fetchWithAuth(API_URL);
        if (!response.ok) throw new Error('Falha ao carregar usuários');
        currentUserList = await response.json();

        const tbody = document.getElementById('tbody-usuarios');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (currentUserList.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhum usuário encontrado.</td></tr>';
            return;
        }

        currentUserList.forEach(user => {
            const tr = document.createElement('tr');

            // Badge logic
            const roleBadge = user.role === 'admin'
                ? '<span class="badge bg-danger">Administrador</span>'
                : '<span class="badge bg-secondary">Usuário</span>';

            const statusBadge = user.is_active
                ? '<span class="badge bg-success">Ativo</span>'
                : '<span class="badge bg-warning text-dark">Inativo</span>';

            tr.innerHTML = `
                <td class="fw-bold text-dark">${user.username}</td>
                <td>${user.full_name || '-'}</td>
                <td class="text-center">${roleBadge}</td>
                <td class="text-center">${statusBadge}</td>
                <td class="text-center">
                    <button class="btn btn-warning btn-sm shadow-sm me-1" onclick="editarUsuario('${user.username}')" title="Editar">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button class="btn btn-danger btn-sm shadow-sm" onclick="deletarUsuario('${user.username}')" title="Excluir">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error(error);
        if (window.ui) ui.feedbackErro('Erro ao carregar usuários: ' + error.message);
    }
}

// Abrir Modal de Criação (Resetar form)
function abrirModalNovoUsuario() {
    const form = document.getElementById('form-usuario');
    if (!form) return;
    form.reset();
    form.classList.remove('was-validated');
    document.getElementById('usuario_id').value = ''; // Limpa ID oculto (username antigo)
    document.getElementById('username').removeAttribute('disabled'); // Habilita campo username

    // Título
    document.getElementById('modalTitulo').innerHTML = '<i class="bi bi-person-plus-fill me-2"></i><span>Novo Usuário</span>';

    // Checkbox ativo por padrão
    const activeCheck = document.getElementById('is_active');
    if (activeCheck) activeCheck.checked = true;

    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(document.getElementById('modalUsuario'));
        modal.show();
    }
}

// Abrir Modal de Edição
window.editarUsuario = function (username) {
    const user = currentUserList.find(u => u.username === username);
    if (!user) return;

    const form = document.getElementById('form-usuario');
    if (!form) return;
    form.reset();
    form.classList.remove('was-validated');

    // Preencher campos
    document.getElementById('usuario_id').value = user.username; // Usamos username como ID
    document.getElementById('username').value = user.username;
    document.getElementById('username').setAttribute('disabled', 'disabled'); // Não pode mudar username na edição

    document.getElementById('full_name').value = user.full_name || '';
    document.getElementById('role').value = user.role;

    // Password fica vazio (opcional na edição)
    document.getElementById('password').value = '';

    const activeCheck = document.getElementById('is_active');
    if (activeCheck) activeCheck.checked = user.is_active;

    document.getElementById('modalTitulo').innerHTML = '<i class="bi bi-pencil-square me-2"></i><span>Editar Usuário</span>';

    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(document.getElementById('modalUsuario'));
        modal.show();
    }
}

// Deletar usuário
window.deletarUsuario = function (username) {
    if (window.ui) {
        ui.confirmarExclusao(
            `${API_URL}/${username}`,
            `Usuário ${username}`,
            () => carregarUsuarios()
        );
    }
}


// ==========================================
// 2. GERENCIAMENTO DE CREDENCIAIS POWERBI
// ==========================================

async function carregarCredenciaisPowerBI() {
    try {
        const response = await fetchWithAuth(PBI_API_URL);
        if (!response.ok) throw new Error('Falha ao carregar credenciais PowerBI');
        currentPowerBIList = await response.json();

        const tbody = document.getElementById('tbody-powerbi');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (currentPowerBIList.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhuma credencial PowerBI cadastrada.</td></tr>';
            return;
        }

        currentPowerBIList.forEach(cred => {
            const tr = document.createElement('tr');

            const statusBadge = cred.is_active
                ? '<span class="badge bg-success">Ativo</span>'
                : '<span class="badge bg-warning text-dark">Inativo</span>';

            tr.innerHTML = `
                <td class="fw-bold text-dark">${cred.project_name}</td>
                <td>${cred.email}</td>
                <td class="text-center">
                    <div class="d-inline-flex align-items-center bg-light px-3 py-1 rounded border border-light-subtle">
                        <span id="pbi-text-${cred.id}" class="me-2 fw-mono small" style="letter-spacing: 2px;">••••••••</span>
                        <button class="btn btn-sm btn-link p-0 text-decoration-none text-muted" onclick="revelarSenhaPowerBI('${cred.id}')" id="btn-reveal-${cred.id}" title="Revelar Senha">
                            <i class="bi bi-eye-fill"></i>
                        </button>
                    </div>
                </td>
                <td class="text-center">${statusBadge}</td>
                <td class="text-center">
                    <button class="btn btn-warning btn-sm shadow-sm me-1" onclick="editarCredencialPowerBI('${cred.id}')" title="Editar">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button class="btn btn-danger btn-sm shadow-sm" onclick="deletarCredencialPowerBI('${cred.id}')" title="Excluir">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error(error);
        if (window.ui) ui.feedbackErro('Erro ao carregar credenciais PowerBI: ' + error.message);
    }
}

// Revelar Senha
window.revelarSenhaPowerBI = async function(id) {
    const textSpan = document.getElementById(`pbi-text-${id}`);
    const btnIcon = document.querySelector(`#btn-reveal-${id} i`);
    if (!textSpan || !btnIcon) return;

    // Se já estiver revelado, oculta de volta para segurança
    if (btnIcon.classList.contains('bi-eye-slash-fill')) {
        textSpan.textContent = '••••••••';
        textSpan.style.letterSpacing = '2px';
        btnIcon.classList.remove('bi-eye-slash-fill');
        btnIcon.classList.add('bi-eye-fill');
        return;
    }

    try {
        const response = await fetchWithAuth(`${PBI_API_URL}/${id}/reveal`);
        if (!response.ok) throw new Error('Não foi possível revelar a senha');
        const data = await response.json();
        
        textSpan.textContent = data.password;
        textSpan.style.letterSpacing = 'normal';
        btnIcon.classList.remove('bi-eye-fill');
        btnIcon.classList.add('bi-eye-slash-fill');
    } catch (error) {
        console.error(error);
        if (window.ui) ui.feedbackErro('Erro ao descriptografar senha: ' + error.message);
    }
}

// Abrir Modal de Nova Credencial
window.abrirModalNovaCredencial = function() {
    const form = document.getElementById('form-powerbi');
    if (!form) return;
    form.reset();
    form.classList.remove('was-validated');
    document.getElementById('powerbi_id').value = '';
    
    // Título
    document.getElementById('modalPowerBITitulo').innerHTML = '<i class="bi bi-plus-circle-fill me-2"></i><span>Nova Credencial PowerBI</span>';
    
    // Senha obrigatória na criação
    document.getElementById('pbi_password').setAttribute('required', 'required');
    document.getElementById('pbi_password_help').textContent = 'Digite a senha da credencial.';

    const activeCheck = document.getElementById('pbi_is_active');
    if (activeCheck) activeCheck.checked = true;

    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(document.getElementById('modalPowerBI'));
        modal.show();
    }
}

// Abrir Modal de Edição de Credencial
window.editarCredencialPowerBI = function(id) {
    const cred = currentPowerBIList.find(c => String(c.id) === String(id));
    if (!cred) return;

    const form = document.getElementById('form-powerbi');
    if (!form) return;
    form.reset();
    form.classList.remove('was-validated');

    // Preencher campos
    document.getElementById('powerbi_id').value = cred.id;
    document.getElementById('pbi_project_name').value = cred.project_name;
    document.getElementById('pbi_email').value = cred.email;
    
    // Password opcional na edição
    document.getElementById('pbi_password').value = '';
    document.getElementById('pbi_password').removeAttribute('required');
    document.getElementById('pbi_password_help').textContent = 'Deixe em branco para manter a senha atual.';

    const activeCheck = document.getElementById('pbi_is_active');
    if (activeCheck) activeCheck.checked = cred.is_active;

    document.getElementById('modalPowerBITitulo').innerHTML = '<i class="bi bi-pencil-square me-2"></i><span>Editar Credencial PowerBI</span>';

    if (typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(document.getElementById('modalPowerBI'));
        modal.show();
    }
}

// Deletar Credencial
window.deletarCredencialPowerBI = function(id) {
    if (window.ui) {
        ui.confirmarExclusao(
            `${PBI_API_URL}/${id}`,
            `Credencial do projeto`,
            () => carregarCredenciaisPowerBI()
        );
    }
}


// ==========================================
// 3. INICIALIZAÇÃO E BINDINGS
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Carregar aba padrão
    carregarUsuarios();

    // Adicionar eventos de clique para trocar de abas e recarregar dados
    const tabUsuarios = document.getElementById('usuarios-tab');
    if (tabUsuarios) {
        tabUsuarios.addEventListener('shown.bs.tab', () => {
            carregarUsuarios();
        });
    }

    const tabPowerBI = document.getElementById('powerbi-tab');
    if (tabPowerBI) {
        tabPowerBI.addEventListener('shown.bs.tab', () => {
            carregarCredenciaisPowerBI();
        });
    }

    // Botão novo usuário
    const btnNovo = document.getElementById('btn-novo-usuario');
    if (btnNovo) {
        btnNovo.addEventListener('click', abrirModalNovoUsuario);
    }

    // Botão nova credencial PowerBI
    const btnNovaPBI = document.getElementById('btn-nova-credencial');
    if (btnNovaPBI) {
        btnNovaPBI.addEventListener('click', abrirModalNovaCredencial);
    }

    // Submit do Form Usuário
    const formUsuario = document.getElementById('form-usuario');
    if (formUsuario) {
        formUsuario.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Validação básica
            if (!formUsuario.checkValidity()) {
                e.stopPropagation();
                formUsuario.classList.add('was-validated');
                return;
            }

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const full_name = document.getElementById('full_name').value;
            const role = document.getElementById('role').value;
            const is_active = document.getElementById('is_active') ? document.getElementById('is_active').checked : true;

            // Modo Edição se tiver usuario_id (que guarda o username original)
            const originalUsername = document.getElementById('usuario_id').value;
            const isEdit = !!originalUsername;

            const payload = { full_name, role, is_active };

            // Lógica específica
            if (isEdit) {
                // Na edição, senha é opcional
                if (password) payload.password = password;
            } else {
                // Na criação, username e password são obrigatórios
                payload.username = username;
                payload.password = password;
                if (!password) {
                    ui.feedbackErro('Senha é obrigatória para novos usuários.');
                    return;
                }
            }

            const url = isEdit ? `${API_URL}/${originalUsername}` : API_URL;
            const method = isEdit ? 'PUT' : 'POST';

            try {
                if (window.ui && window.Swal) Swal.showLoading();

                const response = await fetchWithAuth(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    const modalEl = document.getElementById('modalUsuario');
                    let modal = null;
                    if (typeof bootstrap !== 'undefined') {
                        modal = bootstrap.Modal.getInstance(modalEl);
                    }
                    if (modal) modal.hide();

                    ui.feedbackSucesso(
                        isEdit ? 'Usuário atualizado!' : 'Usuário criado!',
                        () => carregarUsuarios()
                    );
                } else {
                    const err = await response.json();
                    ui.feedbackErro('Erro: ' + (err.detail || 'Falha ao salvar.'));
                }
            } catch (error) {
                console.error(error);
                ui.feedbackErro('Erro de conexão ao salvar usuário.');
            }
        });
    }

    // Submit do Form PowerBI
    const formPowerBI = document.getElementById('form-powerbi');
    if (formPowerBI) {
        formPowerBI.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Validação básica
            if (!formPowerBI.checkValidity()) {
                e.stopPropagation();
                formPowerBI.classList.add('was-validated');
                return;
            }

            const id = document.getElementById('powerbi_id').value;
            const project_name = document.getElementById('pbi_project_name').value;
            const email = document.getElementById('pbi_email').value;
            const password = document.getElementById('pbi_password').value;
            const is_active = document.getElementById('pbi_is_active') ? document.getElementById('pbi_is_active').checked : true;

            const isEdit = !!id;
            const payload = { project_name, email, is_active };

            if (isEdit) {
                // Na edição, senha é opcional
                if (password) payload.password = password;
            } else {
                // Na criação, senha é obrigatória
                if (!password) {
                    ui.feedbackErro('Senha é obrigatória para novas credenciais.');
                    return;
                }
                payload.password = password;
            }

            const url = isEdit ? `${PBI_API_URL}/${id}` : PBI_API_URL;
            const method = isEdit ? 'PUT' : 'POST';

            try {
                if (window.ui && window.Swal) Swal.showLoading();

                const response = await fetchWithAuth(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    const modalEl = document.getElementById('modalPowerBI');
                    let modal = null;
                    if (typeof bootstrap !== 'undefined') {
                        modal = bootstrap.Modal.getInstance(modalEl);
                    }
                    if (modal) modal.hide();

                    ui.feedbackSucesso(
                        isEdit ? 'Credencial PowerBI atualizada!' : 'Credencial PowerBI criada!',
                        () => carregarCredenciaisPowerBI()
                    );
                } else {
                    const err = await response.json();
                    ui.feedbackErro('Erro: ' + (err.detail || 'Falha ao salvar.'));
                }
            } catch (error) {
                console.error(error);
                ui.feedbackErro('Erro de conexão ao salvar credencial.');
            }
        });
    }
});
