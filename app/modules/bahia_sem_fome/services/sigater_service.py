"""
BSF SIGATER Service - Ingestão Inteligente e Roteamento de Atestes
Mapeia automaticamente atestes exportados do SIGATER para os técnicos e comunidades corretos.
"""

import os
import io
import re
import difflib
import zipfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from app.services.scanner_service import (
    get_base_storage_path,
    normalizar_data
)
from app.modules.bahia_sem_fome.services.auditoria_service import (
    sanitizar_nome_seguro,
    normalizar_nome_canonico,
    extrair_categoria_atividade
)

logger = logging.getLogger("sigater_service")


def carregar_mapa_beneficiarios_reais(base_dir: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """
    Varre a estrutura real de técnicos no disco e cria um catálogo indexado de todos os beneficiários:
    Chave: Nome normalizado (sem acentos, maiúsculo) -> {tecnico, comunidade, pasta_beneficiario, nome_original}
    """
    caminho_base = base_dir or get_base_storage_path()
    catalogo = {}

    if not caminho_base.exists():
        return catalogo

    ignorar = {"ATESTES", "CARACTERIZAÇÃO", "CARACTERIZACAO", "PLANOS PRODUTIVOS", "TEMP", "UPLOADS"}

    for tec in caminho_base.iterdir():
        if not tec.is_dir() or tec.name.startswith("_") or tec.name.upper() in ignorar:
            continue
        
        doc_ativ = tec / "documentos-atividades"
        alvo = doc_ativ if doc_ativ.exists() else tec

        for com in alvo.iterdir():
            if not com.is_dir() or com.name.upper() == "ATIVIDADE COLETIVA":
                continue

            for benef in com.iterdir():
                if benef.is_dir():
                    nome_canonico = normalizar_nome_canonico(benef.name)
                    catalogo[nome_canonico] = {
                        "tecnico": tec.name,
                        "comunidade": com.name,
                        "pasta_beneficiario": benef,
                        "nome_original": benef.name
                    }

    return catalogo


def encontrar_melhor_beneficiario(
    nome_candidato: str,
    catalogo_beneficiarios: Dict[str, Dict[str, Any]]
) -> Optional[Tuple[Dict[str, Any], float]]:
    """
    Localiza o beneficiário real no catálogo usando similaridade difusa (Fuzzy Matching).
    Retorna (dados_beneficiario, score) se score >= 0.75, senão None.
    """
    if not nome_candidato or len(nome_candidato) < 3:
        return None

    cand_norm = normalizar_nome_canonico(nome_candidato)

    # 1. Match exato
    if cand_norm in catalogo_beneficiarios:
        return catalogo_beneficiarios[cand_norm], 1.0

    melhor_match = None
    melhor_score = 0.0

    partes_cand = cand_norm.split()

    for b_norm, b_info in catalogo_beneficiarios.items():
        # Match por contenção se tiver mais de 2 palavras
        if len(partes_cand) >= 2:
            if cand_norm in b_norm or b_norm in cand_norm:
                return b_info, 0.95

            partes_b = b_norm.split()
            # Se primeiro e segundo nome forem iguais
            if len(partes_b) >= 2 and partes_cand[0] == partes_b[0] and partes_cand[1] == partes_b[1]:
                score = difflib.SequenceMatcher(None, cand_norm, b_norm).ratio()
                if score >= 0.65 and score > melhor_score:
                    melhor_score = score
                    melhor_match = b_info
                continue

        score = difflib.SequenceMatcher(None, cand_norm, b_norm).ratio()
        if score >= 0.78 and score > melhor_score:
            melhor_score = score
            melhor_match = b_info

    if melhor_match:
        return melhor_match, melhor_score

    return None


def extrair_metadados_nome_arquivo(nome_arquivo: str) -> Tuple[str, str]:
    """
    Extrai o nome do beneficiário e a data a partir do padrão de arquivo exportado pelo SIGATER:
    Ex: 'Renata_da_Silva_-_Ateste_16-09-2025_2025-11-14_11-38-06.pdf' -> ('RENATA DA SILVA', '16.09.2025')
    """
    limpo = re.sub(r"\.pdf$", "", nome_arquivo, flags=re.IGNORECASE)
    
    # Extrai data DD-MM-AAAA ou DD_MM_AAAA
    data_match = re.search(r"(\d{2})[-_\.](\d{2})[-_\.](\d{4})", limpo)
    data_fmt = ""
    if data_match:
        d, m, y = data_match.groups()
        data_fmt = f"{d}.{m}.{y}"
        
    # Extrai o nome antes do marcador de ateste
    partes = re.split(r"[-_]+(?:ateste|at[-_]caract|caracteriza|at)", limpo, flags=re.IGNORECASE)
    nome_cru = partes[0]
    nome_cru = re.sub(r"[^a-zA-Z\s_]", " ", nome_cru).replace("_", " ")
    nome_norm = re.sub(r"\s+", " ", nome_cru).strip().upper()
    return nome_norm, data_fmt


def extrair_metadados_ateste_pdf(pdf_bytes: bytes, nome_arquivo: str = "") -> Dict[str, Any]:
    """
    Função de extração de metadados de atestes compatível com a API e testes.
    """
    nome_norm, data_fmt = extrair_metadados_nome_arquivo(nome_arquivo)
    return {
        "beneficiario": nome_norm,
        "data": data_fmt,
        "comunidade": "",
        "tecnico": "",
        "atividade": "CARACTERIZAÇÃO"
    }


def organizar_ateste_no_disco_local(
    pdf_bytes: bytes,
    nome_beneficiario: str,
    comunidade: str,
    tecnico: str,
    data_atividade: str,
    atividade_nome: str,
    base_storage_dir: Optional[Path] = None,
    catalogo_beneficiarios: Optional[Dict[str, Dict[str, Any]]] = None,
    nome_arquivo_original: str = ""
) -> Dict[str, Any]:
    """
    Salva o Ateste na pasta correta do beneficiário real no disco:
    [TECNICO] / documentos-atividades / [COMUNIDADE] / [BENEFICIARIO] / [DD.MM.AAAA - ATIVIDADE] / [BENEFICIARIO] - ATESTE.pdf
    """
    base_dir = base_storage_dir or get_base_storage_path()
    
    if catalogo_beneficiarios is None:
        catalogo_beneficiarios = carregar_mapa_beneficiarios_reais(base_dir)

    # 1. Tenta identificar o beneficiário real por similaridade
    match_result = encontrar_melhor_beneficiario(nome_beneficiario, catalogo_beneficiarios)
    
    if match_result:
        b_info, score = match_result
        pasta_benef = b_info["pasta_beneficiario"]
        nome_benef_real = b_info["nome_original"]
        tec_nome = b_info["tecnico"]
        com_nome = b_info["comunidade"]
        status_match = f"Pareado ({score:.2f}) com {nome_benef_real}"
    elif tecnico and comunidade and nome_beneficiario and comunidade != "GERAL":
        # Se técnico e comunidade foram explicitamente informados
        tec_norm = sanitizar_nome_seguro(tecnico).lower()
        com_norm = sanitizar_nome_seguro(comunidade)
        benef_norm = normalizar_nome_canonico(nome_beneficiario)
        pasta_benef = base_dir / tec_norm / "documentos-atividades" / com_norm / benef_norm
        pasta_benef.mkdir(parents=True, exist_ok=True)
        nome_benef_real = benef_norm
        tec_nome = tec_norm
        com_nome = com_norm
        status_match = "Destino explícito"
    else:
        # Se NÃO encontrou beneficiário conhecido com segurança, NÃO inventa pastas estranhas!
        # Coloca na pasta de triagem / pendentes de revisão
        pasta_triagem = base_dir / "_IMPORTACOES_PENDENTES_REVISAO"
        pasta_triagem.mkdir(parents=True, exist_ok=True)
        
        nome_arquivo_salvar = nome_arquivo_original or f"{sanitizar_nome_seguro(nome_beneficiario)}_ATEST.pdf"
        caminho_final = pasta_triagem / nome_arquivo_salvar
        with open(caminho_final, "wb") as f_out:
            f_out.write(pdf_bytes)
            
        return {
            "status": "pendente_revisao",
            "caminho_absoluto": str(caminho_final),
            "caminho_relativo": f"_IMPORTACOES_PENDENTES_REVISAO/{caminho_final.name}",
            "beneficiario": nome_beneficiario,
            "motivo": "Beneficiário não localizado com segurança no sistema"
        }

    # 2. Formata a subpasta da atividade
    data_fmt = normalizar_data(data_atividade) if data_atividade else datetime.now().strftime("%d.%m.%Y")
    cat_ativ = extrair_categoria_atividade(atividade_nome)
    
    pasta_atividade_alvo = None
    if pasta_benef.exists():
        for sub in pasta_benef.iterdir():
            if sub.is_dir() and (data_fmt in sub.name or cat_ativ in sanitizar_nome_seguro(sub.name)):
                pasta_atividade_alvo = sub
                break

    if not pasta_atividade_alvo:
        nome_pasta_ativ = f"{data_fmt} - {cat_ativ}" if cat_ativ != "OUTROS" else data_fmt
        pasta_atividade_alvo = pasta_benef / nome_pasta_ativ
        pasta_atividade_alvo.mkdir(parents=True, exist_ok=True)

    # 3. Salva o PDF do Ateste com o nome canônico
    nome_arquivo_final = f"{normalizar_nome_canonico(nome_benef_real)} - ATESTE.pdf"
    caminho_final = pasta_atividade_alvo / nome_arquivo_final

    with open(caminho_final, "wb") as f_out:
        f_out.write(pdf_bytes)

    rel_path = f"{tec_nome}/documentos-atividades/{com_nome}/{nome_benef_real}/{pasta_atividade_alvo.name}/{nome_arquivo_final}"
    
    return {
        "status": "sucesso",
        "match": status_match,
        "caminho_absoluto": str(caminho_final),
        "caminho_relativo": rel_path,
        "beneficiario": nome_benef_real,
        "tecnico": tec_nome,
        "comunidade": com_nome,
        "atividade": cat_ativ,
        "pasta": pasta_atividade_alvo.name
    }


def processar_pacote_zip_sigater(
    zip_bytes: bytes,
    atividade_padrao: str = "CARACTERIZAÇÃO",
    base_storage_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Processa um arquivo ZIP contendo múltiplos Atestes exportados do SIGATER.
    Usa o catálogo de beneficiários reais para distribuir cada arquivo na pasta certa.
    """
    base_dir = base_storage_dir or get_base_storage_path()
    catalogo = carregar_mapa_beneficiarios_reais(base_dir)
    
    processados = []
    erros = []
    pendentes_revisao = []

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            for item in zf.infolist():
                if item.is_dir() or not item.filename.lower().endswith('.pdf'):
                    continue

                pdf_content = zf.read(item.filename)
                nome_simples = Path(item.filename).name

                # Ignora arquivos corrompidos ou HTML
                if not pdf_content.startswith(b'%PDF'):
                    logger.warning(f"Arquivo '{nome_simples}' no ZIP não é um PDF válido. Ignorando.")
                    erros.append({"arquivo": nome_simples, "erro": "Arquivo corrompido ou HTML"})
                    continue

                # Extrai nome e data pelo nome do arquivo
                nome_cand, data_cand = extrair_metadados_nome_arquivo(nome_simples)

                try:
                    res = organizar_ateste_no_disco_local(
                        pdf_bytes=pdf_content,
                        nome_beneficiario=nome_cand,
                        comunidade="",
                        tecnico="",
                        data_atividade=data_cand,
                        atividade_nome=atividade_padrao,
                        base_storage_dir=base_dir,
                        catalogo_beneficiarios=catalogo,
                        nome_arquivo_original=nome_simples
                    )
                    
                    if res.get("status") == "sucesso":
                        processados.append(res)
                    else:
                        pendentes_revisao.append(res)
                except Exception as e_item:
                    logger.error(f"Erro ao organizar '{nome_simples}': {e_item}")
                    erros.append({"arquivo": nome_simples, "erro": str(e_item)})

    except Exception as e:
        logger.error(f"Erro ao descompactar ZIP do SIGATER: {e}")
        return {
            "sucesso": False,
            "erro": str(e),
            "total_processados": 0
        }

    return {
        "sucesso": True,
        "total_processados": len(processados),
        "total_pendentes_revisao": len(pendentes_revisao),
        "total_erros": len(erros),
        "processados": processados,
        "pendentes_revisao": pendentes_revisao,
        "erros": erros
    }
