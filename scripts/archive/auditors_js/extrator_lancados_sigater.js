/**
 * ==============================================================================
 * 🔍 EXTRATOR DE LANÇAMENTOS DO SIGATER (SEM NECESSIDADE DE COLETUM)
 * ==============================================================================
 * Função:
 * 1. Lê todos os beneficiários lançados no SIGATER no mês/atividade selecionada.
 * 2. Extrai: Código, Nome, CPF, Data da Execução, Técnico e Comunidade.
 * 3. Exibe painel visual interativo na tela com busca, botão de copiar e exportar CSV.
 * 4. Funciona tanto na tela de "Listagem de Execuções" quanto na tela do "Cronograma".
 *
 * Como usar:
 * 1. No SIGATER, abra a tela desejada (ou clique em [AE] no mês que quer conferir).
 * 2. Pressione F12 e abra a aba "Console".
 * 3. Cole este código e aperte [ENTER].
 * ==============================================================================
 */
(async function() {
    console.clear();
    console.log('%c🚀 INICIANDO LEITURA DOS LANÇAMENTOS NO SIGATER...', 'color: #00bcd4; font-size: 16px; font-weight: bold;');

    // Remove painel anterior se já existir
    const antigo = document.getElementById('painelExtratorSigater');
    if (antigo) antigo.remove();

    function normalizar(txt) {
        if (!txt) return '';
        return String(txt).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase().trim();
    }

    // -------------------------------------------------------------
    // CENÁRIO 1: O usuário está na tela do Cronograma / Matriz
    // (com colunas de meses como "17° 11/2025", botões [AE], etc.)
    // -------------------------------------------------------------
    const linksAE = Array.from(document.querySelectorAll('a, button')).filter(el => {
        const txt = (el.innerText || '').trim();
        const title = (el.getAttribute('title') || '').toLowerCase();
        const href = (el.getAttribute('href') || '').toLowerCase();
        const onclick = (el.getAttribute('onclick') || '').toLowerCase();
        return txt === 'AE' || title.includes('execu') || href.includes('cronograma_execucao') || onclick.includes('cronograma_execucao');
    });

    // Se estiver na tela do cronograma e não houver tabela de execuções aberta:
    const linksLupa = Array.from(document.querySelectorAll('a[href*="/read/"], a[href*="cronograma_execucao/read"], table tbody tr a'));
    const urlsExecucoesDiretas = Array.from(new Set(
        linksLupa.map(a => a.href).filter(h => h && (h.includes('/read/') || h.includes('cronograma_execucao/read')))
    ));

    if (urlsExecucoesDiretas.length === 0 && linksAE.length > 0) {
        // Identificar os meses disponíveis nas colunas
        const colunasMeses = [];
        const badgesMes = Array.from(document.querySelectorAll('div, span, th, td, h4, h5, p')).filter(el => {
            const t = el.innerText || '';
            return /\d+°\s*\d{1,2}\/\d{4}/.test(t);
        });

        // Monta painel orientando a escolher o mês ou clicar no [AE]
        const divAviso = document.createElement('div');
        divAviso.id = 'painelExtratorSigater';
        divAviso.style.cssText = 'position:fixed;bottom:20px;right:20px;width:520px;background:#181a20;color:#fff;padding:22px;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:999999;font-family:Segoe UI, sans-serif;font-size:13px;border:2px solid #00bcd4;';
        divAviso.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:10px;margin-bottom:14px;">
                <strong style="color:#00bcd4;font-size:16px;">📌 Tela de Cronograma Detectada</strong>
                <button onclick="document.getElementById('painelExtratorSigater').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:18px;">✖</button>
            </div>
            <p style="margin:0 0 12px 0;color:#ddd;line-height:1.5;">
                Você está na tela de <strong>Planejamento / Cronograma</strong>.<br>
                Para listar quem foi lançado no mês desejado:
            </p>
            <div style="background:#22252e;padding:12px;border-radius:8px;border-left:4px solid #00e676;margin-bottom:14px;">
                👉 <strong>Clique no botão [AE]</strong> (Atividades Executadas) ou no <strong>ícone com número</strong> abaixo da coluna do mês que você deseja conferir.
            </div>
            <p style="color:#aaa;font-size:12px;margin:0 0 14px 0;">
                Assim que a lista de execuções abrir na tela, cole este mesmo código novamente para extrair todos os nomes e CPFs instantaneamente!
            </p>
            <button onclick="document.getElementById('painelExtratorSigater').remove()" style="width:100%;padding:10px;background:#00bcd4;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;">
                Entendido! Vou abrir a lista de execuções
            </button>
        `;
        document.body.appendChild(divAviso);
        return;
    }

    if (urlsExecucoesDiretas.length === 0) {
        alert('Nenhuma execução encontrada nesta tela. Por favor, clique no botão [AE] da coluna do mês para abrir a listagem de execuções.');
        return;
    }

    console.log(`📋 Detectadas ${urlsExecucoesDiretas.length} execuções na página. Extraindo dados...`);

    // -------------------------------------------------------------
    // CENÁRIO 2: Extração profunda das execuções
    // -------------------------------------------------------------
    const div = document.createElement('div');
    div.id = 'painelExtratorSigater';
    div.style.cssText = 'position:fixed;bottom:20px;right:20px;width:620px;max-height:85vh;overflow-y:auto;background:#181a20;color:#fff;padding:22px;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:999999;font-family:Segoe UI, sans-serif;font-size:13px;border:2px solid #00bcd4;';
    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:10px;margin-bottom:14px;">
            <strong style="color:#00bcd4;font-size:16px;">⏳ Lendo as ${urlsExecucoesDiretas.length} Execuções no SIGATER...</strong>
            <button onclick="document.getElementById('painelExtratorSigater').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:18px;">✖</button>
        </div>
        <p id="statusProgressoExtrator" style="margin:0;color:#ccc;">Consultando detalhes dos beneficiários...</p>
        <div style="width:100%;background:#2a2d36;height:12px;border-radius:6px;margin:12px 0;overflow:hidden;">
            <div id="barraProgressoExtrator" style="width:0%;height:100%;background:linear-gradient(90deg, #00bcd4, #00e676);transition:width 0.2s;"></div>
        </div>
    `;
    document.body.appendChild(div);

    const lancados = [];
    const BATCH_SIZE = 12;
    let concluidos = 0;

    for (let i = 0; i < urlsExecucoesDiretas.length; i += BATCH_SIZE) {
        const batch = urlsExecucoesDiretas.slice(i, i + BATCH_SIZE);
        await Promise.all(batch.map(async (url) => {
            try {
                const resp = await fetch(url);
                if (resp.ok) {
                    const html = await resp.text();
                    const doc = new DOMParser().parseFromString(html, 'text/html');

                    let nomeBeneficiario = '';
                    let cpfBeneficiario = '';
                    let dataExecucao = '';
                    let tecnico = '';
                    let comunidade = '';
                    let municipio = '';

                    const trs = Array.from(doc.querySelectorAll('table tr'));
                    for (const tr of trs) {
                        const texto = tr.innerText || '';

                        // CPF e Nome
                        if (texto.includes('Dados da DAP') || texto.includes('DAP_MDA') || /\d{3}\.\d{3}\.\d{3}-\d{2}/.test(texto)) {
                            const tds = Array.from(tr.querySelectorAll('td'));
                            tds.forEach(td => {
                                const t = td.innerText.trim();
                                if (/\d{3}\.\d{3}\.\d{3}-\d{2}/.test(t)) {
                                    cpfBeneficiario = t;
                                } else if (t.split(' ').length >= 2 && t.length >= 6 && !t.includes('DAP') && !t.includes('SIGATER') && !t.includes('MDA')) {
                                    nomeBeneficiario = t;
                                }
                            });
                        }

                        // Data
                        if (texto.includes('Data') && /\d{2}\/\d{2}\/\d{4}/.test(texto) && !dataExecucao) {
                            const m = texto.match(/(\d{2}\/\d{2}\/\d{4})/);
                            if (m) dataExecucao = m[1];
                        }

                        // Técnico
                        if ((texto.includes('Técnico') || texto.includes('Responsável')) && !tecnico) {
                            const partes = texto.split(/[:\n]/);
                            if (partes.length > 1 && partes[1].trim().length > 3) {
                                tecnico = partes[1].trim();
                            }
                        }

                        // Comunidade / Município
                        if ((texto.includes('Comunidade') || texto.includes('Localidade')) && !comunidade) {
                            const partes = texto.split(/[:\n]/);
                            if (partes.length > 1) comunidade = partes[1].trim();
                        }
                    }

                    // Fallback Nome pelo arquivo anexado
                    if (!nomeBeneficiario) {
                        const pdfLinks = Array.from(doc.querySelectorAll('a[href*=".pdf"], [title*=".pdf"]')).map(a => a.innerText || a.title || '');
                        for (const pdf of pdfLinks) {
                            const match = pdf.match(/([A-Z_]+)_-_(?:ATESTE|COLETUM)/i);
                            if (match) {
                                nomeBeneficiario = match[1].replace(/_/g, ' ');
                                break;
                            }
                        }
                    }

                    const codExecMatch = url.match(/\/read\/(\d+)/);
                    const codExec = codExecMatch ? `#${codExecMatch[1]}` : 'N/A';

                    lancados.push({
                        codigo: codExec,
                        beneficiario: (nomeBeneficiario || 'Não Identificado').trim(),
                        cpf: (cpfBeneficiario || '-').trim(),
                        data: dataExecucao || 'S/ Data',
                        tecnico: tecnico || '-',
                        comunidade: comunidade || '-',
                        url: url
                    });
                }
            } catch (err) {
            } finally {
                concluidos++;
                const perc = Math.round((concluidos / urlsExecucoesDiretas.length) * 100);
                const elStatus = document.getElementById('statusProgressoExtrator');
                const elBarra = document.getElementById('barraProgressoExtrator');
                if (elStatus) elStatus.innerText = `Lendo execuções: ${concluidos} de ${urlsExecucoesDiretas.length} (${perc}%)...`;
                if (elBarra) elBarra.style.width = `${perc}%`;
            }
        }));
    }

    // Ordenar alfabeticamente por nome
    lancados.sort((a, b) => a.beneficiario.localeCompare(b.beneficiario));

    // Exibir no console
    console.log('%c====================================================================', 'color: #888');
    console.log(`%c📊 TOTAL DE BENEFICIÁRIOS LANÇADOS NESTE MÊS NO SIGATER: %c${lancados.length}`, 'font-size: 15px; font-weight: bold; color: #fff;', 'color: #00e676; font-weight: bold; font-size: 16px;');
    console.log('%c====================================================================', 'color: #888');
    console.table(lancados.map((item, idx) => ({
        '#': idx + 1,
        'Código': item.codigo,
        'Beneficiário': item.beneficiario,
        'CPF': item.cpf,
        'Data': item.data,
        'Técnico': item.tecnico,
        'Comunidade': item.comunidade
    })));

    // Montar Painel Flutuante Final
    window._dadosLancadosSigater = lancados;

    function renderizarLista(itens) {
        return itens.map((p, i) => `
            <div style="background:#22252e;padding:10px 14px;border-radius:8px;margin-bottom:8px;border-left:4px solid #00bcd4;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <strong style="color:#fff;font-size:13px;">${i+1}. ${p.beneficiario}</strong>
                    <span style="background:#00bcd4;color:#000;font-size:10px;font-weight:bold;padding:2px 6px;border-radius:4px;margin-left:8px;">${p.codigo}</span><br>
                    <small style="color:#bbb;">CPF: <span style="color:#00e676;">${p.cpf}</span> | 📅 Data: <strong>${p.data}</strong></small><br>
                    <small style="color:#ffd54f;">👤 Técnico: ${p.tecnico} ${p.comunidade !== '-' ? '• 📍 ' + p.comunidade : ''}</small>
                </div>
                <a href="${p.url}" target="_blank" style="background:#333842;color:#00bcd4;padding:6px 10px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:bold;white-space:nowrap;">
                    Ver ↗
                </a>
            </div>
        `).join('');
    }

    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:10px;margin-bottom:12px;">
            <div>
                <strong style="color:#00e676;font-size:16px;">✅ ${lancados.length} Lançamentos Encontrados</strong><br>
                <small style="color:#aaa;">Listagem oficial extraída do SIGATER</small>
            </div>
            <button onclick="document.getElementById('painelExtratorSigater').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:18px;">✖</button>
        </div>

        <input type="text" id="filtroExtrator" placeholder="🔍 Filtrar por nome ou CPF..." style="width:100%;box-sizing:border-box;padding:10px;border-radius:6px;background:#22252e;border:1px solid #444;color:#fff;margin-bottom:12px;font-size:13px;outline:none;">

        <div id="containerListaExtrator" style="max-height:400px;overflow-y:auto;padding-right:4px;">
            ${renderizarLista(lancados)}
        </div>

        <div style="display:flex;gap:10px;margin-top:14px;">
            <button id="btnCopiarListaExtrator" style="flex:1;padding:10px;background:#00bcd4;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:13px;">
                📋 Copiar Lista (${lancados.length})
            </button>
            <button id="btnBaixarCsvExtrator" style="flex:1;padding:10px;background:#00e676;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:13px;">
                📥 Baixar Excel / CSV
            </button>
        </div>
    `;

    // Filtro em tempo real
    document.getElementById('filtroExtrator').addEventListener('input', function(e) {
        const termo = normalizar(e.target.value);
        const filtrados = window._dadosLancadosSigater.filter(item => 
            normalizar(item.beneficiario).includes(termo) || item.cpf.replace(/\D/g, '').includes(termo.replace(/\D/g, ''))
        );
        document.getElementById('containerListaExtrator').innerHTML = renderizarLista(filtrados);
    });

    // Copiar Texto
    document.getElementById('btnCopiarListaExtrator').onclick = function() {
        const txt = window._dadosLancadosSigater.map((p, i) => `${i+1}. ${p.beneficiario} | CPF: ${p.cpf} | Data: ${p.data} | Código: ${p.codigo} | Técnico: ${p.tecnico}`).join('\n');
        navigator.clipboard.writeText(txt).then(() => alert(`Lista dos ${window._dadosLancadosSigater.length} beneficiários copiada com sucesso!`));
    };

    // Baixar CSV
    document.getElementById('btnBaixarCsvExtrator').onclick = function() {
        let csv = '\uFEFFNº;Código SIGATER;Beneficiário;CPF;Data Execução;Técnico;Comunidade;Link\n';
        window._dadosLancadosSigater.forEach((p, i) => {
            csv += `"${i+1}";"${p.codigo}";"${p.beneficiario}";"${p.cpf}";"${p.data}";"${p.tecnico}";"${p.comunidade}";"${p.url}"\n`;
        });
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `Lancamentos_SIGATER_${new Date().toISOString().slice(0,10)}.csv`;
        link.click();
    };
})();
