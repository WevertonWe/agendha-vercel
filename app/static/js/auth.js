// static/js/auth.js

/**
 * Wrapper para o fetch que adiciona automaticamente o header Authorization
 * e redireciona para login em caso de 401.
 */
async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('access_token');

    const headers = {
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers
    };

    const response = await fetch(url, config);

    if (response.status === 401) {
        // Token expirado ou inválido
        console.warn('Sessão expirada ou inválida. Redirecionando para login...');
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return response; // Retorna a resposta mesmo assim para o caller tratar se quiser
    }

    return response;
}

// Função de Logout
function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
}

// Adiciona listener ao botão de logout se existir na página
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }

    // Lógica para Trocar Senha
    const formTrocarSenha = document.getElementById('formTrocarSenha');
    if (formTrocarSenha) {
        formTrocarSenha.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const senhaAtual = document.getElementById('senha_atual').value;
            const novaSenha = document.getElementById('nova_senha').value;
            const confirmarSenha = document.getElementById('confirmar_senha').value;

            if (novaSenha !== confirmarSenha) {
                if (window.ui) ui.feedbackAviso('A nova senha e a confirmação não conferem.');
                else alert('A nova senha e a confirmação não conferem.');
                return;
            }

            const submitBtn = formTrocarSenha.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Salvando...'; // nosec

            try {
                const response = await fetchWithAuth('/api/auth/change-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        senha_atual: senhaAtual,
                        nova_senha: novaSenha,
                        confirmar_senha: confirmarSenha
                    })
                });

                if (response.ok) {
                    if (window.ui) ui.feedbackSucesso('Senha alterada com sucesso!');
                    else alert('Senha alterada com sucesso!');
                    
                    const modalEl = document.getElementById('modalTrocarSenha');
                    if (modalEl && typeof bootstrap !== 'undefined') {
                        const modal = bootstrap.Modal.getInstance(modalEl);
                        if (modal) modal.hide();
                    }
                    formTrocarSenha.reset();
                } else {
                    const errorData = await response.json();
                    const msg = errorData.detail || 'Erro ao alterar senha.';
                    if (window.ui) ui.feedbackErro(msg);
                    else alert(msg);
                }
            } catch (error) {
                console.error('Erro:', error);
                if (window.ui) ui.feedbackErro('Erro de conexão ao alterar senha.');
                else alert('Erro de conexão ao alterar senha.');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText; // nosec
            }
        });
    }
});
