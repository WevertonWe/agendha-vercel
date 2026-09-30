"""
Serviço do SIGATER Hub - Automação de Scripts F12, Coletum e Rastreamento de Pendências
Módulo: Bahia Sem Fome (BSF)
"""

import json
import logging
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.core.database import get_db_connection, get_supabase
from app.services.coletum_service import buscar_respostas_formulario

logger = logging.getLogger(__name__)

# Mapeamento de Atividades para seus formulários no Coletum
ATIVIDADES_BSF = {
    "PLANO_PRODUTIVO": {
        "codigo": "PLANO_PRODUTIVO",
        "nome": "Elaboração do Plano Produtivo da UPF",
        "form_id": "37163",
        "somente_sigater": False
    },
    "SOCIOECONOMICO": {
        "codigo": "SOCIOECONOMICO",
        "nome": "Levantamento Socioeconômico e Geolocalização",
        "form_id": "37184",
        "somente_sigater": False
    },
    "CARACTERIZACAO": {
        "codigo": "CARACTERIZACAO",
        "nome": "Caracterização da UPF",
        "form_id": "37205",
        "somente_sigater": False
    },
    "ACOMPANHAMENTO_PLANO": {
        "codigo": "ACOMPANHAMENTO_PLANO",
        "nome": "Acompanhamento Plano Produtivo",
        "form_id": "37226",
        "somente_sigater": False
    },
    "VISITA_AVALIATIVA": {
        "codigo": "VISITA_AVALIATIVA",
        "nome": "Visita Técnica Avaliativa",
        "form_id": "41981",
        "somente_sigater": False
    },
    "VISITA_INDIVIDUAL": {
        "codigo": "VISITA_INDIVIDUAL",
        "nome": "Visita Técnica Individual",
        "form_id": "38513",
        "somente_sigater": False
    },
    "VISITA_SOCIAL": {
        "codigo": "VISITA_SOCIAL",
        "nome": "Visita Social",
        "form_id": "37142",
        "somente_sigater": False
    },
    "CADASTRO_GRUPO_FAMILIAR": {
        "codigo": "CADASTRO_GRUPO_FAMILIAR",
        "nome": "Cadastro do Grupo Familiar",
        "form_id": None,
        "somente_sigater": True
    }
}

MESES_NOMES = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

_CACHE_COLETUM_FORMULARIOS: Dict[str, Dict[str, Any]] = {}
_CACHE_TTL_SEGUNDOS = 600  # 10 minutos


