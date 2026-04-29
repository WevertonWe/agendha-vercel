// static/js/pages/consolidado.js
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetchWithAuth('/api/beneficiarios/consolidado/atividades');
        if (!response.ok) throw new Error('Falha ao buscar dados da API.');
        const dados = await response.json();
        console.log('Dados recebidos do Consolidado:', dados);

        let totalBeneficiarios = 0, totalCadastrados = 0, totalEmCadastro = 0, totalOutros = 0;

        // A CORREÇÃO ESTÁ AQUI: Adicionamos '|| 0' para tratar valores nulos ou undefined
        dados.forEach(d => {
            totalBeneficiarios += Number(d.total_beneficiarios || 0);
            totalCadastrados += Number(d.cadastrado || 0);
            totalEmCadastro += Number(d.em_cadastro || 0);
            totalOutros += Number(d.outros_status || 0);
        });

        const elTotal = document.getElementById('kpi-total-beneficiarios');
        const elCadastrados = document.getElementById('kpi-cadastrados');
        const elEmCadastro = document.getElementById('kpi-em-cadastro');
        const elOutros = document.getElementById('kpi-outros-status');

        if (elTotal) elTotal.textContent = totalBeneficiarios;
        if (elCadastrados) elCadastrados.textContent = totalCadastrados;
        if (elEmCadastro) elEmCadastro.textContent = totalEmCadastro;
        if (elOutros) elOutros.textContent = totalOutros;

        const tbody = document.getElementById('tbody-consolidado');
        tbody.innerHTML = '';
        if (dados.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">Nenhum dado encontrado.</td></tr>';
            return;
        }

        dados.forEach(municipio => {
            const tr = document.createElement('tr');
            // A CORREÇÃO TAMBÉM ESTÁ AQUI: Adicionamos '|| 0' nas células da tabela
            tr.innerHTML = `
                <td>${municipio.municipio}</td>
                <td>${municipio.total_beneficiarios || 0}</td>
                <td>${municipio.em_cadastro || 0}</td>
                <td>${municipio.cadastrado || 0}</td>
                <td>${municipio.a_construir || 0}</td>
                <td>${municipio.construida || 0}</td>
                <td>${municipio.outros_status || 0}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Erro ao carregar dados consolidados:", error);
    }
});
