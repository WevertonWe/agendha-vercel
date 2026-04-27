/**
 * Gestão de Materiais - Lógica Frontend
 */

let tabelaMateriais;
const API_URL = '/api/materiais';
let currentId = null;

$(document).ready(function () {
    initTable();
});

/**
 * @descrição Inicializa o DataTables de Materiais com configuração server-side simplificada (client-side processing do JSON total).
 * @comportamento
 *  1. Busca JSON de /api/materiais/.
 *  2. Configura colunas: Nome (negrito), Categoria, Unidade (Badge), Ações (Editar/Excluir).
 *  3. Define linguagem PT-BR.
 */
function initTable() {
    tabelaMateriais = $('#tabelaMateriais').DataTable({
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json"
        },
        ajax: {
            url: API_URL + '/',
            dataSrc: '',
            error: function (xhr, error, thrown) {
                console.error("Erro ao carregar dados:", xhr);
                if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Não foi possível carregar os materiais.', 'error');
            }
        },
        columns: [
            { data: 'id', className: 'text-center align-middle' },
            {
                data: 'nome',
                className: 'text-center align-middle',
                render: function (data, type, row) {
                    return `<div class="fw-bold">${data}</div>`;
                }
            },
            { data: 'categoria', className: 'text-center align-middle' },
            {
                data: 'unidade',
                className: 'text-center align-middle',
                render: function (data) {
                    return `<span class="badge bg-light text-dark border">${data}</span>`;
                }
            },
            { data: 'descricao', className: 'text-center align-middle' },
            {
                data: null,
                className: 'text-center align-middle text-nowrap',
                render: function (data, type, row) {
                    return `
                        <div class="d-flex justify-content-center gap-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="editarMaterial(${row.id})" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="excluirMaterial(${row.id})" title="Excluir">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    `;
                }
            }
        ],
        dom: '<"d-flex justify-content-between align-items-center mb-3"f>t<"d-flex justify-content-between align-items-center mt-3"ip>',
        pageLength: 10
    });
}

function openModal(material = null) {
    if (material) {
        currentId = material.id;
        $('#modalTitle').text('Editar Material');
        $('#materialId').val(material.id);
        $('#nome').val(material.nome);
        $('#categoria').val(material.categoria);
        $('#unidade').val(material.unidade);
        $('#descricao').val(material.descricao);
    } else {
        currentId = null;
        $('#modalTitle').text('Novo Material');
        $('#formMaterial')[0].reset();
        $('#materialId').val('');
        $('#unidade').val('un'); // Default e sugestão
    }

    $('#modalMaterial').modal('show');
}

window.editarMaterial = function (id) {
    let dados = tabelaMateriais.rows().data().toArray().find(item => item.id == id);
    if (dados) {
        openModal(dados);
    }
};

window.excluirMaterial = function (id) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'Tem certeza?',
            text: "Esta ação não pode ser desfeita.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sim, excluir!',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `${API_URL}/${id}`,
                    type: 'DELETE',
                    headers: {
                        "Authorization": "Bearer " + localStorage.getItem("access_token")
                    },
                    success: function () {
                        Swal.fire('Excluído!', 'O material foi removido.', 'success');
                        tabelaMateriais.ajax.reload();
                    },
                    error: function (xhr) {
                        Swal.fire('Erro!', 'Falha ao excluir o registro.', 'error');
                    }
                });
            }
        });
    }
};

/**
 * @descrição Salva (Cria ou Atualiza) um material.
 * @uso Botão "Salvar" no Modal de Material.
 * @comportamento
 *  1. Valida campos obrigatórios (Nome, Unidade).
 *  2. Monta payload JSON.
 *  3. Decide método HTTP (POST ou PUT) baseado em 'currentId'.
 *  4. Envia para API e recarrega tabela em caso de sucesso.
 */
window.salvarMaterial = function () {
    // Validação básica
    if (!$('#nome').val() || !$('#unidade').val()) {
        if (typeof Swal !== 'undefined') Swal.fire('Atenção', 'Preencha os campos obrigatórios (*).', 'warning');
        return;
    }

    const payload = {
        nome: $('#nome').val(),
        unidade: $('#unidade').val(),
        categoria: $('#categoria').val() || null,
        descricao: $('#descricao').val() || null
    };

    const method = currentId ? 'PUT' : 'POST';
    const url = currentId ? `${API_URL}/${currentId}` : API_URL + '/';

    $.ajax({
        url: url,
        type: method,
        contentType: 'application/json',
        data: JSON.stringify(payload),
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("access_token")
        },
        success: function () {
            $('#modalMaterial').modal('hide');
            if (typeof Swal !== 'undefined') Swal.fire('Sucesso!', 'Operação realizada com sucesso.', 'success');
            tabelaMateriais.ajax.reload();
        },
        error: function (xhr) {
            let msg = 'Erro ao salvar.';
            if (xhr.status === 422) {
                try {
                    const detail = xhr.responseJSON.detail;
                    if (Array.isArray(detail)) {
                        msg = detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('<br>');
                    } else {
                        msg = detail;
                    }
                } catch (e) { }
            } else if (xhr.responseJSON && xhr.responseJSON.detail) {
                msg = xhr.responseJSON.detail;
            }
            if (typeof Swal !== 'undefined') Swal.fire('Erro!', msg, 'error');
        }
    });
};
