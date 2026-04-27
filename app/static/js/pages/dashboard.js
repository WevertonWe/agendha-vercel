// js/dashboard.js

// Endereço da nossa nova API de consolidados
const API_CONSOLIDADO_URL = '/api/beneficiarios/consolidado/atividades';

// Função que será executada quando a página carregar
document.addEventListener("DOMContentLoaded", () => {
    carregarDadosKPI();
    carregarEventosGRH();
});

async function carregarDadosKPI() {
    try {
        console.log("Buscando dados consolidados da API...");
        const response = await fetchWithAuth(API_CONSOLIDADO_URL);
        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status}`);
        }
        const dadosPorMunicipio = await response.json();
        console.log("Dados recebidos:", dadosPorMunicipio);

        // Calcula os totais gerais usando o método 'reduce'
        const totais = dadosPorMunicipio.reduce((acc, municipio) => {
            acc.total_beneficiarios += municipio.total_beneficiarios;
            acc.cadastrado += municipio.cadastrado;
            acc.em_cadastro += municipio.em_cadastro;
            acc.outros_status += municipio.outros_status;
            return acc;
        }, { // Valores iniciais do acumulador
            total_beneficiarios: 0,
            cadastrado: 0,
            em_cadastro: 0,
            outros_status: 0
        });

        console.log("Totais calculados:", totais);

        // Atualiza os cartões no HTML com os totais
        document.getElementById('kpi-total-beneficiarios').textContent = totais.total_beneficiarios;
        document.getElementById('kpi-cadastrados').textContent = totais.cadastrado;
        document.getElementById('kpi-em-cadastro').textContent = totais.em_cadastro;
        document.getElementById('kpi-outros-status').textContent = totais.outros_status;

        // Chama a função para preencher a tabela com os dados detalhados
        popularTabelaConsolidada(dadosPorMunicipio);
        criarGraficoMunicipios(dadosPorMunicipio);


    } catch (error) {
        console.error("Erro ao carregar dados do dashboard:", error);
        // Opcional: Mostrar uma mensagem de erro em algum lugar da página
        const kpiCards = document.querySelectorAll('.kpi-number');
        kpiCards.forEach(card => card.textContent = 'Erro!');
    }
}

function popularTabelaConsolidada(dadosPorMunicipio) {
    const tbody = document.getElementById('tbody-consolidado');
    if (!tbody) {
        console.error("Elemento 'tbody-consolidado' não encontrado!");
        return;
    }

    tbody.innerHTML = ''; // Limpa a mensagem "Carregando dados..."

    dadosPorMunicipio.forEach(municipio => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${municipio.municipio}</td>
            <td>${municipio.total_beneficiarios}</td>
            <td>${municipio.em_cadastro}</td>
            <td>${municipio.cadastrado}</td>
            <td>${municipio.a_construir}</td>
            <td>${municipio.construida}</td>
            <td>${municipio.outros_status}</td>
        `;
        tbody.appendChild(tr);
    });
}

function criarGraficoMunicipios(dadosPorMunicipio) {
    const ctx = document.getElementById('graficoMunicipios');
    if (!ctx) return;

    // 1. Preparamos os dados para o gráfico
    const labels = dadosPorMunicipio.map(item => item.municipio); // Nomes dos municípios
    const dataPoints = dadosPorMunicipio.map(item => item.total_beneficiarios); // Totais

    // 2. Criamos o gráfico
    new Chart(ctx, {
        type: 'bar', // Tipo do gráfico (pode ser 'pie', 'line', etc.)
        data: {
            labels: labels,
            datasets: [{
                label: 'Total de Beneficiários',
                data: dataPoints,
                backgroundColor: 'rgba(0, 123, 255, 0.7)', // Cor das barras
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true // Garante que o eixo Y comece no zero
                }
            },
            responsive: true,
            plugins: {
                legend: {
                    display: false // Esconde a legenda, pois o título já é claro
                },
                title: {
                    display: true,
                    text: 'Distribuição de Beneficiários por Município'
                }
            }
        }



    });
}


// =======================================================
// ==      LÓGICA PARA A TABELA DE EVENTOS GRH          ==
// =======================================================

const API_EVENTOS_URL = '/api/eventos_grh';

// Função principal para carregar e mostrar os eventos
async function carregarEventosGRH() {
    try {
        console.log("Buscando dados de eventos da API...");
        const response = await fetchWithAuth(API_EVENTOS_URL);
        if (!response.ok) throw new Error("Falha ao buscar eventos.");

        const eventos = await response.json();
        popularTabelaEventos(eventos);

    } catch (error) {
        console.error("Erro ao carregar eventos:", error);
        const tbody = document.getElementById('tbody-eventos');
        if (tbody) tbody.innerHTML = `<tr><td colspan="4">Erro ao carregar eventos.</td></tr>`;
    }
}

// Função para preencher a tabela com os dados
function popularTabelaEventos(eventos) {
    const tbody = document.getElementById('tbody-eventos');
    if (!tbody) return;

    tbody.innerHTML = ''; // Limpa a tabela

    eventos.forEach(evento => {
        const tr = document.createElement('tr');
        // Usamos um truque com 'dataset' para guardar o ID do evento no checkbox
        tr.innerHTML = `
            <td>${evento.id}</td>
            <td>${evento.municipio_comunidade}</td>
            <td>${evento.dia_previsto}</td>
            <td class="text-center">
                <input class="form-check-input" type="checkbox" 
                       data-id="${evento.id}" ${evento.realizado ? 'checked' : ''}>
            </td>
        `;
        tbody.appendChild(tr);
    });

    // Adiciona o 'escutador' de eventos para todos os checkboxes da tabela
    tbody.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', async (event) => {
            const eventoId = event.target.dataset.id;
            const novoStatus = event.target.checked;
            await atualizarStatusEvento(eventoId, novoStatus);
        });
    });
}

// Função para enviar a atualização para o back-end (API PUT)
async function atualizarStatusEvento(id, novoStatus) {
    console.log(`Atualizando evento ID ${id} para realizado = ${novoStatus}`);

    // Primeiro, buscamos o evento completo para ter todos os dados
    const responseGet = await fetchWithAuth(`${API_EVENTOS_URL}`);
    const eventos = await responseGet.json();
    const eventoParaAtualizar = eventos.find(e => e.id == id);

    if (!eventoParaAtualizar) {
        console.error(`Evento com ID ${id} não encontrado.`);
        return;
    }

    // Atualizamos apenas o campo 'realizado'
    eventoParaAtualizar.realizado = novoStatus;

    try {
        const response = await fetchWithAuth(`${API_EVENTOS_URL}/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(eventoParaAtualizar)
        });

        if (!response.ok) {
            throw new Error("Falha ao atualizar o status no servidor.");
        }

        const result = await response.json();
        console.log("Atualização bem-sucedida:", result);
        // Opcional: mostrar uma notificação de sucesso para o usuário

    } catch (error) {
        console.error("Erro ao atualizar evento:", error);
        // Opcional: reverter o checkbox e mostrar uma mensagem de erro
        alert("Não foi possível salvar a alteração. Verifique o console.");
    }
}


