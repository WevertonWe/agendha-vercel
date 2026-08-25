"""
Serviço de Integração e Cruzamento com a API Coletum (v2) - Bahia Sem Fome (BSF)
Responsável por:
1. Autenticação e consulta aos formulários e respostas via API v2.
2. Cruzamento inteligente de dados com a lista de beneficiários do banco / pastas locais.
3. Detecção de discrepâncias de grafia/nomes (Fuzzy Matching) marcados como "Atenção / Revisão Manual".
4. Detecção de inconsistências de datas marcadas como "Aviso de Data".
"""

import os
import re
import httpx
import logging
import unicodedata
from difflib import SequenceMatcher
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

from app.core.database import get_supabase

logger = logging.getLogger(__name__)

# Token lido prioritariamente de variável de ambiente com fallback seguro
COLETUM_TOKEN = os.getenv("COLETUM_TOKEN", "517vrjljdboc8g0wwsw48k8co40cos8")
BASE_URL_V2 = "https://coletum.com/api/webservice/v2"


def normalizar_texto_comparacao(texto: str) -> str:
    """Normaliza texto para comparação segura e insensível a acentos/espaços."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize('NFKD', str(texto))
    sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    limpo = re.sub(r'[^A-Z0-9\s]', '', sem_acento.upper())
    return re.sub(r'\s+', ' ', limpo).strip()


def normalizar_cpf_comparacao(cpf: str) -> str:
    """Extrai apenas os números do CPF."""
    if not cpf:
        return ""
    return re.sub(r'\D', '', str(cpf))


def calcular_similaridade_nomes(nome1: str, nome2: str) -> float:
    """Retorna taxa de similaridade (0.0 a 1.0) entre dois nomes."""
    n1 = normalizar_texto_comparacao(nome1)
    n2 = normalizar_texto_comparacao(nome2)
    if not n1 or not n2:
        return 0.0
    if n1 == n2:
        return 1.0
    return SequenceMatcher(None, n1, n2).ratio()


def extrair_data_coletum(valor_data: str) -> Optional[str]:
    """Tenta converter datas diversas do Coletum para DD/MM/AAAA."""
    if not valor_data:
        return None
    val_str = str(valor_data).strip().replace('/', '-').replace('.', '-')
    parts = val_str.split('-')
    try:
        if len(parts) == 3:
            if len(parts[0]) == 4:  # YYYY-MM-DD
                return f"{int(parts[2]):02d}/{int(parts[1]):02d}/{parts[0]}"
            elif len(parts[2]) == 4:  # DD-MM-YYYY
                return f"{int(parts[0]):02d}/{int(parts[1]):02d}/{parts[2]}"
    except Exception:
        pass
    return str(valor_data)


async def listar_formularios_coletum() -> List[Dict[str, Any]]:
    """Busca a lista de formulários ativos na conta Coletum."""
    headers = {
        "Token": COLETUM_TOKEN,
        "Accept": "application/json"
    }
    url = f"{BASE_URL_V2}/forms"
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.error(f"Erro ao listar formulários Coletum: HTTP {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Exceção ao conectar à API do Coletum: {e}")
            return []


async def buscar_respostas_formulario(form_id: str, limit: int = 200) -> List[Dict[str, Any]]:
    """Busca as respostas submetidas para um formulário específico no Coletum."""
    headers = {
        "Token": COLETUM_TOKEN,
        "Accept": "application/json"
    }
    url = f"{BASE_URL_V2}/forms/{form_id}/answers?limit={limit}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.error(f"Erro ao buscar respostas do formulário {form_id}: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Exceção ao buscar respostas do Coletum {form_id}: {e}")
            return []


def extrair_metadados_resposta_coletum(resposta_raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrai de forma resiliente os campos-chave (Nome, CPF, Data, Técnico, Município)
    a partir da estrutura dinâmica de resposta da API Coletum.
    """
    ans = resposta_raw.get("answer", {}) or {}
    ans_id = resposta_raw.get("id") or resposta_raw.get("code") or "N/A"
    data_envio = resposta_raw.get("created_at") or resposta_raw.get("updated_at") or ""

    nome_benef = ""
    cpf_benef = ""
    municipio = ""
    comunidade = ""
    tecnico = ""
    data_atividade = ""

    # Varre as chaves do dicionário de respostas de forma normalizada (sem acento)
    for k, v in ans.items():
        k_norm = normalizar_texto_comparacao(str(k))
        v_str = str(v).strip()

        # Nome
        if any(term in k_norm for term in ["NOME DO BENEFICI", "BENEFICIARIO", "NOME COMPLETO", "NOME"]) and not nome_benef:
            if "TECNICO" not in k_norm:
                nome_benef = v_str
        # CPF
        if "CPF" in k_norm and not cpf_benef:
            if "TECNICO" not in k_norm:
                cpf_benef = normalizar_cpf_comparacao(v_str)
        # Município
        if "MUNICIPIO" in k_norm or "CIDADE" in k_norm:
            municipio = v_str
        # Comunidade
        if "COMUNIDADE" in k_norm or "LOCALIDADE" in k_norm:
            comunidade = v_str
        # Técnico
        if any(term in k_norm for term in ["TECNICO", "RESPONSAVEL"]):
            tecnico = v_str
        # Data
        if any(term in k_norm for term in ["DATA DA ATIVIDADE", "DATA ATIVIDADE", "DATA REALIZACAO", "DATA"]):
            data_atividade = extrair_data_coletum(v_str) or v_str

    return {
        "coletum_id": ans_id,
        "data_envio": data_envio,
        "beneficiario": nome_benef,
        "cpf": cpf_benef,
        "municipio": municipio,
        "comunidade": comunidade,
        "tecnico": tecnico,
        "data_atividade": data_atividade,
        "raw_answer": ans
    }