def calcular_competencia_mes_contrato(mes_contrato: int) -> Dict[str, Any]:
    """
    Calcula a competência com base no Mês do Contrato.
    O contrato iniciou em Julho/2024 (Mês 1 = 07/2024).
    """
    if mes_contrato < 1:
        mes_contrato = 1

    total_meses = (7 - 1) + (mes_contrato - 1)
    ano = 2024 + (total_meses // 12)
    mes = (total_meses % 12) + 1
    mes_str = f"{mes:02d}"
    ano_str = str(ano)
    nome_mes = MESES_NOMES[mes]
    ano_contrato = ((mes_contrato - 1) // 12) + 1

    return {
        "mes_contrato": mes_contrato,
        "ano_contrato": ano_contrato,
        "mes": mes,
        "mes_str": mes_str,
        "ano": ano,
        "ano_str": ano_str,
        "nome_mes": nome_mes,
        "mes_ano": f"{mes_str}/{ano_str}",
        "filtro_iso": f"{ano_str}-{mes_str}",
        "label": f"Mês {mes_contrato} ({nome_mes}/{ano_str} - Ano {ano_contrato})"
    }


def extrair_dados_beneficiario_resposta(resp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrai dados (Nome, CPF, Técnico, Data, Comunidade, Município) de resposta do Coletum.
    Suporta campos simples, dicionários com 'label' (ex: 'Nome - CPF') e estruturas aninhadas.
    """
    ans = resp.get("answer", {})
    coletum_id = str(resp.get("id", ""))
    
    nome = ""
    cpf = ""
    data_str = ""
    tecnico = ""
    municipio = ""
    comunidade = ""

    def extrair_de_label(lbl: str):
        nonlocal nome, cpf
        lbl = lbl.strip()
        if not lbl:
            return
        # Formato comum: "NOME DO BENEFICIARIO - 000.000.000-00"
        if " - " in lbl:
            partes = lbl.rsplit(" - ", 1)
            possivel_cpf = partes[1].strip()
            digitos = re.sub(r'\D', '', possivel_cpf)
            if len(digitos) == 11:
                if not cpf:
                    cpf = possivel_cpf
                if not nome and len(partes[0].strip()) > 2:
                    nome = partes[0].strip()
                return
        
        # Se não tem " - ", procura padrão de CPF no texto
        m_cpf = re.search(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', lbl)
        if m_cpf:
            if not cpf:
                cpf = m_cpf.group(0)
            texto_sem_cpf = lbl.replace(m_cpf.group(0), "").replace("-", "").strip()
            if not nome and len(texto_sem_cpf) > 2:
                nome = texto_sem_cpf
        elif not nome and len(lbl) > 2 and not lbl.isdigit():
            nome = lbl

    cpf_tecnico = ""

    def varrer(obj):
        nonlocal nome, cpf, cpf_tecnico, data_str, tecnico, municipio, comunidade
        if isinstance(obj, dict):
            for k, v in obj.items():
                k_lower = str(k).lower()
                
                # Caso especial: objeto com chave 'label' (ex: beneficiario_a866671: {"label": "...", "answer_id": ...})
                if isinstance(v, dict) and "label" in v:
                    extrair_de_label(str(v.get("label", "")))

                # Campo chamado 'label'
                if k_lower == "label" and isinstance(v, str):
                    extrair_de_label(v)

                # Nome do beneficiário
                if not nome and ("nome" in k_lower or "titular" in k_lower or "beneficiario" in k_lower) and "tecnico" not in k_lower:
                    if isinstance(v, str) and len(v.strip()) > 3 and not v.strip().isdigit():
                        nome = v.strip()

                # CPF do técnico
                if not cpf_tecnico and "cpf" in k_lower and "tecnico" in k_lower:
                    if isinstance(v, str) and any(c.isdigit() for c in v):
                        cpf_tecnico = v.strip()

                # CPF do beneficiário
                if not cpf and "cpf" in k_lower and "tecnico" not in k_lower:
                    if isinstance(v, str) and any(c.isdigit() for c in v):
                        cpf = v.strip()

                # Técnico
                if not tecnico and "tecnico" in k_lower and ("nome" in k_lower or "responsavel" in k_lower):
                    if isinstance(v, str) and len(v.strip()) > 2:
                        tecnico = v.strip()

                # Data de realização
                if not data_str and ("data" in k_lower or "realizacao" in k_lower):
                    if isinstance(v, str) and (len(v) >= 8) and ("-" in v or "/" in v):
                        data_str = v.strip()

                # Município
                if not municipio and "municipio" in k_lower:
                    if isinstance(v, str):
                        municipio = v.strip()

                # Comunidade
                if not comunidade and "comunidade" in k_lower:
                    if isinstance(v, str):
                        comunidade = v.strip()

                if isinstance(v, (dict, list)):
                    varrer(v)
        elif isinstance(obj, list):
            for item in obj:
                varrer(item)

    varrer(ans)

    # Se o CPF extraído do beneficiário for idêntico ao CPF do técnico, é repetição indevida
    if cpf and cpf_tecnico:
        c_clean = re.sub(r'\D', '', cpf)
        ct_clean = re.sub(r'\D', '', cpf_tecnico)
        if c_clean and c_clean == ct_clean:
            cpf = ""

    data_formatada = data_str
    if data_str:
        d_clean = data_str.split("T")[0].replace(".", "-").replace("/", "-")
        partes = d_clean.split("-")
        if len(partes) == 3:
            if len(partes[0]) == 4:
                data_formatada = f"{int(partes[2]):02d}/{int(partes[1]):02d}/{partes[0]}"
            elif len(partes[2]) == 4:
                data_formatada = f"{int(partes[0]):02d}/{int(partes[1]):02d}/{partes[2]}"

    if municipio and "-" in municipio:
        partes_m = municipio.split("-")
        if len(partes_m) > 1 and partes_m[-1].strip().isdigit():
            municipio = "-".join(partes_m[:-1]).strip()

    return {
        "coletum_id": coletum_id,
        "beneficiario": nome.upper().strip() if nome else "NÃO INFORMADO",
        "cpf": cpf.strip() if cpf else "",
        "tecnico": tecnico.strip() if tecnico else "NÃO INFORMADO",
        "municipio": municipio.strip() if municipio else "",
        "comunidade": comunidade.strip() if comunidade else "",
        "data": data_formatada,
        "data_raw": data_str
    }


async def carregar_respostas_coletum_com_cache(form_id: str) -> List[Dict[str, Any]]:
    """Carrega respostas de um formulário da API Coletum com cache temporário em memória."""
    agora = datetime.now().timestamp()
    if form_id in _CACHE_COLETUM_FORMULARIOS:
        cached = _CACHE_COLETUM_FORMULARIOS[form_id]
        if agora - cached.get("ts", 0) < _CACHE_TTL_SEGUNDOS:
            return cached.get("dados", [])

    respostas = await buscar_respostas_formulario(form_id, limit=3000)
    _CACHE_COLETUM_FORMULARIOS[form_id] = {
        "dados": respostas,
        "ts": agora
    }
    return respostas


async def obter_beneficiarios_coletum_competencia(
    atividade_codigo: str,
    mes_contrato: int
) -> Dict[str, Any]:
    """
    Busca todas as respostas do Coletum para a atividade e mês selecionados.
    """
    info_ativ = ATIVIDADES_BSF.get(atividade_codigo)
    if not info_ativ:
        raise ValueError(f"Atividade inválida: {atividade_codigo}")

    comp = calcular_competencia_mes_contrato(mes_contrato)
    filtro_iso = comp["filtro_iso"]
    filtro_barra = f"/{comp['mes_str']}/{comp['ano_str']}"
    filtro_ponto = f".{comp['mes_str']}.{comp['ano_str']}"

    form_id = info_ativ.get("form_id")
    if not form_id:
        return {
            "competencia": comp,
            "atividade": info_ativ,
            "total_coletum": 0,
            "beneficiarios": [],
            "mensagem": "Esta atividade é exclusiva do SIGATER (não utiliza formulário no Coletum)."
        }

    respostas_raw = await carregar_respostas_coletum_com_cache(form_id)
    beneficiarios_filtrados = []
    cpfs_vistos = set()
    duplicados_detectados = []
    total_preenchimentos = 0

    for r in respostas_raw:
        item = extrair_dados_beneficiario_resposta(r)
        d_raw = item.get("data_raw", "")
        d_fmt = item.get("data", "")

        pertence = False
        if d_raw and filtro_iso in d_raw:
            pertence = True
        elif d_fmt and (filtro_barra in d_fmt or filtro_ponto in d_fmt):
            pertence = True

        if pertence:
            total_preenchimentos += 1
            cpf_limpo = re.sub(r'\D', '', item.get("cpf", ""))
            if cpf_limpo and len(cpf_limpo) == 11:
                chave = cpf_limpo
            elif item.get("beneficiario") and item.get("beneficiario") != "NÃO INFORMADO":
                chave = item.get("beneficiario")
            else:
                chave = item.get("coletum_id") or str(len(cpfs_vistos))

            if chave not in cpfs_vistos:
                cpfs_vistos.add(chave)
                beneficiarios_filtrados.append(item)
            else:
                duplicados_detectados.append({
                    "coletum_id": item.get("coletum_id"),
                    "beneficiario": item.get("beneficiario"),
                    "cpf": item.get("cpf"),
                    "tecnico": item.get("tecnico"),
                    "data": item.get("data"),
                    "comunidade": item.get("comunidade"),
                    "municipio": item.get("municipio")
                })

    beneficiarios_filtrados.sort(key=lambda x: x["beneficiario"])

    msg = f"Foram localizados {len(beneficiarios_filtrados)} beneficiários únicos"
    if duplicados_detectados:
        msg += f" ({total_preenchimentos} preenchimentos no Coletum - {len(duplicados_detectados)} duplicidade(s) para o mesmo beneficiário)."
    else:
        msg += f" no Coletum para {comp['nome_mes']}/{comp['ano']}."

    return {
        "competencia": comp,
        "atividade": info_ativ,
        "total_coletum": len(beneficiarios_filtrados),
        "total_preenchimentos": total_preenchimentos,
        "duplicados": duplicados_detectados,
        "beneficiarios": beneficiarios_filtrados,
        "mensagem": msg
    }


def gerar_script_f12_dinamico(
    atividade_codigo: str,
    mes_contrato: int,
    beneficiarios: List[Dict[str, Any]],
    duplicados: Optional[List[Dict[str, Any]]] = None,
    total_preenchimentos: Optional[int] = None
) -> str:
    """
    Gera o código JavaScript otimizado para colar no Console do Navegador (F12) no portal SIGATER.
    """
    info_ativ = ATIVIDADES_BSF.get(atividade_codigo, {})
    comp = calcular_competencia_mes_contrato(mes_contrato)
    nome_ativ = info_ativ.get("nome", atividade_codigo)
    
    dados_json = json.dumps(beneficiarios, ensure_ascii=False, indent=2)

    aviso_dupl_js = ""
    if duplicados:
        aviso_dupl_js = f"console.log('%cℹ️ Nota: {total_preenchimentos or len(beneficiarios)} formulários no Coletum -> {len(beneficiarios)} beneficiários únicos ({len(duplicados)} duplicidade(s) para a mesma pessoa).', 'color: #ffb74d; font-size: 13px;');"

    script = f"""/**
 * ==============================================================================
 * 🔍 AUDITOR AUTOMÁTICO SIGATER vs COLETUM - AGENDHA
 * Atividade: {nome_ativ}
 * Competência: {comp['label']} (Mês {mes_contrato})
 * Total no Coletum: {len(beneficiarios)} beneficiários únicos
 * ==============================================================================
 * Como usar:
 * 1. No SIGATER, abra a tela "LISTAGEM - EXECUÇÕES" da atividade correspondente.
 * 2. Abra o Console do Navegador (F12 -> Console).
 * 3. Cole este código completo e pressione [ENTER].
 * ==============================================================================
 */
(async function() {{
    console.clear();
    console.log('%c🚀 INICIANDO AUDITORIA: {nome_ativ} ({comp["mes_ano"]})...', 'color: #00bcd4; font-size: 16px; font-weight: bold;');
    {aviso_dupl_js}

    const coletumBase = {dados_json};

    function normalizar(txt) {{
        if (!txt) return '';
        return txt.toString()
            .normalize('NFD')
            .replace(/[\\u0300-\\u036f]/g, '')
            .replace(/[^a-zA-Z0-9\\s]/g, ' ')
            .toUpperCase()
            .replace(/\\s+/g, ' ')
            .trim();
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

    const antigo = document.getElementById('painelAuditoriaAgendha');
    if (antigo) antigo.remove();

    const linksLupa = Array.from(document.querySelectorAll('a[href*="/read/"], a[href*="cronograma_execucao/read"], table tbody tr a'));
    const urlsExecucoes = Array.from(new Set(
        linksLupa.map(a => a.href).filter(h => h && (h.includes('/read/') || h.includes('cronograma_execucao/read')))
    ));

    console.log(`📋 Total de execuções identificadas no SIGATER: ${{urlsExecucoes.length}}`);

    const div = document.createElement('div');
    div.id = 'painelAuditoriaAgendha';
    div.style.cssText = 'position:fixed;bottom:20px;right:20px;width:550px;max-height:85vh;overflow-y:auto;background:#151821;color:#fff;padding:20px;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,0.85);z-index:999999;font-family:Segoe UI,Roboto,sans-serif;font-size:13px;border:2px solid #00bcd4;';
    div.innerHTML = `
        <div style="border-bottom:1px solid #333;padding-bottom:8px;margin-bottom:12px;">
            <strong style="color:#00bcd4;font-size:15px;">⏳ Lendo ${{urlsExecucoes.length}} Execuções no SIGATER...</strong>
        </div>
        <p id="statusProgressoAgendha" style="margin:0;color:#ccc;">Aguarde a varredura das páginas...</p>
        <div style="width:100%;background:#222;height:10px;border-radius:5px;margin-top:10px;overflow:hidden;">
            <div id="barraProgressoAgendha" style="width:0%;height:100%;background:#00bcd4;transition:width 0.2s;"></div>
        </div>
    `;
    document.body.appendChild(div);

    const sigaterLancados = [];

    if (urlsExecucoes.length === 0) {{
        console.log('⚠️ Nenhuma URL /read/ encontrada. Verificando dados na tabela visível...');
        const trs = Array.from(document.querySelectorAll('table tbody tr'));
        trs.forEach(tr => {{
            const txt = tr.innerText || '';
            const cpfMatch = txt.match(/\\d{{3}}\\.\\d{{3}}\\.\\d{{3}}-\\d{{2}}/) || txt.match(/\\d{{11}}/);
            sigaterLancados.push({{
                nome: txt,
                cpf: cpfMatch ? cpfMatch[0] : '',
                htmlBruto: normalizar(txt)
            }});
        }});
    }} else {{
        const BATCH_SIZE = 12;
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
                        let dataExecucao = '';
                        let tecnicoNome = '';
                        let comunidadeNome = '';
                        let municipioNome = '';

                        const MUNICIPIOS_SISTEMA = ['PAULO AFONSO', 'GLORIA', 'CANUDOS', 'UAUA', 'SANTA BRIGIDA', 'CHORROCHO', 'RODELAS', 'MACURURE', 'ABARE', 'JEREMOABO', 'PEDRO ALEXANDRE', 'ESTADO DA BAHIA', 'SECRETARIA', 'TERMO DE COLABORACAO', 'BAHIA SEM FOME', 'ASSENTAMENTO', 'COMUNIDADE'];

                        function isNomeValido(str) {{
                            if (!str || typeof str !== 'string') return false;
                            const n = normalizar(str);
                            if (n.length < 4 || n.split(' ').length < 2) return false;
                            if (MUNICIPIOS_SISTEMA.some(m => n === m || n.startsWith(m + ' ') || n.endsWith(' ' + m))) return false;
                            if (n.includes('DAP') || n.includes('SIGATER') || n.includes('MDA') || n.includes('SISTEMA') || n.includes('EXECUCAO')) return false;
                            return true;
                        }}

                        const trsPart = Array.from(doc.querySelectorAll('table tr'));
                        for (const tr of trsPart) {{
                            const texto = tr.innerText || '';
                            
                            // 1. Prioridade: Procura campos explícitos de Beneficiário / Titular
                            if (!nomeBeneficiario || !isNomeValido(nomeBeneficiario)) {{
                                if (/beneficiário|titular|produtor|público alvo/i.test(texto)) {{
                                    const tds = Array.from(tr.querySelectorAll('td, th'));
                                    tds.forEach(td => {{
                                        const t = td.innerText.trim();
                                        if (isNomeValido(t) && !/beneficiário|titular|produtor|público/i.test(t)) {{
                                            nomeBeneficiario = t;
                                        }}
                                    }});
                                }}
                            }}

                            // 2. DAP / CPF
                            if (texto.includes('Dados da DAP') || texto.includes('DAP_MDA') || /\\d{{3}}\\.\\d{{3}}\\.\\d{{3}}-\\d{{2}}/.test(texto)) {{
                                const tds = Array.from(tr.querySelectorAll('td'));
                                tds.forEach(td => {{
                                    const t = td.innerText.trim();
                                    if (/\\d{{3}}\\.\\d{{3}}\\.\\d{{3}}-\\d{{2}}/.test(t)) {{
                                        cpfBeneficiario = t;
                                    }} else if ((!nomeBeneficiario || !isNomeValido(nomeBeneficiario)) && isNomeValido(t)) {{
                                        nomeBeneficiario = t;
                                    }}
                                }});
                            }}

                            if (!dataExecucao && (/data/i.test(texto) || /realiza/i.test(texto))) {{
                                const mData = texto.match(/\\d{{2}}\\/\\d{{2}}\\/\\d{{4}}/) || texto.match(/\\d{{4}}-\\d{{2}}-\\d{{2}}/);
                                if (mData) dataExecucao = mData[0];
                            }}

                            if (!tecnicoNome && (/técnico/i.test(texto) || /responsável/i.test(texto) || /executor/i.test(texto))) {{
                                const tds = Array.from(tr.querySelectorAll('td'));
                                tds.forEach(td => {{
                                    const t = td.innerText.trim();
                                    if (t.split(' ').length >= 2 && !t.includes('Técnico') && !t.includes('Responsável') && t.length > 3 && !MUNICIPIOS_SISTEMA.some(m => normalizar(t) === m)) {{
                                        tecnicoNome = t;
                                    }}
                                }});
                            }}

                            if (!municipioNome && /município|cidade/i.test(texto)) {{
                                const tds = Array.from(tr.querySelectorAll('td'));
                                tds.forEach(td => {{
                                    const t = td.innerText.trim();
                                    if (t && !/município|cidade/i.test(t) && t.length > 2) {{
                                        municipioNome = t;
                                    }}
                                }});
                            }}
                        }}

                        if (!nomeBeneficiario || !isNomeValido(nomeBeneficiario)) {{
                            const pdfLinks = Array.from(doc.querySelectorAll('a[href*=".pdf"], [title*=".pdf"]')).map(a => a.innerText || a.title || '');
                            for (const pdf of pdfLinks) {{
                                const match = pdf.match(/([A-Z_]+)_-_(?:ATESTE|COLETUM)/i);
                                if (match) {{
                                    const possivelNome = match[1].replace(/_/g, ' ').trim();
                                    if (isNomeValido(possivelNome)) {{
                                        nomeBeneficiario = possivelNome;
                                        break;
                                    }}
                                }}
                            }}
                        }}

                        // Extrai todos os CPFs do documento para match preciso
                        const allCpfs = Array.from(new Set(
                            ((doc.body ? doc.body.innerText : html).match(/\\b\\d{{3}}\\.\\d{{3}}\\.\\d{{3}}-\\d{{2}}\\b/g) || []).map(cleanCpf)
                        ));

                        const codExec = url.match(/\\/read\\/(\\d+)/) ? url.match(/\\/read\\/(\\d+)/)[1] : '';

                        sigaterLancados.push({{
                            codExec,
                            url,
                            nome: nomeBeneficiario || 'Não Identificado',
                            cpf: cpfBeneficiario || (allCpfs.length > 0 ? allCpfs[0] : '-'),
                            cpfs: allCpfs,
                            data: dataExecucao,
                            tecnico: tecnicoNome,
                            comunidade: comunidadeNome,
                            municipio: municipioNome,
                            htmlBruto: normalizar(html)
                        }});
                    }}
                }} catch (err) {{
                    console.warn(err);
                }} finally {{
                    concluidos++;
                    const perc = Math.round((concluidos / urlsExecucoes.length) * 100);
                    const elStatus = document.getElementById('statusProgressoAgendha');
                    const elBarra = document.getElementById('barraProgressoAgendha');
                    if (elStatus) elStatus.innerText = `Processando: ${{concluidos}} de ${{urlsExecucoes.length}} (${{perc}}%)...`;
                    if (elBarra) elBarra.style.width = `${{perc}}%`;
                }}
            }}));
        }}
    }}

    // Mapeamento exclusivo 1-para-1 (cada execução no SIGATER só confirma 1 beneficiário no Coletum)
    const sigaterUsados = new Set();
    const lancadosConfirmados = [];
    const pendentesNaoLancados = [];

    // PASSAGEM 1: Correspondência Exata por CPF (1-para-1)
    coletumBase.forEach(col => {{
        col._confirmado = false;
        const cpfCol = cleanCpf(col.cpf);
        if (cpfCol.length === 11) {{
            for (let i = 0; i < sigaterLancados.length; i++) {{
                if (sigaterUsados.has(i)) continue;
                const sig = sigaterLancados[i];
                const sigCpf = cleanCpf(sig.cpf);
                if (sigCpf === cpfCol || (sig.cpfs && sig.cpfs.includes(cpfCol))) {{
                    sigaterUsados.add(i);
                    col._confirmado = true;
                    col._matchTipo = 'CPF_EXATO';
                    col._matchExec = sig.codExec;
                    col._matchUrl = sig.url;
                    lancadosConfirmados.push(col);
                    break;
                }}
            }}
        }}
    }});

    // PASSAGEM 2: Correspondência Exata por Nome Normalizado (1-para-1, sem conflito de CPF)
    coletumBase.forEach(col => {{
        if (col._confirmado) return;
        const nomeColNorm = normalizar(col.beneficiario);
        const cpfCol = cleanCpf(col.cpf);

        for (let i = 0; i < sigaterLancados.length; i++) {{
            if (sigaterUsados.has(i)) continue;
            const sig = sigaterLancados[i];
            const sigCpf = cleanCpf(sig.cpf);

            // Bloqueia se ambos possuem CPFs válidos de 11 dígitos porém distintos
            if (cpfCol.length === 11 && sigCpf.length === 11 && cpfCol !== sigCpf) {{
                continue;
            }}

            const nomeSigNorm = normalizar(sig.nome);
            if (nomeColNorm && nomeSigNorm && nomeColNorm === nomeSigNorm) {{
                sigaterUsados.add(i);
                col._confirmado = true;
                col._matchTipo = 'NOME_EXATO';
                col._matchExec = sig.codExec;
                col._matchUrl = sig.url;
                lancadosConfirmados.push(col);
                break;
            }}
        }}
    }});

    // PASSAGEM 3: Correspondência por Alta Similaridade (>= 0.88, 1-para-1, sem conflito de CPF)
    coletumBase.forEach(col => {{
        if (col._confirmado) return;
        const cpfCol = cleanCpf(col.cpf);
        let melhorIdx = -1;
        let maiorScore = 0;

        for (let i = 0; i < sigaterLancados.length; i++) {{
            if (sigaterUsados.has(i)) continue;
            const sig = sigaterLancados[i];
            const sigCpf = cleanCpf(sig.cpf);

            if (cpfCol.length === 11 && sigCpf.length === 11 && cpfCol !== sigCpf) {{
                continue;
            }}

            const score = similaridade(col.beneficiario, sig.nome);
            if (score >= 0.88 && score > maiorScore) {{
                maiorScore = score;
                melhorIdx = i;
            }}
        }}

        if (melhorIdx !== -1) {{
            sigaterUsados.add(melhorIdx);
            col._confirmado = true;
            col._matchTipo = `SIMILARIDADE_${{Math.round(maiorScore * 100)}}%`;
            col._matchExec = sigaterLancados[melhorIdx].codExec;
            col._matchUrl = sigaterLancados[melhorIdx].url;
            lancadosConfirmados.push(col);
        }} else {{
            pendentesNaoLancados.push(col);
        }}
    }});

    // Identifica execuções no SIGATER que não foram pareadas com ninguém do Coletum deste mês
    const sigaterSobrando = [];
    for (let i = 0; i < sigaterLancados.length; i++) {{
        if (!sigaterUsados.has(i)) {{
            sigaterSobrando.push(sigaterLancados[i]);
        }}
    }}

    // Formata os confirmados/lançados com seus respectivos Códigos SIGATER
    const lancadosFormatados = lancadosConfirmados.map(c => ({{
        beneficiario: c.beneficiario,
        cpf: c.cpf,
        tecnico: c.tecnico,
        comunidade: c.comunidade,
        municipio: c.municipio,
        data: c.data,
        codigo_sigater: c._matchExec || '',
        link_sigater: c._matchUrl || '',
        match_tipo: c._matchTipo || 'CONFIRMADO_SIGATER',
        status: 'LANCADO'
    }}));

    // Formata os registros do SIGATER sem par no Coletum
    const apenasSigaterFormatados = sigaterSobrando.map(s => ({{
        beneficiario: s.nome,
        cpf: s.cpf && s.cpf !== '-' ? s.cpf : (s.cpfs && s.cpfs.length > 0 ? s.cpfs[0] : ''),
        tecnico: s.tecnico || 'SIGATER (Sem Coletum)',
        comunidade: s.comunidade || '',
        municipio: s.municipio || '',
        data: s.data || '',
        codigo_sigater: s.codExec || '',
        link_sigater: s.url || '',
        status: 'SEM_COLETUM',
        match_tipo: 'APENAS_SIGATER',
        observacoes: 'Lançado no SIGATER, porém sem formulário correspondente no Coletum para este mês.'
    }}));

    window.__auditoriaSigater = {{
        coletumBase,
        sigaterLancados,
        lancadosConfirmados: lancadosFormatados,
        pendentesNaoLancados,
        sigaterSobrando: apenasSigaterFormatados,
        apenasSigater: apenasSigaterFormatados
    }};

    console.log('%c====================================================================', 'color: #888');
    console.log(`%c📊 AUDITORIA SIGATER: {nome_ativ} ({comp["mes_ano"]} - MÊS {mes_contrato})
- Meta no Coletum: %c${{coletumBase.length}}%c
- Lançados no SIGATER: %c${{sigaterLancados.length}}%c
- Confirmados com Código: %c${{lancadosFormatados.length}}%c
- ⚠️ FALTAM LANÇAR (COLETUM): %c${{pendentesNaoLancados.length}}%c
- ⚠️ APENAS NO SIGATER (SEM COLETUM): %c${{apenasSigaterFormatados.length}}%c`,
        'font-weight: bold; font-size: 14px; color: #fff;',
        'color: #00e676; font-weight: bold;', 'color: #fff;',
        'color: #00bcd4; font-weight: bold;', 'color: #fff;',
        'color: #29b6f6; font-weight: bold;', 'color: #fff;',
        'color: #ff1744; font-weight: bold; font-size: 15px;', 'color: #fff;',
        'color: #ff9800; font-weight: bold; font-size: 15px;', 'color: #fff;'
    );
    console.log('%c====================================================================', 'color: #888');

    if (lancadosFormatados.length > 0) {{
        console.log(`%c✅ BENEFICIÁRIOS LANÇADOS NO SIGATER COM CÓDIGO (${{lancadosFormatados.length}}):`, 'color: #00e676; font-size: 14px; font-weight: bold;');
        console.table(lancadosFormatados.map((l, i) => ({{
            '#': i + 1,
            'Código SIGATER': l.codigo_sigater ? `#${{l.codigo_sigater}}` : '-',
            'Beneficiário': l.beneficiario,
            'CPF': l.cpf,
            'Técnico': l.tecnico,
            'Data': l.data,
            'Match': l.match_tipo
        }})));
    }}

    if (pendentesNaoLancados.length > 0) {{
        console.log(`%c⚠️ BENEFICIÁRIOS PENDENTES NO SIGATER (${{pendentesNaoLancados.length}}):`, 'color: #ff5252; font-size: 14px; font-weight: bold;');
        console.table(pendentesNaoLancados.map((p, i) => ({{
            '#': i + 1,
            'Beneficiário': p.beneficiario,
            'CPF': p.cpf,
            'Técnico': p.tecnico,
            'Comunidade': p.comunidade,
            'Município': p.municipio,
            'Data': p.data
        }})));
    }}

    if (apenasSigaterFormatados.length > 0) {{
        console.log(`%c⚠️ LANÇAMENTOS NO SIGATER SEM PAR NO COLETUM (${{apenasSigaterFormatados.length}}):`, 'color: #ff9800; font-size: 13px; font-weight: bold;');
        console.table(apenasSigaterFormatados.map((s, i) => ({{
            '#': i + 1,
            'Cód Execução': s.codigo_sigater ? `#${{s.codigo_sigater}}` : '-',
            'Nome no SIGATER': s.beneficiario,
            'CPF': s.cpf,
            'Link': s.link_sigater
        }})));
    }}

    const temAlerta = pendentesNaoLancados.length > 0 || apenasSigaterFormatados.length > 0;
    div.style.border = `2px solid ${{temAlerta ? '#ff9800' : '#00e676'}}`;
    div.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #333;padding-bottom:8px;margin-bottom:12px;">
            <div>
                <strong style="color:${{pendentesNaoLancados.length > 0 ? '#ff5252' : (apenasSigaterFormatados.length > 0 ? '#ff9800' : '#00e676')}};font-size:15px;">
                    ${{pendentesNaoLancados.length > 0 ? `⚠️ Faltam ${{pendentesNaoLancados.length}} para Lançar` : (apenasSigaterFormatados.length > 0 ? `⚠️ ${{apenasSigaterFormatados.length}} sem par no Coletum` : '✅ Meta 100% Batida!')}}
                </strong>
                <div style="font-size:11px;color:#aaa;margin-top:2px;">
                    Lançados com Código: <span style="color:#00e676;font-weight:bold;">${{lancadosFormatados.length}}</span> / ${{coletumBase.length}}
                    ${{apenasSigaterFormatados.length > 0 ? ` | <span style="color:#ff9800;font-weight:bold;">+${{apenasSigaterFormatados.length}} apenas no SIGATER</span>` : ''}}
                </div>
            </div>
            <button onclick="document.getElementById('painelAuditoriaAgendha').remove()" style="background:none;border:none;color:#aaa;cursor:pointer;font-size:16px;">✖</button>
        </div>
        
        <div style="max-height:280px;overflow-y:auto;">
            ${{lancadosFormatados.length > 0 ? `
                <div style="margin-bottom:10px;">
                    <strong style="color:#00e676;font-size:12px;">✅ Lançados com Código SIGATER (${{lancadosFormatados.length}}):</strong>
                    ${{lancadosFormatados.slice(0, 4).map(l => `
                        <div style="background:#1a2e22;padding:6px 8px;border-radius:4px;margin-top:4px;border-left:3px solid #00e676;font-size:12px;">
                            <strong>${{l.beneficiario}}</strong> 
                            <span style="background:#00e676;color:#000;padding:1px 5px;border-radius:3px;font-size:11px;font-weight:bold;margin-left:5px;">#${{l.codigo_sigater || 'S/N'}}</span>
                        </div>
                    `).join('')}}
                    ${{lancadosFormatados.length > 4 ? `<small style="color:#888;display:block;margin-top:4px;">... e mais ${{lancadosFormatados.length - 4}} lançados</small>` : ''}}
                </div>
            ` : ''}}

            ${{pendentesNaoLancados.length > 0 ? `
                <div style="margin-top:10px;">
                    <strong style="color:#ff5252;font-size:12px;">⚠️ Pendentes a Lançar (${{pendentesNaoLancados.length}}):</strong>
                    ${{pendentesNaoLancados.map((p, i) => `
                        <div style="background:#22252e;padding:8px;border-radius:4px;margin-top:4px;border-left:3px solid #ff5252;font-size:12px;">
                            <strong>${{i+1}}. ${{p.beneficiario}}</strong><br>
                            <small style="color:#bbb;">CPF: ${{p.cpf}} | ${{p.comunidade}} (${{p.municipio}})</small>
                        </div>
                    `).join('')}}
                </div>
            ` : ''}}

            ${{apenasSigaterFormatados.length > 0 ? `
                <div style="margin-top:10px;">
                    <strong style="color:#ff9800;font-size:12px;">⚠️ Lançados no SIGATER sem par no Coletum (${{apenasSigaterFormatados.length}}):</strong>
                    ${{apenasSigaterFormatados.map((s, i) => `
                        <div style="background:#2b2014;padding:8px;border-radius:4px;margin-top:4px;border-left:3px solid #ff9800;font-size:12px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <strong>${{i+1}}. ${{s.beneficiario}}</strong>
                                <span style="background:#ff9800;color:#000;padding:1px 5px;border-radius:3px;font-size:11px;font-weight:bold;">#${{s.codigo_sigater || 'S/N'}}</span>
                            </div>
                            <small style="color:#ffb74d;">CPF: ${{s.cpf || 'Não informado'}} | <span style="color:#bbb;">Apenas no SIGATER</span></small>
                        </div>
                    `).join('')}}
                </div>
            ` : ''}}
        </div>

        <div style="display:flex;flex-direction:column;gap:6px;margin-top:12px;">
            <button id="btnCopiarTudoAgendha" style="padding:10px;background:#00e676;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:12px;">
                📦 Copiar Todos (Lançados + Códigos + Pendentes + Divergências) para o Agendha
            </button>
            <div style="display:flex;gap:6px;">
                <button id="btnCopiarLancados" style="flex:1;padding:8px;background:#00bcd4;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:11px;">
                    📋 Lançados (${{lancadosFormatados.length}})
                </button>
                <button id="btnCopiarPendentes" style="flex:1;padding:8px;background:#ff5252;color:#fff;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:11px;">
                    ⚠️ Pendentes (${{pendentesNaoLancados.length}})
                </button>
                ${{apenasSigaterFormatados.length > 0 ? `
                    <button id="btnCopiarApenasSigater" style="flex:1;padding:8px;background:#ff9800;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:11px;">
                        ⚠️ Sem Coletum (${{apenasSigaterFormatados.length}})
                    </button>
                ` : ''}}
            </div>
        </div>
    `;

    document.getElementById('btnCopiarTudoAgendha').onclick = function() {{
        const payload = JSON.stringify({{
            mes_contrato: {mes_contrato},
            atividade_codigo: "{atividade_codigo}",
            atividade_nome: "{nome_ativ}",
            competencia: "{comp['mes_ano']}",
            lancados: lancadosFormatados,
            pendentes: pendentesNaoLancados,
            apenas_sigater: apenasSigaterFormatados
        }}, null, 2);
        navigator.clipboard.writeText(payload).then(() => {{
            alert(`✅ Auditoria Completa Copiada!\\n${{lancadosFormatados.length}} lançados com código, ${{pendentesNaoLancados.length}} pendentes e ${{apenasSigaterFormatados.length}} apenas no SIGATER.\\nCole no Agendha em 'Registrar Retorno / Lançamentos'.`);
        }});
    }};

    document.getElementById('btnCopiarLancados').onclick = function() {{
        const txt = lancadosFormatados.map((l, i) => `${{i+1}}. ${{l.beneficiario}} | CPF: ${{l.cpf}} | Código SIGATER: ${{l.codigo_sigater}} | Técnico: ${{l.tecnico}} - ${{l.comunidade}} (${{l.municipio}}) - Data: ${{l.data}} | Status: LANCADO`).join('\\n');
        navigator.clipboard.writeText(txt).then(() => {{
            alert(`Lista dos ${{lancadosFormatados.length}} beneficiários lançados copiada!`);
        }});
    }};

    document.getElementById('btnCopiarPendentes').onclick = function() {{
        const txt = pendentesNaoLancados.map((p, i) => `${{i+1}}. ${{p.beneficiario}} | CPF: ${{p.cpf}} | Técnico: ${{p.tecnico}} - ${{p.comunidade}} (${{p.municipio}}) - Data: ${{p.data}} | Status: PENDENTE`).join('\\n');
        navigator.clipboard.writeText(txt).then(() => {{
            alert(`Lista dos ${{pendentesNaoLancados.length}} pendentes copiada!`);
        }});
    }};

    const btnSemCol = document.getElementById('btnCopiarApenasSigater');
    if (btnSemCol) {{
        btnSemCol.onclick = function() {{
            const txt = apenasSigaterFormatados.map((s, i) => `${{i+1}}. ${{s.beneficiario}} | CPF: ${{s.cpf}} | Código SIGATER: ${{s.codigo_sigater}} | Status: SEM_COLETUM`).join('\\n');
            navigator.clipboard.writeText(txt).then(() => {{
                alert(`Lista dos ${{apenasSigaterFormatados.length}} lançamentos sem Coletum copiada!`);
            }});
        }};
    }}
}})();
"""
    return script


def _is_postgres(conn) -> bool:
    """Verifica se a conexão ativa é PostgreSQL/psycopg2 ou SQLite local."""
    return conn.__class__.__name__ not in ('AuditConnection', 'Connection', 'sqlite3.Connection')


def _exec_sql(conn, query: str, params: tuple = ()):
    """Executa query SQL adaptando placeholders ('?' para SQLite e '%s' para PostgreSQL)."""
    cursor = conn.cursor()
    if _is_postgres(conn):
        query = query.replace('?', '%s')
    cursor.execute(query, params)
    return cursor


def _garantir_tabela_pendencias(conn):
    """Garante a criação e evolução da tabela de pendências/lançamentos tanto no PostgreSQL quanto no SQLite."""
    cursor = conn.cursor()
    try:
        if _is_postgres(conn):
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bsf_sigater_pendencias (
                    id SERIAL PRIMARY KEY,
                    mes_contrato INTEGER NOT NULL,
                    mes_ano_referencia TEXT NOT NULL,
                    atividade_nome TEXT NOT NULL,
                    beneficiario_nome TEXT NOT NULL,
                    beneficiario_cpf TEXT,
                    tecnico TEXT,
                    comunidade TEXT,
                    municipio TEXT,
                    data_execucao TEXT,
                    status TEXT DEFAULT 'PENDENTE',
                    codigo_sigater TEXT,
                    link_sigater TEXT,
                    match_tipo TEXT,
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            for col in ["codigo_sigater", "link_sigater", "match_tipo", "observacoes"]:
                try:
                    cursor.execute(f"ALTER TABLE bsf_sigater_pendencias ADD COLUMN IF NOT EXISTS {col} TEXT;")
                except Exception:
                    pass
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bsf_sigater_pendencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mes_contrato INTEGER NOT NULL,
                    mes_ano_referencia TEXT NOT NULL,
                    atividade_nome TEXT NOT NULL,
                    beneficiario_nome TEXT NOT NULL,
                    beneficiario_cpf TEXT,
                    tecnico TEXT,
                    comunidade TEXT,
                    municipio TEXT,
                    data_execucao TEXT,
                    status TEXT DEFAULT 'PENDENTE',
                    codigo_sigater TEXT,
                    link_sigater TEXT,
                    match_tipo TEXT,
                    observacoes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("PRAGMA table_info(bsf_sigater_pendencias);")
            cols_existentes = [row[1] for row in cursor.fetchall()]
            for col in ["codigo_sigater", "link_sigater", "match_tipo", "observacoes"]:
                if col not in cols_existentes:
                    try:
                        cursor.execute(f"ALTER TABLE bsf_sigater_pendencias ADD COLUMN {col} TEXT;")
                    except Exception:
                        pass
        conn.commit()
    except Exception as e:
        logger.warning(f"Aviso ao verificar tabela bsf_sigater_pendencias: {e}")
        conn.rollback()


def salvar_pendencias_no_banco(
    mes_contrato: int,
    mes_ano_referencia: str,
    atividade_nome: str,
    pendentes: Optional[List[Dict[str, Any]]] = None,
    lancados: Optional[List[Dict[str, Any]]] = None,
    apenas_sigater: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Grava ou atualiza a lista de beneficiários lançados, pendentes e lançados sem Coletum no banco de dados.
    """
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    total_salvos = 0
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        _garantir_tabela_pendencias(conn)
        
        # 1. Processa Lançados / Confirmados com Códigos SIGATER (com par no Coletum)
        if lancados:
            for l in lancados:
                nome = str(l.get("beneficiario") or l.get("nome", "")).strip().upper()
                cpf = str(l.get("cpf", "")).strip()
                tecnico = str(l.get("tecnico", "")).strip()
                comunidade = str(l.get("comunidade", "")).strip()
                municipio = str(l.get("municipio", "")).strip()
                data_execucao = str(l.get("data", "") or l.get("data_execucao", "")).strip()
                codigo_sigater = str(l.get("codigo_sigater") or l.get("codExec") or l.get("cod_exec") or "").strip()
                link_sigater = str(l.get("link_sigater") or l.get("url") or "").strip()
                match_tipo = str(l.get("match_tipo") or l.get("_matchTipo") or "CONFIRMADO_SIGATER").strip()

                if not nome:
                    continue

                cursor = _exec_sql(conn, """
                    SELECT id FROM bsf_sigater_pendencias
                    WHERE mes_contrato = ? AND atividade_nome = ? AND beneficiario_nome = ?
                """, (mes_contrato, atividade_nome, nome))
                row = cursor.fetchone()

                if row:
                    reg_id = row["id"] if isinstance(row, dict) or hasattr(row, "__getitem__") else row[0]
                    _exec_sql(conn, """
                        UPDATE bsf_sigater_pendencias
                        SET beneficiario_cpf = CASE WHEN ? != '' THEN ? ELSE beneficiario_cpf END,
                            tecnico = CASE WHEN ? != '' THEN ? ELSE tecnico END,
                            comunidade = CASE WHEN ? != '' THEN ? ELSE comunidade END,
                            municipio = CASE WHEN ? != '' THEN ? ELSE municipio END,
                            data_execucao = CASE WHEN ? != '' THEN ? ELSE data_execucao END,
                            status = 'LANCADO',
                            codigo_sigater = ?,
                            link_sigater = ?,
                            match_tipo = ?,
                            updated_at = ?
                        WHERE id = ?
                    """, (cpf, cpf, tecnico, tecnico, comunidade, comunidade, municipio, municipio, data_execucao, data_execucao, codigo_sigater, link_sigater, match_tipo, agora, reg_id))
                else:
                    _exec_sql(conn, """
                        INSERT INTO bsf_sigater_pendencias (
                            mes_contrato, mes_ano_referencia, atividade_nome,
                            beneficiario_nome, beneficiario_cpf, tecnico,
                            comunidade, municipio, data_execucao, status,
                            codigo_sigater, link_sigater, match_tipo,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'LANCADO', ?, ?, ?, ?, ?)
                    """, (
                        mes_contrato, mes_ano_referencia, atividade_nome,
                        nome, cpf, tecnico, comunidade, municipio, data_execucao,
                        codigo_sigater, link_sigater, match_tipo,
                        agora, agora
                    ))
                total_salvos += 1

        # 2. Processa Pendentes (estão no Coletum, mas ainda não lançados no SIGATER)
        if pendentes:
            for p in pendentes:
                nome = str(p.get("beneficiario") or p.get("nome", "")).strip().upper()
                cpf = str(p.get("cpf", "")).strip()
                tecnico = str(p.get("tecnico", "")).strip()
                comunidade = str(p.get("comunidade", "")).strip()
                municipio = str(p.get("municipio", "")).strip()
                data_execucao = str(p.get("data", "") or p.get("data_execucao", "")).strip()
                codigo_sigater = str(p.get("codigo_sigater") or p.get("codExec") or p.get("cod_exec") or "").strip()

                if not nome:
                    continue

                cursor = _exec_sql(conn, """
                    SELECT id, status FROM bsf_sigater_pendencias
                    WHERE mes_contrato = ? AND atividade_nome = ? AND beneficiario_nome = ?
                """, (mes_contrato, atividade_nome, nome))
                row = cursor.fetchone()

                if row:
                    reg_id = row["id"] if isinstance(row, dict) or hasattr(row, "__getitem__") else row[0]
                    # Se for pendente, atualiza dados
                    _exec_sql(conn, """
                        UPDATE bsf_sigater_pendencias
                        SET beneficiario_cpf = CASE WHEN ? != '' THEN ? ELSE beneficiario_cpf END,
                            tecnico = CASE WHEN ? != '' THEN ? ELSE tecnico END,
                            comunidade = CASE WHEN ? != '' THEN ? ELSE comunidade END,
                            municipio = CASE WHEN ? != '' THEN ? ELSE municipio END,
                            data_execucao = CASE WHEN ? != '' THEN ? ELSE data_execucao END,
                            status = CASE WHEN status = 'LANCADO' THEN status ELSE 'PENDENTE' END,
                            codigo_sigater = CASE WHEN ? != '' THEN ? ELSE codigo_sigater END,
                            updated_at = ?
                        WHERE id = ?
                    """, (cpf, cpf, tecnico, tecnico, comunidade, comunidade, municipio, municipio, data_execucao, data_execucao, codigo_sigater, codigo_sigater, agora, reg_id))
                else:
                    _exec_sql(conn, """
                        INSERT INTO bsf_sigater_pendencias (
                            mes_contrato, mes_ano_referencia, atividade_nome,
                            beneficiario_nome, beneficiario_cpf, tecnico,
                            comunidade, municipio, data_execucao, status,
                            codigo_sigater, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDENTE', ?, ?, ?)
                    """, (
                        mes_contrato, mes_ano_referencia, atividade_nome,
                        nome, cpf, tecnico, comunidade, municipio, data_execucao,
                        codigo_sigater, agora, agora
                    ))
                total_salvos += 1

        # 3. Processa Apenas no SIGATER (Lançados no SIGATER sem par no Coletum)
        if apenas_sigater:
            for s in apenas_sigater:
                nome = str(s.get("beneficiario") or s.get("nome", "")).strip().upper()
                cpf = str(s.get("cpf", "")).strip()
                tecnico = str(s.get("tecnico", "") or "SIGATER (Sem Coletum)").strip()
                comunidade = str(s.get("comunidade", "")).strip()
                municipio = str(s.get("municipio", "")).strip()
                data_execucao = str(s.get("data", "") or s.get("data_execucao", "")).strip()
                codigo_sigater = str(s.get("codigo_sigater") or s.get("codExec") or s.get("cod_exec") or "").strip()
                link_sigater = str(s.get("link_sigater") or s.get("url") or "").strip()
                match_tipo = str(s.get("match_tipo") or "APENAS_SIGATER").strip()
                observacoes = str(s.get("observacoes") or "Lançado no SIGATER, porém sem formulário correspondente no Coletum.").strip()

                if not nome:
                    continue

                cursor = _exec_sql(conn, """
                    SELECT id FROM bsf_sigater_pendencias
                    WHERE mes_contrato = ? AND atividade_nome = ? AND beneficiario_nome = ?
                """, (mes_contrato, atividade_nome, nome))
                row = cursor.fetchone()

                if row:
                    reg_id = row["id"] if isinstance(row, dict) or hasattr(row, "__getitem__") else row[0]
                    _exec_sql(conn, """
                        UPDATE bsf_sigater_pendencias
                        SET beneficiario_cpf = CASE WHEN ? != '' THEN ? ELSE beneficiario_cpf END,
                            tecnico = CASE WHEN ? != '' THEN ? ELSE tecnico END,
                            comunidade = CASE WHEN ? != '' THEN ? ELSE comunidade END,
                            municipio = CASE WHEN ? != '' THEN ? ELSE municipio END,
                            data_execucao = CASE WHEN ? != '' THEN ? ELSE data_execucao END,
                            status = 'SEM_COLETUM',
                            codigo_sigater = ?,
                            link_sigater = ?,
                            match_tipo = ?,
                            observacoes = ?,
                            updated_at = ?
                        WHERE id = ?
                    """, (cpf, cpf, tecnico, tecnico, comunidade, comunidade, municipio, municipio, data_execucao, data_execucao, codigo_sigater, link_sigater, match_tipo, observacoes, agora, reg_id))
                else:
                    _exec_sql(conn, """
                        INSERT INTO bsf_sigater_pendencias (
                            mes_contrato, mes_ano_referencia, atividade_nome,
                            beneficiario_nome, beneficiario_cpf, tecnico,
                            comunidade, municipio, data_execucao, status,
                            codigo_sigater, link_sigater, match_tipo, observacoes,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'SEM_COLETUM', ?, ?, ?, ?, ?, ?)
                    """, (
                        mes_contrato, mes_ano_referencia, atividade_nome,
                        nome, cpf, tecnico, comunidade, municipio, data_execucao,
                        codigo_sigater, link_sigater, match_tipo, observacoes,
                        agora, agora
                    ))
                total_salvos += 1

        conn.commit()
        return {
            "sucesso": True,
            "total_processados": total_salvos,
            "total_lancados": len(lancados) if lancados else 0,
            "total_pendentes": len(pendentes) if pendentes else 0,
            "total_apenas_sigater": len(apenas_sigater) if apenas_sigater else 0,
            "mensagem": f"{total_salvos} registro(s) processado(s) com sucesso!"
        }
    except Exception as e:
        logger.error(f"Erro ao salvar pendências/lançamentos SIGATER no banco: {e}")
        conn.rollback()
        raise e
    finally:
        try:
            next(conn_gen, None)
        except Exception:
            pass


def listar_pendencias_do_banco(
    mes_contrato: Optional[int] = None,
    atividade_nome: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Consulta os registros salvos na tabela bsf_sigater_pendencias com filtros opcionais."""
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    try:
        _garantir_tabela_pendencias(conn)
        query = "SELECT * FROM bsf_sigater_pendencias WHERE 1=1"
        params = []

        if mes_contrato is not None:
            query += " AND mes_contrato = ?"
            params.append(mes_contrato)

        if atividade_nome:
            query += " AND atividade_nome LIKE ?"
            params.append(f"%{atividade_nome}%")

        if status:
            query += " AND status = ?"
            params.append(status.upper())

        query += " ORDER BY mes_contrato DESC, status ASC, beneficiario_nome ASC"
        cursor = _exec_sql(conn, query, tuple(params))
        rows = cursor.fetchall()

        resultado = []
        for r in rows:
            if isinstance(r, dict):
                resultado.append(dict(r))
            elif hasattr(r, "keys"):
                resultado.append({k: r[k] for k in r.keys()})
            else:
                resultado.append({
                    "id": r[0], "mes_contrato": r[1], "mes_ano_referencia": r[2],
                    "atividade_nome": r[3], "beneficiario_nome": r[4],
                    "beneficiario_cpf": r[5], "tecnico": r[6], "comunidade": r[7],
                    "municipio": r[8], "data_execucao": r[9], "status": r[10],
                    "codigo_sigater": r[11] if len(r) > 11 else "",
                    "link_sigater": r[12] if len(r) > 12 else "",
                    "match_tipo": r[13] if len(r) > 13 else "",
                    "observacoes": r[14] if len(r) > 14 else "",
                    "created_at": r[15] if len(r) > 15 else "",
                    "updated_at": r[16] if len(r) > 16 else ""
                })
        return resultado
    finally:
        try:
            next(conn_gen, None)
        except Exception:
            pass


def alterar_status_pendencia(pendencia_id: int, novo_status: str) -> bool:
    """Atualiza o status de uma pendência/lançamento ('LANCADO', 'PENDENTE' ou 'RESOLVIDO')."""
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        _garantir_tabela_pendencias(conn)
        _exec_sql(conn, """
            UPDATE bsf_sigater_pendencias
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (novo_status.upper(), agora, pendencia_id))
        conn.commit()
        return True
    finally:
        try:
            next(conn_gen, None)
        except Exception:
            pass


def atualizar_codigo_sigater_registro(
    registro_id: int,
    codigo_sigater: Optional[str] = None,
    novo_status: Optional[str] = None,
    beneficiario_nome: Optional[str] = None,
    beneficiario_cpf: Optional[str] = None,
    tecnico: Optional[str] = None,
    comunidade: Optional[str] = None,
    municipio: Optional[str] = None,
    observacoes: Optional[str] = None
) -> bool:
    """Atualiza dados cadastrais, Código SIGATER e status de um registro individual."""
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        _garantir_tabela_pendencias(conn)
        
        campos = ["updated_at = ?"]
        valores = [agora]
        
        if codigo_sigater is not None:
            cod_limpo = codigo_sigater.strip().replace("#", "")
            campos.append("codigo_sigater = ?")
            valores.append(cod_limpo)
            
        if novo_status is not None and str(novo_status).strip():
            campos.append("status = ?")
            valores.append(str(novo_status).strip().upper())
            
        if beneficiario_nome is not None and str(beneficiario_nome).strip():
            campos.append("beneficiario_nome = ?")
            valores.append(str(beneficiario_nome).strip().upper())
            
        if beneficiario_cpf is not None:
            campos.append("beneficiario_cpf = ?")
            valores.append(str(beneficiario_cpf).strip())
            
        if tecnico is not None:
            campos.append("tecnico = ?")
            valores.append(str(tecnico).strip())
            
        if comunidade is not None:
            campos.append("comunidade = ?")
            valores.append(str(comunidade).strip())
            
        if municipio is not None:
            campos.append("municipio = ?")
            valores.append(str(municipio).strip())
            
        if observacoes is not None:
            campos.append("observacoes = ?")
            valores.append(str(observacoes).strip())
            
        valores.append(registro_id)
        sql = f"UPDATE bsf_sigater_pendencias SET {', '.join(campos)} WHERE id = ?"
        _exec_sql(conn, sql, tuple(valores))
        conn.commit()
        return True
    finally:
        try:
            next(conn_gen, None)
        except Exception:
            pass


def remover_pendencia(pendencia_id: int) -> bool:
    """Remove um registro da tabela bsf_sigater_pendencias."""
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    try:
        _garantir_tabela_pendencias(conn)
        _exec_sql(conn, "DELETE FROM bsf_sigater_pendencias WHERE id = ?", (pendencia_id,))
        conn.commit()
        return True
    finally:
        try:
            next(conn_gen, None)
        except Exception:
            pass
