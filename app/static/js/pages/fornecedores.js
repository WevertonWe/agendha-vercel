/**
 * Gestão de Fornecedores - Lógica Frontend
 */

let tabelaFornecedores;
const API_URL = '/api/fornecedores';
let currentId = null;

$(document).ready(function () {
    initTable();
    initMasks();
});

function initMasks() {
    // Máscara dinâmica para CPF ou CNPJ
    var behavior = function (val) {
        return val.replace(/\D/g, '').length === 11 ? '000.000.000-009' : '00.000.000/0000-00';
    },
        options = {
            onKeyPress: function (val, e, field, options) {
                field.mask(behavior.apply({}, arguments), options);
            }
        };

    $('#documento').mask(behavior, options);
    $('#telefone').mask('(00) 00000-0000');
    $('#cep').mask('00000-000');

    $('#cep').on('blur', function () {
        var cep = $(this).val().replace(/\D/g, '');
        if (cep != "") {
            var validacep = /^[0-9]{8}$/;
            if (validacep.test(cep)) {
                // Preenche com "..." enquanto consulta
                $('#endereco').val("...");

                $.getJSON("https://viacep.com.br/ws/" + cep + "/json/?callback=?", function (dados) {
                    if (!("erro" in dados)) {
                        // Atualiza os campos com os valores da consulta.
                        $('#endereco').val(dados.logradouro + ", " + dados.bairro + ", " + dados.localidade + " - " + dados.uf);
                        $('#numero').focus();
                    } else {
                        if (typeof Swal !== 'undefined') Swal.fire('Erro', 'CEP não encontrado.', 'error');
                        $('#endereco').val("");
                    }
                }).fail(function () {
                    if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Falha ao buscar CEP.', 'error');
                    $('#endereco').val("");
                });
            } else {
                if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Formato de CEP inválido.', 'error');
            }
        }
    });

    // Ao digitar o número, adiciona ao endereço se ele ainda não estiver lá (lógica simples)
    // Para evitar duplicidade complexa, vamos apenas concatenar na hora de salvar ou deixar o usuário livre.
    // O usuário pediu "Deixe o cursor focado no campo 'Número' ... para o usuário completar".
    // Vamos assumir que ele vai digitar o número e depois salvar. 
    // Uma melhoria seria concatenar no final.
    $('#numero').on('change', function () {
        let currentAddr = $('#endereco').val();
        let num = $(this).val();
        if (currentAddr && num && !currentAddr.includes('nº ' + num)) {
            $('#endereco').val(currentAddr + ", nº " + num);
        }
    });
}

function initTable() {
    tabelaFornecedores = $('#tabelaFornecedores').DataTable({
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json"
        },
        ajax: {
            url: API_URL + '/',
            dataSrc: '',
            error: function (xhr, error, thrown) {
                console.error("Erro ao carregar dados:", xhr);
                if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Não foi possível carregar os fornecedores.', 'error');
            }
        },
        columns: [
            { data: 'id', className: 'text-center align-middle' },
            {
                data: 'razao_social',
                className: 'text-center align-middle',
                render: function (data, type, row) {
                    return `
                        <div>
                            <div class="fw-bold">${data}</div>
                            ${row.nome_fantasia ? `<small class="text-muted">${row.nome_fantasia}</small>` : ''}
                        </div>
                    `;
                }
            },
            { data: 'cnpj_cpf', className: 'text-center align-middle' },
            { data: 'telefone', className: 'text-center align-middle' },
            { data: 'endereco', className: 'text-center align-middle' },
            {
                data: null,
                className: 'text-center align-middle text-nowrap',
                render: function (data, type, row) {
                    return `
                        <div class="d-flex justify-content-center gap-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="editarFornecedor(${row.id})" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="excluirFornecedor(${row.id})" title="Excluir">
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

function openModal(fornecedor = null) {
    if (fornecedor) {
        currentId = fornecedor.id;
        $('#modalTitle').text('Editar Fornecedor');
        $('#fornecedorId').val(fornecedor.id);
        $('#razaoSocial').val(fornecedor.razao_social);
        $('#nomeFantasia').val(fornecedor.nome_fantasia);
        $('#documento').val(fornecedor.cnpj_cpf).trigger('input'); // Trigger mask if needed
        $('#email').val(fornecedor.email);
        $('#telefone').val(fornecedor.telefone).trigger('input');
        $('#endereco').val(fornecedor.endereco);
    } else {
        currentId = null;
        $('#modalTitle').text('Novo Fornecedor');
        $('#formFornecedor')[0].reset();
        $('#fornecedorId').val('');
        $('#cep').val('');
        $('#numero').val('');
    }

    $('#modalFornecedor').modal('show');
}

window.editarFornecedor = function (id) {
    // Buscar o dado na linha da tabela ou via API. 
    // Como temos o ID, vamos buscar na API para garantir dados atualizados ou usar row data se preferir.
    // Pela simplicidade e para evitar row searching complexo, vamos buscar o objeto no datatable data.

    // Hack para pegar dados da tabela sem re-fetch
    let dados = tabelaFornecedores.rows().data().toArray().find(item => item.id == id);
    if (dados) {
        openModal(dados);
    }
};

window.excluirFornecedor = function (id) {
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
                        Swal.fire('Excluído!', 'O fornecedor foi removido.', 'success');
                        tabelaFornecedores.ajax.reload();
                    },
                    error: function (xhr) {
                        Swal.fire('Erro!', 'Falha ao excluir o registro.', 'error');
                    }
                });
            }
        });
    }
};

window.salvarFornecedor = function () {
    // Validação básica
    if (!$('#razaoSocial').val() || !$('#documento').val()) {
        if (typeof Swal !== 'undefined') Swal.fire('Atenção', 'Preencha os campos obrigatórios (*).', 'warning');
        return;
    }

    const payload = {
        razao_social: $('#razaoSocial').val(),
        nome_fantasia: $('#nomeFantasia').val() || null,
        cnpj_cpf: $('#documento').val(),
        email: $('#email').val() || null,
        telefone: $('#telefone').val() || null,
        endereco: $('#endereco').val() || null
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
            $('#modalFornecedor').modal('hide');
            if (typeof Swal !== 'undefined') Swal.fire('Sucesso!', 'Operação realizada com sucesso.', 'success');
            tabelaFornecedores.ajax.reload();
        },
        error: function (xhr) {
            let msg = 'Erro ao salvar.';
            if (xhr.status === 422) {
                // Tenta extrair erro de validação do Pydantic
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
