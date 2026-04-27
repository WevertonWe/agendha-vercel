const API_URL = '/api/users';
let currentUserList = [];

// Função principal de carregamento
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
    document.getElementById('form-usuario').reset();
    document.getElementById('usuario_id').value = ''; // Limpa ID oculto (username antigo)
    document.getElementById('username').removeAttribute('disabled'); // Habilita campo username

    // Título
    document.getElementById('modalTitulo').innerHTML = '<i class="bi bi-person-plus-fill me-2"></i><span>Novo Usuário</span>';

    // Checkbox ativo por padrão
    const activeCheck = document.getElementById('is_active');
    if (activeCheck) activeCheck.checked = true;

    if (typeof bootstrap !== 'undefined') {
        new bootstrap.Modal(document.getElementById('modalUsuario')).show();
    }
}

// Abrir Modal de Edição
/**
 * @descrição Abre modal de edição carregando dados do cache local.
 * @param {string} username - O username é usado como chave de busca.
 */
window.editarUsuario = function (username) {
    const user = currentUserList.find(u => u.username === username);
    if (!user) return;

    const form = document.getElementById('form-usuario');
    form.reset();

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
        new bootstrap.Modal(document.getElementById('modalUsuario')).show();
    }
}

// Deletar
window.deletarUsuario = function (username) {
    if (window.ui) {
        ui.confirmarExclusao(
            `${API_URL}/${username}`,
            `Usuário ${username}`,
            () => carregarUsuarios()
        );
    }
}


// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarUsuarios();

    // Botão novo usuário
    const btnNovo = document.getElementById('btn-novo-usuario');
    if (btnNovo) {
        btnNovo.addEventListener('click', abrirModalNovoUsuario);
    }

    // Submit do Form
    const form = document.getElementById('form-usuario');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Validação básica
            if (!form.checkValidity()) {
                e.stopPropagation();
                form.classList.add('was-validated');
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
});