async def auditar_discrepancias_coletum(
    beneficiarios_bd: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Executa o cruzamento completo entre a API Coletum e os beneficiários cadastrados.
    Classifica divergências em:
    - SINCRONIZADO (100% match)
    - ATENCAO_REVISAO_MANUAL (70% - 99% similaridade ou variação de nome)
    - AVISO_DATA_DIVERGENTE (data diferente da esperada / ateste)
    - BENEFICIARIO_NAO_ENCONTRADO (< 70% match)
    """
    # 1. Carrega beneficiários do banco se não fornecidos
    if beneficiarios_bd is None:
        try:
            supabase = get_supabase()
            res = supabase.table("beneficiarios").select("id, nome_completo, cpf, municipio, comunidade, nome_tecnico, data_atividade").eq("projeto", "Bahia Sem Fome").execute()
            beneficiarios_bd = res.data or []
        except Exception as e:
            logger.warning(f"Não foi possível buscar beneficiários no Supabase: {e}")
            beneficiarios_bd = []

    # Cria índice por CPF e mapa normalizado de nomes
    mapa_cpf: Dict[str, Dict[str, Any]] = {}
    lista_nomes_bd: List[Tuple[str, Dict[str, Any]]] = []

    for b in beneficiarios_bd:
        cpf_limpo = normalizar_cpf_comparacao(b.get("cpf", ""))
        if cpf_limpo and len(cpf_limpo) == 11:
            mapa_cpf[cpf_limpo] = b
        nome_norm = normalizar_texto_comparacao(b.get("nome_completo", ""))
        if nome_norm:
            lista_nomes_bd.append((nome_norm, b))

    # 2. Busca formulários do Coletum
    formularios = await listar_formularios_coletum()
    total_respostas_processadas = 0
    divergencias = []
    resumo_status = {
        "sincronizados": 0,
        "atencao_revisao_manual": 0,
        "aviso_data": 0,
        "nao_encontrados": 0
    }

    for form in formularios:
        form_id = form.get("id")
        form_nome = form.get("name", "Formulário")
        respostas = await buscar_respostas_formulario(str(form_id))
        total_respostas_processadas += len(respostas)

        for r in respostas:
            meta = extrair_metadados_resposta_coletum(r)
            nome_coletum = meta["beneficiario"]
            cpf_coletum = meta["cpf"]
            data_coletum = meta["data_atividade"]
            nome_coletum_norm = normalizar_texto_comparacao(nome_coletum)

            # Tentativa 1: Match exato por CPF
            match_benef = None
            tipo_match = "NENHUM"
            score_similaridade = 0.0

            if cpf_coletum and cpf_coletum in mapa_cpf:
                match_benef = mapa_cpf[cpf_coletum]
                tipo_match = "CPF_EXATO"
                score_similaridade = 1.0
            elif nome_coletum_norm:
                # Tentativa 2: Match por nome (Exato ou Fuzzy)
                melhor_score = 0.0
                melhor_benef = None

                for nome_bd_norm, benef in lista_nomes_bd:
                    if nome_coletum_norm == nome_bd_norm:
                        melhor_score = 1.0
                        melhor_benef = benef
                        tipo_match = "NOME_EXATO"
                        break
                    sim = SequenceMatcher(None, nome_coletum_norm, nome_bd_norm).ratio()
                    if sim > melhor_score:
                        melhor_score = sim
                        melhor_benef = benef

                score_similaridade = melhor_score
                if melhor_score >= 0.70:
                    match_benef = melhor_benef
                    if tipo_match != "NOME_EXATO":
                        tipo_match = "FUZZY_NOME"

            # Avaliação de Status e Alertas
            status_item = "SINCRONIZADO"
            mensagens_alerta = []

            if not match_benef:
                status_item = "NAO_ENCONTRADO"
                resumo_status["nao_encontrados"] += 1
                mensagens_alerta.append("Beneficiário não localizado no cadastro do sistema.")
            else:
                nome_sistema = match_benef.get("nome_completo", "")
                if tipo_match == "FUZZY_NOME" or (tipo_match == "CPF_EXATO" and score_similaridade < 0.95):
                    status_item = "ATENCAO_REVISAO_MANUAL"
                    resumo_status["atencao_revisao_manual"] += 1
                    mensagens_alerta.append(
                        f"Divergência de grafia: Coletum '{nome_coletum}' vs Sistema '{nome_sistema}' "
                        f"({int(score_similaridade * 100)}% similaridade)."
                    )

                # Checagem de Divergência de Data
                data_bd = match_benef.get("data_atividade")
                if data_coletum and data_bd and data_coletum != data_bd:
                    if status_item != "ATENCAO_REVISAO_MANUAL":
                        status_item = "AVISO_DATA"
                        resumo_status["aviso_data"] += 1
                    mensagens_alerta.append(
                        f"Aviso de Data: Coletum reporta '{data_coletum}' e o sistema/ateste possui '{data_bd}'."
                    )

                if status_item == "SINCRONIZADO":
                    resumo_status["sincronizados"] += 1

            divergencias.append({
                "formulario_id": form_id,
                "formulario_nome": form_nome,
                "coletum_id": meta["coletum_id"],
                "nome_coletum": nome_coletum,
                "cpf_coletum": cpf_coletum,
                "data_coletum": data_coletum,
                "tecnico_coletum": meta["tecnico"],
                "municipio_coletum": meta["municipio"],
                "status": status_item,
                "match_beneficiario": {
                    "id": match_benef.get("id") if match_benef else None,
                    "nome": match_benef.get("nome_completo") if match_benef else None,
                    "cpf": match_benef.get("cpf") if match_benef else None,
                    "municipio": match_benef.get("municipio") if match_benef else None,
                    "tecnico": match_benef.get("nome_tecnico") if match_benef else None,
                    "data_sistema": match_benef.get("data_atividade") if match_benef else None,
                } if match_benef else None,
                "similaridade": round(score_similaridade * 100, 1),
                "mensagens": mensagens_alerta
            })

    return {
        "timestamp": datetime.now().isoformat(),
        "total_formularios": len(formularios),
        "total_respostas": total_respostas_processadas,
        "resumo": resumo_status,
        "discrepancias": divergencias
    }
