import json
from pathlib import Path

def gerar():
    with open('temp_julho_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f'Total de registros carregados: {len(data)}')

    registros_js = []
    for r in data:
        tec, nome, cpf, com, mun, dt, cid = r
        registros_js.append({
            'tecnico': tec,
            'beneficiario': nome,
            'cpf': cpf,
            'comunidade': com,
            'municipio': mun,
            'data': dt,
            'coletum_id': cid
        })

    json_str = json.dumps(registros_js, ensure_ascii=False, indent=2)

    js_code = f"""/**
 * ==============================================================================
 * 🔍 AUDITOR SIGATER: VISITAS TÉCNICAS AVALIATIVAS (MÊS 7 / JULHO DE 2026)
 * ==============================================================================
 * Atividade: # 67119 (25º 7/2026 - Ano 3) - Visita Técnica Avaliativa (2 h)
 * Meta Coletum: 281 registros | Lançados no SIGATER: ~277 | Pendentes: ~4
 *
 * Instruções de Uso:
 * 1. No SIGATER, abra a tela "LISTAGEM - EXECUÇÕES" da atividade # 67119 (Julho/2026).
 *    (Basta clicar no botão [AE] da coluna 25º 7/2026 na tela de Planejamento).
 * 2. Abra o Console do navegador (pressione F12 e clique na aba "Console").
 * 3. Cole todo este código e aperte [ENTER].
 * 4. O auditor lerá todas as execuções e indicará exatamente quem são os 4 pendentes!
 * ==============================================================================
 */
(async function() {{
    console.clear();
    console.log('%c🚀 AUDITANDO VISITAS TÉCNICAS AVALIATIVAS (JULHO/2026 - 281 REGISTROS COLETUM)...', 'color: #00bcd4; font-size: 16px; font-weight: bold;');

    // 1. Base oficial de dados extraída diretamente do Coletum (Formulário 41981)
    const coletumVisitas = {json_str};

    function normalizar(txt) {{
        if (!txt) return '';
        return String(txt).normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toUpperCase().trim();
    }}

    function cleanCpf(cpf) {{
        if (!cpf) return '';
        return String(cpf).replace(/\\D/g, '');
    }}

    function similaridade(s1, s2) {{
        const n1 = normalizar(s1);
        const n2 = normalizar(s2);
        if (n1 === n2) return 1.0;
        if (!n1 || !n2) return 0.0;
        if (n1.includes(n2) || n2.includes(n1)) return 0.92;
        const p1 = n1.split(' '), p2 = n2.split(' ');
        if (p1.length >= 2 && p2.length >= 2) {{
            if (p1[0] === p2[0] && p1[p1.length - 1] === p2[p2.length - 1]) return 0.88;
        }}
        const set1 = new Set(p1), set2 = new Set(p2);
        const inter = new Set([...set1].filter(x => set2.has(x)));
        return inter.size / new Set([...set1, ...set2]).size;
    }}

    // Remove painel anterior se existir
    const antigo = document.getElementById('painelAuditoriaVisitas7');
    if (antigo) antigo.remove();

    // 2. Identificação das execuções na tela do SIGATER
    const linksLupa = Array.from(document.querySelectorAll('a[href*="/read/"], a[href*="cronograma_execucao/read"], table tbody tr a'));
    const urlsExecucoes = Array.from(new Set(
        linksLupa.map(a => a.href).filter(h => h && (h.includes('/read/') || h.includes('cronograma_execucao/read')))
    ));

    // Se estiver na tela do Cronograma e não na tela de execuções
    if (urlsExecucoes.length === 0) {{
        const divAviso = document.createElement('div');
        divAviso.id = 'painelAuditoriaVisitas7';
        divAviso.style.cssText = 'position:fixed;bottom:20px;right:20px;width:520px;background:#181a20;color:#fff;padding:22px;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:999999;font-family:Segoe UI, sans-serif;font-size:13px;border:2px solid #00bcd4;';
        divAviso.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:10px;margin-bottom:14px;">
                <strong style="color:#00bcd4;font-size:16px;">📌 Tela de Cronograma Detectada</strong>
                <button onclick="document.getElementById('painelAuditoriaVisitas7').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:18px;">✖</button>
            </div>
            <p style="margin:0 0 12px 0;color:#ddd;line-height:1.5;">
                Você está na tela geral de planejamento.<br>
                Para auditar os lançamentos de <strong>Julho/2026 (25º - # 67119)</strong>:
            </p>
            <div style="background:#22252e;padding:12px;border-radius:8px;border-left:4px solid #00e676;margin-bottom:14px;">
                👉 <strong>Clique no botão [AE]</strong> ou no número <strong>277</strong> abaixo da coluna <strong>25º 7/2026</strong> para abrir a lista de execuções.
            </div>
            <p style="color:#aaa;font-size:12px;margin:0 0 14px 0;">
                Assim que a listagem abrir, cole este código novamente no Console (F12)!
            </p>
            <button onclick="document.getElementById('painelAuditoriaVisitas7').remove()" style="width:100%;padding:10px;background:#00bcd4;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;">
                Entendido!
            </button>
        `;
        document.body.appendChild(divAviso);
        return;
    }}

    console.log(`📋 Total de execuções detectadas na página do SIGATER: ${{urlsExecucoes.length}}`);

    // 3. Painel Visual Flutuante de Progresso
    const div = document.createElement('div');
    div.id = 'painelAuditoriaVisitas7';
    div.style.cssText = 'position:fixed;bottom:20px;right:20px;width:600px;max-height:85vh;overflow-y:auto;background:#181a20;color:#fff;padding:22px;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:999999;font-family:Segoe UI, sans-serif;font-size:13px;border:2px solid #00bcd4;';
    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:10px;margin-bottom:12px;">
            <strong style="color:#00bcd4;font-size:16px;">🔍 Auditoria Visitas Avaliativas (Julho/2026)</strong>
            <button onclick="document.getElementById('painelAuditoriaVisitas7').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:18px;">✖</button>
        </div>
        <p id="statusProgresso" style="margin:0;color:#ccc;">Lendo as ${{urlsExecucoes.length}} execuções no SIGATER...</p>
        <div style="width:100%;background:#2a2d36;height:12px;border-radius:6px;margin:12px 0;overflow:hidden;">
            <div id="barraProgresso" style="width:0%;height:100%;background:linear-gradient(90deg, #00bcd4, #00e676);transition:width 0.2s;"></div>
        </div>
    `;
    document.body.appendChild(div);

    // 4. Leitura paralela das páginas de execução
    const sigaterLancados = [];
    const BATCH_SIZE = 15;
    let concluidos = 0;

    for (let i = 0; i < urlsExecucoes.length; i += BATCH_SIZE) {{
        const batch = urlsExecucoes.slice(i, i + BATCH_SIZE);
        await Promise.all(batch.map(async (url) => {{
            try {{
                const resp = await fetch(url);
                if (resp.ok) {{
                    const html = await resp.text();
                    const doc = new DOMParser().parseFromString(html, 'text/html');
                    
                    let nomeBeneficiario = '';
                    let cpfBeneficiario = '';

                    const trsPart = Array.from(doc.querySelectorAll('table tr'));
                    for (const tr of trsPart) {{
                        const texto = tr.innerText || '';
                        if (texto.includes('Dados da DAP') || texto.includes('DAP_MDA') || /\\d{{3}}\\.\\d{{3}}\\.\\d{{3}}-\\d{{2}}/.test(texto)) {{
                            const tds = Array.from(tr.querySelectorAll('td'));
                            tds.forEach(td => {{
                                const t = td.innerText.trim();
                                if (/\\d{{3}}\\.\\d{{3}}\\.\\d{{3}}-\\d{{2}}/.test(t)) {{
                                    cpfBeneficiario = t;
                                }} else if (t.split(' ').length >= 2 && t.length >= 6 && !t.includes('DAP') && !t.includes('SIGATER') && !t.includes('MDA')) {{
                                    nomeBeneficiario = t;
                                }}
                            }});
                        }}
                    }}

                    if (!nomeBeneficiario) {{
                        const pdfLinks = Array.from(doc.querySelectorAll('a[href*=".pdf"], [title*=".pdf"]')).map(a => a.innerText || a.title || '');
                        for (const pdf of pdfLinks) {{
                            const match = pdf.match(/([A-Z_]+)_-_(?:ATESTE|COLETUM)/i);
                            if (match) {{
                                nomeBeneficiario = match[1].replace(/_/g, ' ');
                                break;
                            }}
                        }}
                    }}

                    const codExec = url.match(/\\/read\\/(\\d+)/) ? url.match(/\\/read\\/(\\d+)/)[1] : '';

                    sigaterLancados.push({{
                        codExec,
                        url,
                        nome: nomeBeneficiario || 'Não Identificado',
                        cpf: cpfBeneficiario || '-',
                        htmlBruto: normalizar(html)
                    }});
                }}
            }} catch (err) {{
            }} finally {{
                concluidos++;
                const perc = Math.round((concluidos / urlsExecucoes.length) * 100);
                const elStatus = document.getElementById('statusProgresso');
                const elBarra = document.getElementById('barraProgresso');
                if (elStatus) elStatus.innerText = `Processando: ${{concluidos}} de ${{urlsExecucoes.length}} (${{perc}}%)...`;
                if (elBarra) elBarra.style.width = `${{perc}}%`;
            }}
        }}));
    }}

    // 5. Cruzamento Inteligente: Coletum vs SIGATER
    const lancadosConfirmados = [];
    const pendentesNaoLancados = [];

    coletumVisitas.forEach(col => {{
        const nomeNormCol = normalizar(col.beneficiario);
        const cpfLimpoCol = cleanCpf(col.cpf);

        let achou = false;
        for (const sig of sigaterLancados) {{
            const sigCpfLimpo = cleanCpf(sig.cpf);

            if ((cpfLimpoCol.length >= 8 && sigCpfLimpo.includes(cpfLimpoCol)) ||
                similaridade(col.beneficiario, sig.nome) >= 0.70 ||
                sig.htmlBruto.includes(nomeNormCol)) {{
                achou = true;
                break;
            }}
        }}

        if (achou) {{
            lancadosConfirmados.push(col);
        }} else {{
            pendentesNaoLancados.push(col);
        }}
    }});

    // 6. Agrupamento das pendências por Técnico
    const pendentesPorTecnico = {{}};
    pendentesNaoLancados.forEach(p => {{
        const t = p.tecnico || 'Não Informado';
        if (!pendentesPorTecnico[t]) pendentesPorTecnico[t] = [];
        pendentesPorTecnico[t].push(p);
    }});

    // 7. Exibição Detalhada no Console
    console.log('%c====================================================================', 'color: #888');
    console.log(`%c📊 RESULTADO DA AUDITORIA (VISITAS AVALIATIVAS - JULHO/2026 - ATIVIDADE # 67119):
- Total no Coletum (Julho): %c${{coletumVisitas.length}}%c
- Lançados no SIGATER: %c${{sigaterLancados.length}}%c
- Confirmados: %c${{lancadosConfirmados.length}}%c
- ⚠️ PENDENTES DE LANÇAMENTO: %c${{pendentesNaoLancados.length}}%c`,
        'font-weight: bold; font-size: 14px; color: #fff;',
        'color: #00e676; font-weight: bold;', 'color: #fff;',
        'color: #00bcd4; font-weight: bold;', 'color: #fff;',
        'color: #29b6f6; font-weight: bold;', 'color: #fff;',
        'color: #ff1744; font-weight: bold; font-size: 16px;', 'color: #fff;'
    );
    console.log('%c====================================================================', 'color: #888');

    if (pendentesNaoLancados.length > 0) {{
        console.log(`%c⚠️ LISTA DOS BENEFICIÁRIOS PENDENTES NO SIGATER (${{pendentesNaoLancados.length}}):`, 'color: #ff5252; font-size: 15px; font-weight: bold;');
        console.table(pendentesNaoLancados.map((p, i) => ({{
            '#': i + 1,
            'Beneficiário': p.beneficiario,
            'CPF': p.cpf,
            'Técnico': p.tecnico,
            'Comunidade': p.comunidade,
            'Município': p.municipio,
            'Data': p.data,
            'ID Coletum': p.coletum_id
        }})));
    }} else {{
        console.log('%c🎉 Parabéns! Todas as 281 visitas do Coletum constam como lançadas no SIGATER!', 'color: #00e676; font-size: 16px; font-weight: bold;');
    }}

    // 8. Atualização do Painel Flutuante Final
    window._pendentesVisitasJulho = pendentesNaoLancados;

    div.style.border = pendentesNaoLancados.length > 0 ? '2px solid #ff5252' : '2px solid #00e676';
    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:10px;margin-bottom:12px;">
            <strong style="color:${{pendentesNaoLancados.length > 0 ? '#ff5252' : '#00e676'}};font-size:16px;">
                ${{pendentesNaoLancados.length > 0 ? `⚠️ Faltam ${{pendentesNaoLancados.length}} Visitas Avaliativas no SIGATER` : '✅ 100% das Visitas Lançadas!'}}
            </strong>
            <button onclick="document.getElementById('painelAuditoriaVisitas7').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:18px;">✖</button>
        </div>
        <p style="margin:0 0 10px 0;color:#ccc;">
            Meta Coletum: <strong>${{coletumVisitas.length}}</strong> | Lançados SIGATER: <strong style="color:#00bcd4;">${{sigaterLancados.length}}</strong> | Pendentes: <strong style="color:#ff5252;font-size:15px;">${{pendentesNaoLancados.length}}</strong>
        </p>

        ${{Object.keys(pendentesPorTecnico).length > 0 ? `
            <div style="background:#22252e;padding:12px;border-radius:8px;margin-bottom:12px;">
                <strong style="color:#ffd54f;display:block;margin-bottom:8px;">👤 Pendências por Técnico:</strong>
                ${{Object.keys(pendentesPorTecnico).map(t => `
                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;">
                        <span>👤 ${{t}}</span>
                        <strong style="color:#ff5252;">${{pendentesPorTecnico[t].length}} pendente(s)</strong>
                    </div>
                `).join('')}}
            </div>
        ` : ''}}

        <div style="max-height:320px;overflow-y:auto;padding-right:4px;">
            ${{pendentesNaoLancados.map((p, i) => `
                <div style="background:#22252e;padding:10px 12px;border-radius:6px;margin-bottom:8px;border-left:4px solid #ff5252;">
                    <strong style="color:#fff;font-size:13px;">${{i+1}}. ${{p.beneficiario}}</strong><br>
                    <small style="color:#bbb;">CPF: <span style="color:#00e676;">${{p.cpf}}</span> | ${{p.comunidade}} (${{p.municipio}})</small><br>
                    <small style="color:#ffd54f;">👤 Técnico: ${{p.tecnico}} • 📅 Data: ${{p.data}}</small>
                </div>
            `).join('')}}
        </div>

        ${{pendentesNaoLancados.length > 0 ? `
        <div style="display:flex;gap:10px;margin-top:14px;">
            <button id="btnCopiarPendentesVisitas" style="flex:1;padding:10px;background:#00bcd4;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:13px;">
                📋 Copiar Lista de Pendentes (${{pendentesNaoLancados.length}})
            </button>
            <button id="btnBaixarCsvPendentesVisitas" style="flex:1;padding:10px;background:#00e676;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:13px;">
                📥 Baixar CSV
            </button>
        </div>` : ''}}
    `;

    // Ações dos botões
    if (document.getElementById('btnCopiarPendentesVisitas')) {{
        document.getElementById('btnCopiarPendentesVisitas').onclick = function() {{
            const txt = pendentesNaoLancados.map((p, i) => 
                `${{i+1}}. ${{p.beneficiario}} | CPF: ${{p.cpf}} | Téc: ${{p.tecnico}} | ${{p.comunidade}} (${{p.municipio}}) | Data: ${{p.data}}`
            ).join('\\n');
            navigator.clipboard.writeText(txt).then(() => alert(`Lista dos ${{pendentesNaoLancados.length}} pendentes copiada com sucesso!`));
        }};
    }}

    if (document.getElementById('btnBaixarCsvPendentesVisitas')) {{
        document.getElementById('btnBaixarCsvPendentesVisitas').onclick = function() {{
            let csv = '\\uFEFFNº;Beneficiário;CPF;Técnico;Município;Comunidade;Data Realização;ID Coletum\\n';
            pendentesNaoLancados.forEach((p, i) => {{
                csv += `"${{i+1}}";"${{p.beneficiario}}";"${{p.cpf}}";"${{p.tecnico}}";"${{p.municipio}}";"${{p.comunidade}}";"${{p.data}}";"${{p.coletum_id}}"\\n`;
            }});
            const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'Pendencias_Visitas_Avaliativas_Julho_2026.csv';
            link.click();
        }};
    }}
}})();
"""

    caminho_final = Path('scripts/auditor_visitas_avaliativas_julho_2026.js')
    with open(caminho_final, 'w', encoding='utf-8') as f:
        f.write(js_code)
    print(f'✅ Salvo com sucesso em: {caminho_final}')

    caminho_archive = Path('scripts/archive/auditors_js/auditor_visitas_avaliativas_julho_2026.js')
    with open(caminho_archive, 'w', encoding='utf-8') as f:
        f.write(js_code)
    print(f'✅ Salvo também em: {caminho_archive}')

if __name__ == '__main__':
    gerar()
