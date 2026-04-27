// ===================================
// == TESTE DE CARREGAMENTO DO FICHEIRO ==
console.log("Olá do Parceiro de Programação! O ficheiro fila-validacao.js foi carregado com sucesso!");
// ===================================

// Espera o DOM (a página HTML) ser completamente carregado antes de executar o script
document.addEventListener('DOMContentLoaded', function () {

    // Inicializa a tabela DataTables com configurações básicas
    // e define o idioma para português do Brasil.
    const tabela = new DataTable('#tabela-validacao', {
        language: {
            url: 'https://cdn.datatables.net/plug-ins/2.0.8/i18n/pt-BR.json',
        },
        // Ordena a tabela pela primeira coluna (ID) em ordem decrescente por padrão
        order: [[0, 'desc']]
    });

    // Função assíncrona para buscar os dados da API
    async function carregarFilaValidacao() {
        try {
            // Faz a chamada para a nossa API no back-end
            const response = await fetchWithAuth('/api/ocr/fila-validacao');

            // Se a resposta não for bem-sucedida (ex: erro 500), lança um erro
            if (!response.ok) {
                throw new Error(`Erro na rede: ${response.statusText}`);
            }

            // Converte a resposta em JSON
            const data = await response.json();

            // Limpa a tabela de quaisquer dados antigos antes de adicionar novos
            tabela.clear();

            // Itera sobre cada item recebido da API
            data.forEach(item => {
                // Formata a data para um formato mais legível (dd/mm/aaaa hh:mm:ss)
                const dataFormatada = new Date(item.data_criacao).toLocaleString('pt-BR');

                // Cria os botões de ação
                const botaoValidar = `
                    <div class="d-flex gap-2">
                        <a href="/validacao?id=${item.id}" class="btn btn-primary btn-sm" title="Validar">
                            <i class="bi bi-pencil-square"></i> Validar
                        </a>
                        <button class="btn btn-danger btn-sm btn-delete" data-id="${item.id}" title="Excluir">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                `;

                // Adiciona uma nova linha na tabela com os dados do item
                tabela.row.add([
                    item.id,
                    item.nome_arquivo,
                    item.status,
                    dataFormatada,
                    botaoValidar
                ]);
            });

            // Redesenha a tabela para exibir as novas linhas adicionadas
            tabela.draw();

        } catch (error) {
            // Se ocorrer algum erro durante o processo, exibe no console
            console.error('Falha ao carregar a fila de validação:', error);
            const corpoTabela = document.querySelector('#tabela-validacao tbody');
            corpoTabela.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Não foi possível carregar os dados. Tente novamente mais tarde.</td></tr>`;
        }
    }

    // Event Delegation para o botão de excluir
    document.querySelector('#tabela-validacao tbody').addEventListener('click', async function (e) {
        // Verifica se o clique foi num botão de delete ou no ícone dentro dele
        const btn = e.target.closest('.btn-delete');
        if (!btn) return;

        const id = btn.getAttribute('data-id');
        if (!id) return;

        if (!confirm('Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.')) {
            return;
        }

        try {
            const response = await fetchWithAuth(`/api/ocr/fila-validacao/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                // Remove a linha da tabela DataTables
                // O método row() do DataTables pode buscar pelo elemento TR
                const tr = btn.closest('tr');
                tabela.row(tr).remove().draw(false); // false mantém a paginação
            } else {
                alert('Erro ao excluir item.');
            }
        } catch (error) {
            console.error('Erro ao excluir:', error);
            alert('Erro de conexão ao tentar excluir.');
        }
    });

    // Chama a função para carregar os dados assim que a página estiver pronta
    carregarFilaValidacao();
});
