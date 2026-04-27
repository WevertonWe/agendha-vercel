// static/js/pages/graficos.js
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetchWithAuth('/api/beneficiarios/consolidado/atividades');
        if (!response.ok) throw new Error('Falha ao buscar dados da API.');
        const dados = await response.json();

        const labelsMunicipios = dados.map(d => d.municipio);
        const dataMunicipios = dados.map(d => d.total_beneficiarios || 0); // Correção aqui
        renderizarGraficoBarras(labelsMunicipios, dataMunicipios);

        let totalEmCadastro = 0, totalCadastrado = 0, totalAConstruir = 0, totalConstruida = 0, totalOutros = 0;

        // A CORREÇÃO ESTÁ AQUI: Adicionamos '|| 0' para tratar valores nulos ou undefined
        dados.forEach(d => {
            totalEmCadastro += d.em_cadastro || 0;
            totalCadastrado += d.cadastrado || 0;
            totalAConstruir += d.a_construir || 0;
            totalConstruida += d.construida || 0;
            totalOutros += d.outros_status || 0;
        });

        const labelsStatus = ['Em Cadastro', 'Cadastrado', 'A Construir', 'Construída', 'Outros Status'];
        const dataStatus = [totalEmCadastro, totalCadastrado, totalAConstruir, totalConstruida, totalOutros];
        renderizarGraficoPizza(labelsStatus, dataStatus);

    } catch (error) {
        console.error("Erro ao carregar dados para os gráficos:", error);
    }
});

function renderizarGraficoBarras(labels, dataPoints) {
    const ctx = document.getElementById('graficoMunicipios').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total de Beneficiários',
                data: dataPoints,
                backgroundColor: '#0d6efd', // Primary Blue
                borderRadius: 4, // Rounded corners
                barPercentage: 0.7, // Slightly thinner bars
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { borderDash: [2, 2] } // Dashed Y grid
                },
                x: {
                    grid: { display: false } // Remove X grid lines
                }
            },
            plugins: {
                legend: { display: false } // Hide legend for single dataset
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function renderizarGraficoPizza(labels, dataPoints) {
    const ctx = document.getElementById('graficoStatusGeral').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Status do Projeto',
                data: dataPoints,
                backgroundColor: [
                    '#ffc107', // Em Cadastro (Amarelo)
                    '#198754', // Cadastrado (Verde)
                    '#0d6efd', // A Construir (Azul)
                    '#0dcaf0', // Construída (Ciano)
                    '#6c757d'  // Outros (Cinza)
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%', // Thinner ring
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                }
            }
        }
    });
}
