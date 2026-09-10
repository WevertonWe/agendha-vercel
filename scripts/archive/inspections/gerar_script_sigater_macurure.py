import json

with open("migson_caracterizacao_47.json", "r", encoding="utf-8") as f:
    migson_data = json.load(f)

migson_json = json.dumps(migson_data, ensure_ascii=False)

js_code = """/**
 * ==============================================================================
 * 🔍 AUDITOR AUTOMÁTICO SIGATER: CARACTERIZAÇÃO I (MÊS 23 - MAIO/2026)
 * ==============================================================================
 * Atividade: # 60765 (Caracterização I)
 * Município Alvo: MACURURÉ (Migson Brayne)
 *
 * Como usar:
 * 1. Na página do SIGATER (onde você está vendo a lista de Abaré e Macururé),
 * 2. Pressione F12 e clique na aba "Console".
 * 3. Cole este código abaixo e aperte ENTER.
 * ==============================================================================
 */
(async function() {
    console.clear();
    console.log('%c🚀 INICIANDO AUDITORIA DE MACURURÉ NO SIGATER...', 'color: #00bcd4; font-size: 16px; font-weight: bold;');

    const coletumMigson = __MIGSON_DATA__;

    function normalizar(txt) {
        if (!txt) return '';
        return String(txt).normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toUpperCase().trim();
    }

    function cleanCpf(cpf) {
        if (!cpf) return '';
        return String(cpf).replace(/\\D/g, '');
    }

    function similaridade(s1, s2) {
        const n1 = normalizar(s1);
        const n2 = normalizar(s2);
        if (n1 === n2) return 1.0;
        if (!n1 || !n2) return 0.0;
        if (n1.includes(n2) || n2.includes(n1)) return 0.92;
        const p1 = n1.split(' '), p2 = n2.split(' ');
        if (p1.length >= 2 && p2.length >= 2) {
            if (p1[0] === p2[0] && p1[p1.length - 1] === p2[p2.length - 1]) return 0.88;
        }
        return 0.0;
    }

    // 1. Identifica todos os links das lupas de consulta
    const links = Array.from(document.querySelectorAll('a[href*="/read/"], a[href*="cronograma_execucao/read"], a[href*="execucao"]'));
    const urlsExecucoes = Array.from(new Set(
        links.map(a => a.href).filter(h => h && h.includes('/read/'))
    ));

    console.log(`📋 Total de execuções detectadas na página: ${urlsExecucoes.length}`);

    if (urlsExecucoes.length === 0) {
        alert('Nenhum link de execução encontrado na tela. Certifique-se de estar na listagem de execuções.');
        return;
    }

    // Painel Visual Flutuante
    const antigo = document.getElementById('painelAuditoriaMacurure');
    if (antigo) antigo.remove();

    const div = document.createElement('div');
    div.id = 'painelAuditoriaMacurure';
    div.style.cssText = 'position:fixed;bottom:20px;right:20px;width:560px;max-height:85vh;overflow-y:auto;background:#181a20;color:#fff;padding:20px;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:999999;font-family:Segoe UI, sans-serif;font-size:13px;border:2px solid #00bcd4;';
    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:8px;margin-bottom:12px;">
            <strong style="color:#00bcd4;font-size:15px;"><i class="fas fa-search"></i> Auditoria Macururé (Caracterização I - 5/2026)</strong>
            <button onclick="document.getElementById('painelAuditoriaMacurure').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:16px;">✖</button>
        </div>
        <p id="statusProgresso" style="margin:0;color:#ccc;">Consultando as ${urlsExecucoes.length} execuções no SIGATER...</p>
        <div style="width:100%;background:#2a2d36;height:12px;border-radius:6px;margin:12px 0;overflow:hidden;">
            <div id="barraProgresso" style="width:0%;height:100%;background:linear-gradient(90deg, #00bcd4, #00e676);transition:width 0.2s;"></div>
        </div>
    `;
    document.body.appendChild(div);

    // Leitura paralela em lotes de 10
    const sigaterLancados = [];
    const BATCH_SIZE = 10;
    let concluidos = 0;

    for (let i = 0; i < urlsExecucoes.length; i += BATCH_SIZE) {
        const batch = urlsExecucoes.slice(i, i + BATCH_SIZE);
        await Promise.all(batch.map(async (url) => {
            try {
                const resp = await fetch(url);
                if (resp.ok) {
                    const html = await resp.text();
                    const doc = new DOMParser().parseFromString(html, 'text/html');
                    
                    let nomeBeneficiario = '';
                    let cpfBeneficiario = '';

                    const trs = Array.from(doc.querySelectorAll('table tr'));
                    for (const tr of trs) {
                        const texto = tr.innerText || '';
                        if (/\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}/.test(texto)) {
                            const tds = Array.from(tr.querySelectorAll('td'));
                            tds.forEach(td => {
                                const t = td.innerText.trim();
                                if (/\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}/.test(t)) {
                                    cpfBeneficiario = t;
                                } else if (t.split(' ').length >= 2 && t.length >= 6 && !t.includes('DAP') && !t.includes('SIGATER') && !t.includes('MDA')) {
                                    nomeBeneficiario = t;
                                }
                            });
                        }
                    }

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

                    const codExec = url.match(/\\/read\\/(\\d+)/) ? url.match(/\\/read\\/(\\d+)/)[1] : '';

                    sigaterLancados.push({
                        codExec,
                        url,
                        nome: nomeBeneficiario || '',
                        cpf: cpfBeneficiario || '',
                        htmlBruto: normalizar(html)
                    });
                }
            } catch (err) {
            } finally {
                concluidos++;
                const perc = Math.round((concluidos / urlsExecucoes.length) * 100);
                const elStatus = document.getElementById('statusProgresso');
                const elBarra = document.getElementById('barraProgresso');
                if (elStatus) elStatus.innerText = `Lendo execuções: ${concluidos} de ${urlsExecucoes.length} (${perc}%)...`;
                if (elBarra) elBarra.style.width = `${perc}%`;
            }
        }));
    }

    // Cruzamento com os 47 de Migson
    const lancadosConfirmados = [];
    const faltamLancados = [];

    coletumMigson.forEach(col => {
        const nomeCol = col[1];
        const cpfCol = col[2];
        const nomeNorm = normalizar(nomeCol);
        const cpfLimpo = cleanCpf(cpfCol);

        let achou = false;
        let codigoAchado = '';

        for (const sig of sigaterLancados) {
            const sigCpf = cleanCpf(sig.cpf);
            if ((cpfLimpo.length >= 8 && sigCpf.includes(cpfLimpo)) ||
                similaridade(nomeCol, sig.nome) >= 0.85 ||
                sig.htmlBruto.includes(nomeNorm)) {
                achou = true;
                codigoAchado = sig.codExec;
                break;
            }}

        if (achou) {
            lancadosConfirmados.push({ ...col, codigoExecucao: codigoAchado });
        } else {
            faltamLancados.push(col);
        }
    });

    // Exibição dos resultados
    console.log('%c====================================================================', 'color: #888');
    console.log(`%c📊 RESULTADO DA CONFERÊNCIA DE MACURURÉ:
- Total de Campo (Coletum Migson): ${coletumMigson.length}
- Já Lançados no SIGATER: ${lancadosConfirmados.length}
- ⚠️ FALTAM LANÇAR NO SIGATER: ${faltamLancados.length}`, 'font-size: 14px; font-weight: bold; color: #00e676;');
    console.log('%c====================================================================', 'color: #888');

    console.log('%c🔴 LISTA DOS QUE FALTAM LANÇAR EM MACURURÉ:', 'color: #ff1744; font-size: 15px; font-weight: bold;');
    faltamLancados.forEach((f, idx) => {
        console.log(`%c${idx+1}. ${f[1]} | CPF: ${f[2]} | Comunidade: ${f[3]} | Data: ${f[5]}`, 'color: #ffc107; font-weight: bold;');
    });

    // Atualiza Painel na Tela
    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:8px;margin-bottom:12px;">
            <strong style="color:#00bcd4;font-size:15px;">📊 Auditoria Macururé: Caracterização I (5/2026)</strong>
            <button onclick="document.getElementById('painelAuditoriaMacurure').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:16px;">✖</button>
        </div>
        <div style="background:#232730;padding:10px;border-radius:8px;margin-bottom:12px;">
            <div>Total do Técnico Migson: <strong>${coletumMigson.length}</strong></div>
            <div style="color:#00e676;">✅ Já Lançados no SIGATER: <strong>${lancadosConfirmados.length}</strong></div>
            <div style="color:#ff1744;font-size:14px;font-weight:bold;margin-top:4px;">⚠️ FALTAM LANÇAR: <strong>${faltamLancados.length}</strong></div>
        </div>
        <div style="font-weight:bold;color:#ff9800;margin-bottom:6px;">⚠️ Beneficiários que Faltam Lançar:</div>
        <div style="background:#111;padding:10px;border-radius:8px;font-family:monospace;font-size:12px;color:#fff;max-height:220px;overflow-y:auto;">
            ${faltamLancados.map((f, i) => `<div><strong>${i+1}.</strong> ${f[1]} <br><span style="color:#aaa;">CPF: ${f[2]} | Com: ${f[3]} | Data: ${f[5]}</span></div><hr style="border:0;border-top:1px solid #222;margin:4px 0;">`).join('')}
        </div>
        <button id="btnCopiarFaltantes" style="width:100%;margin-top:10px;padding:8px;background:#00bcd4;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;">📋 Copiar Lista dos Faltantes</button>
    `;

    document.getElementById('btnCopiarFaltantes').onclick = function() {
        const texto = faltamLancados.map((f, i) => `${i+1}. ${f[1]} | CPF: ${f[2]} | Comunidade: ${f[3]} | Data: ${f[5]}`).join('\\n');
        navigator.clipboard.writeText(texto);
        alert('Lista dos que faltam lançar copiada com sucesso!');
    };
})();
""".replace("__MIGSON_DATA__", migson_json)

with open("auditor_sigater_caracterizacao_macurure.js", "w", encoding="utf-8") as f:
    f.write(js_code)

print("Arquivo 'auditor_sigater_caracterizacao_macurure.js' gerado com sucesso!")
