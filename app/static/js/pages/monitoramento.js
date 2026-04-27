document.addEventListener('DOMContentLoaded', () => {
    const API_URL = '/api/eventos_grh';
    const tbody = document.getElementById('tbody-eventos');
    const modalEl = document.getElementById('modalEvento');
    let modal;
    if (typeof bootstrap !== 'undefined') {
        modal = new bootstrap.Modal(modalEl);
    }
    const form = document.getElementById('form-evento');
    const modalLabel = document.getElementById('modalEventoLabel');
    const eventoIdInput = document.getElementById('evento-id');
    const infoArquivo = document.getElementById('arquivo-existente-info');

    async function carregarEventos() {
        try {
            const response = await fetchWithAuth(API_URL);
            if (!response.ok) throw new Error('Falha ao carregar dados do servidor.');

            const eventos = await response.json();
            tbody.innerHTML = '';

            eventos.forEach(evento => {
                const tr = document.createElement('tr');
                tr.dataset.eventoId = evento.id;

                // Formatar a data (exemplo simples, ajuste se necessário)
                // Se a data já vier formatada do seu DB, pode remover isto.
                let dataFormatada = evento.dia_previsto;
                if (evento.dia_previsto && evento.dia_previsto.includes('T')) {
                    dataFormatada = new Date(evento.dia_previsto).toLocaleDateString('pt-BR', { timeZone: 'UTC' });
                } else if (evento.dia_previsto && evento.dia_previsto.includes('-')) {
                    // Converte AAAA-MM-DD para DD/MM/AAAA
                    const partes = evento.dia_previsto.split('-');
                    if (partes.length === 3) {
                        dataFormatada = `${partes[2]}/${partes[1]}/${partes[0]}`;
                    }
                }

                let hrefDocumento = '';
                if (evento.caminho_arquivo) {
                    const nomeArquivo = evento.caminho_arquivo.split('/').pop();
                    hrefDocumento = `/api/grh/documento/${encodeURIComponent(nomeArquivo)}`;
                }

                tr.innerHTML = `
                    <td class="col-municipio" title="${evento.municipio_comunidade}">${evento.municipio_comunidade}</td>
                    <td class="col-data">${dataFormatada}</td> 
                    <td class="col-observacao" title="${evento.observacao || ''}">${evento.observacao || ''}</td>
                    <td class="col-documento">
                        ${hrefDocumento ? `<a href="${hrefDocumento}" target="_blank" class="btn btn-info btn-sm" title="Ver Documento"><i class="bi bi-file-earmark-pdf-fill"></i></a>` : ''}
                    </td>
                    <td class="col-realizado">
                        <div class="form-check form-switch d-flex justify-content-center">
                            <input class="form-check-input" type="checkbox" role="switch" data-id="${evento.id}" ${evento.realizado ? 'checked' : ''}>
                        </div>
                    </td>
                    <td class="col-acoes">
                        <button class="btn btn-warning btn-sm btn-editar" title="Editar"><i class="bi bi-pencil-fill"></i></button>
                        <button class="btn btn-danger btn-sm btn-deletar" title="Deletar"><i class="bi bi-trash-fill"></i></button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } catch (error) {
            console.error("Erro ao carregar eventos:", error);
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Falha ao carregar os dados.</td></tr>';
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = eventoIdInput.value;
        const formData = new FormData(form); // <-- Pega TODOS os campos, incluindo o ficheiro

        // MUDANÇA!
        // A URL e o método são definidos dinamicamente.
        const url = id ? `${API_URL}/${id}` : API_URL;
        const method = id ? 'PUT' : 'POST';

        try {
            // MUDANÇA!
            // Não há mais 'if/else' para o body.
            // Enviamos SEMPRE FormData, tanto para POST quanto para PUT.
            // O back-end agora sabe como tratar um PUT com FormData.
            const response = await fetchWithAuth(url, {
                method: method,
                body: formData
                // Não defina 'Content-Type', o browser faz isso
                // automaticamente para FormData (multipart/form-data).
            });

            if (!response.ok) {
                const erro = await response.json();
                throw new Error(`Falha ao salvar o evento: ${erro.detail || response.statusText}`);
            }

            if (modal) modal.hide();
            ui.feedbackSucesso('Evento salvo com sucesso!');
            carregarEventos();
        } catch (error) {
            ui.feedbackErro(error.message);
        }
    });

    tbody.addEventListener('click', async (e) => {
        const target = e.target;
        const tr = target.closest('tr');
        if (!tr) return;

        const id = tr.dataset.eventoId;

        // --- Lógica para o botão EDITAR ---
        if (target.closest('.btn-editar')) {
            try {
                // (Sua lógica original de buscar na lista)
                const eventos = await (await fetchWithAuth(API_URL)).json();
                const evento = eventos.find(ev => ev.id == id);

                if (!evento) throw new Error('Evento não encontrado.');

                modalLabel.textContent = 'Editar Evento';
                eventoIdInput.value = evento.id;
                document.getElementById('municipio_comunidade').value = evento.municipio_comunidade;
                document.getElementById('dia_previsto').value = evento.dia_previsto;
                document.getElementById('observacao').value = evento.observacao || '';

                if (evento.caminho_arquivo) {
                    const nomeArquivo = evento.caminho_arquivo.split('/').pop();
                    const hrefDocumento = `/api/grh/documento/${encodeURIComponent(nomeArquivo)}`;
                    infoArquivo.innerHTML = `Arquivo atual: <a href="${hrefDocumento}" target="_blank">Ver</a>. Envie um novo para substituir.`;
                    infoArquivo.classList.remove('d-none');
                } else {
                    infoArquivo.innerHTML = 'Nenhum arquivo anexado. Envie um novo.';
                    infoArquivo.classList.remove('d-none');
                }
                // Limpa o campo de ficheiro para não enviar o antigo
                document.getElementById('arquivo').value = '';
                modal.show();
            } catch (error) {
                ui.feedbackErro("Erro ao carregar dados para edição: " + error.message);
            }
        }

        // --- Lógica para o botão DELETAR ---
        if (target.closest('.btn-deletar')) {
            const municipio = tr.cells[0].textContent;
            ui.confirmarExclusao(
                `${API_URL}/${id}`,
                `Evento ${municipio}`,
                () => carregarEventos()
            );
        }

        // --- Lógica para o switch 'REALIZADO' ---
        if (target.classList.contains('form-check-input')) {
            try {
                // MUDANÇA!
                // 1. A URL agora aponta para a nova rota '/status'
                // 2. O body envia APENAS o status de 'realizado'
                const response = await fetchWithAuth(`${API_URL}/${id}/status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ realizado: target.checked })
                });

                if (!response.ok) throw new Error('Falha ao atualizar o status.');

                // Adiciona feedback visual
                tr.classList.add('table-row-success');
                setTimeout(() => tr.classList.remove('table-row-success'), 1000);

            } catch (error) {
                ui.feedbackErro(error.message);
                target.checked = !target.checked; // Reverte o switch em caso de erro
            }
        }
    });

    document.querySelector('[data-bs-target="#modalEvento"]').addEventListener('click', () => {
        modalLabel.textContent = 'Adicionar Novo Evento';
        form.reset();
        eventoIdInput.value = '';
        infoArquivo.classList.add('d-none');
    });

    carregarEventos();
});
