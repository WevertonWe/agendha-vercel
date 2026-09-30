"""
Router do SIGATER Hub - Geração de Scripts F12, Coletum e Rastreamento de Pendências
Módulo: Bahia Sem Fome (BSF)
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

from app.modules.bahia_sem_fome.services.sigater_hub_service import (
    ATIVIDADES_BSF,
    calcular_competencia_mes_contrato,
    obter_beneficiarios_coletum_competencia,
    gerar_script_f12_dinamico,
    salvar_pendencias_no_banco,
    listar_pendencias_do_banco,
    alterar_status_pendencia,
    atualizar_codigo_sigater_registro,
    remover_pendencia
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bsf/sigater-hub", tags=["BSF SIGATER Hub"])


class GerarScriptRequest(BaseModel):
    atividade_codigo: str
    mes_contrato: int


class SalvarPendenciasRequest(BaseModel):
    mes_contrato: Optional[int] = None
    atividade_codigo: Optional[str] = None
    atividade_nome: Optional[str] = None
    competencia: Optional[str] = None
    conteudo_colado: Optional[str] = None
    pendentes: Optional[List[Dict[str, Any]]] = None
    lancados: Optional[List[Dict[str, Any]]] = None
    apenas_sigater: Optional[List[Dict[str, Any]]] = None
    divergencias: Optional[List[Dict[str, Any]]] = None


class AtualizarStatusRequest(BaseModel):
    status: str


class AtualizarCodigoSigaterRequest(BaseModel):
    codigo_sigater: Optional[str] = None
    status: Optional[str] = None
    beneficiario_nome: Optional[str] = None
    beneficiario_cpf: Optional[str] = None
    tecnico: Optional[str] = None
    comunidade: Optional[str] = None
    municipio: Optional[str] = None
    observacoes: Optional[str] = None


@router.get("/configuracoes")
async def obter_configuracoes():
    """Retorna as atividades suportadas e a grade de 36 meses do contrato."""
    meses = [calcular_competencia_mes_contrato(m) for m in range(1, 37)]
    atividades = list(ATIVIDADES_BSF.values())
    return {
        "atividades": atividades,
        "meses": meses
    }


@router.get("/consultar-coletum")
async def consultar_coletum(
    atividade_codigo: str = Query(..., description="Código da atividade (ex: PLANO_PRODUTIVO)"),
    mes_contrato: int = Query(..., ge=1, le=36, description="Número do mês do contrato (1 a 36)")
):
    """Consulta as respostas do Coletum para a atividade e mês selecionados."""
    try:
        dados = await obter_beneficiarios_coletum_competencia(atividade_codigo, mes_contrato)
        return dados
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Erro ao consultar Coletum no Sigater Hub: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Coletum: {str(e)}")


@router.post("/gerar-script")
async def gerar_script(dados: GerarScriptRequest):
    """Gera o script JS completo para colar no Console do Navegador (F12) no SIGATER."""
    try:
        coletum_info = await obter_beneficiarios_coletum_competencia(
            dados.atividade_codigo,
            dados.mes_contrato
        )
        beneficiarios = coletum_info.get("beneficiarios", [])
        
        script_js = gerar_script_f12_dinamico(
            dados.atividade_codigo,
            dados.mes_contrato,
            beneficiarios,
            duplicados=coletum_info.get("duplicados", []),
            total_preenchimentos=coletum_info.get("total_preenchimentos", len(beneficiarios))
        )

        return {
            "sucesso": True,
            "atividade": coletum_info.get("atividade", {}),
            "competencia": coletum_info.get("competencia", {}),
            "total_coletum": len(beneficiarios),
            "script_js": script_js
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Erro ao gerar script F12 no Sigater Hub: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar script: {str(e)}")


@router.post("/salvar-pendencias")
async def salvar_pendencias(payload: SalvarPendenciasRequest):
    """
    Recebe o retorno de auditoria/lançamentos do SIGATER.
    Aceita payload com 'lancados' (com códigos SIGATER), 'pendentes', 'apenas_sigater' ou texto livre colado.
    """
    try:
        mes_contrato = payload.mes_contrato or 1
        atividade_nome = payload.atividade_nome or "Atividade Geral"
        competencia = payload.competencia or ""
        pendentes_finais = payload.pendentes or []
        lancados_finais = payload.lancados or []
        apenas_sigater_finais = payload.apenas_sigater or payload.divergencias or []

        # Se veio texto colado (conteudo_colado)
        if payload.conteudo_colado and not (pendentes_finais or lancados_finais or apenas_sigater_finais):
            texto = payload.conteudo_colado.strip()
            
            # 1. Tenta decodificar como JSON
            if texto.startswith("{") or texto.startswith("["):
                try:
                    parsed = json.loads(texto)
                    if isinstance(parsed, dict):
                        mes_contrato = parsed.get("mes_contrato") or mes_contrato
                        atividade_nome = parsed.get("atividade_nome") or atividade_nome
                        competencia = parsed.get("competencia") or competencia
                        pendentes_finais = parsed.get("pendentes") or []
                        lancados_finais = parsed.get("lancados") or []
                        apenas_sigater_finais = parsed.get("apenas_sigater") or parsed.get("divergencias") or parsed.get("sigaterSobrando") or []
                    elif isinstance(parsed, list):
                        for item in parsed:
                            if isinstance(item, dict):
                                st = str(item.get("status", "")).upper()
                                if st == "SEM_COLETUM" or st == "APENAS_SIGATER":
                                    apenas_sigater_finais.append(item)
                                elif st == "LANCADO" or item.get("codigo_sigater"):
                                    lancados_finais.append(item)
                                else:
                                    pendentes_finais.append(item)
                except Exception:
                    pass

            # 2. Se ainda não extraiu, faz parsing linha por linha
            if not (pendentes_finais or lancados_finais or apenas_sigater_finais):
                linhas = texto.splitlines()
                for linha in linhas:
                    linha = linha.strip()
                    if not linha or linha.startswith("#") or "===" in linha:
                        continue
                    
                    partes = linha.split("|")
                    if len(partes) >= 2:
                        nome_raw = partes[0].strip()
                        nome = re.sub(r'^\d+[\.\-\)]\s*', '', nome_raw).strip()
                        
                        cpf = ""
                        tecnico = ""
                        comunidade = ""
                        municipio = ""
                        data_exec = ""
                        codigo_sigater = ""
                        status_linha = "PENDENTE"

                        for p in partes[1:]:
                            p = p.strip()
                            if "CPF:" in p:
                                cpf = p.replace("CPF:", "").strip()
                            elif "Código SIGATER:" in p or "Codigo SIGATER:" in p or "Código:" in p:
                                codigo_sigater = p.split(":")[-1].strip().replace("#", "")
                            elif "Técnico:" in p:
                                tec_parte = p.replace("Técnico:", "").strip()
                                if " - " in tec_parte:
                                    tecnico, resto = tec_parte.split(" - ", 1)
                                    tecnico = tecnico.strip()
                                    if "(" in resto and ")" in resto:
                                        comunidade = resto.split("(")[0].strip()
                                        municipio = resto.split("(")[1].replace(")", "").strip()
                                    else:
                                        comunidade = resto.strip()
                                else:
                                    tecnico = tec_parte
                            elif "Data:" in p:
                                data_exec = p.replace("Data:", "").strip()
                            elif "Status:" in p:
                                status_linha = p.replace("Status:", "").strip().upper()

                        if nome:
                            item = {
                                "beneficiario": nome,
                                "cpf": cpf,
                                "tecnico": tecnico,
                                "comunidade": comunidade,
                                "municipio": municipio,
                                "data": data_exec,
                                "codigo_sigater": codigo_sigater
                            }
                            if "SEM_COLETUM" in status_linha or "APENAS_SIGATER" in status_linha or "SEM COLETUM" in status_linha:
                                apenas_sigater_finais.append(item)
                            elif status_linha == "LANCADO" or codigo_sigater:
                                lancados_finais.append(item)
                            else:
                                pendentes_finais.append(item)

        if not (pendentes_finais or lancados_finais or apenas_sigater_finais):
            raise HTTPException(status_code=400, detail="Nenhum beneficiário identificado no texto colado.")

        if not competencia:
            comp_info = calcular_competencia_mes_contrato(mes_contrato)
            competencia = comp_info["mes_ano"]

        res = salvar_pendencias_no_banco(
            mes_contrato=mes_contrato,
            mes_ano_referencia=competencia,
            atividade_nome=atividade_nome,
            pendentes=pendentes_finais,
            lancados=lancados_finais,
            apenas_sigater=apenas_sigater_finais
        )
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao salvar lançamentos/pendências SIGATER: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar lançamentos/pendências: {str(e)}")


@router.get("/pendencias")
async def listar_pendencias(
    mes_contrato: Optional[int] = Query(None, description="Filtrar por Mês do Contrato"),
    atividade_nome: Optional[str] = Query(None, description="Filtrar por Atividade"),
    status: Optional[str] = Query(None, description="Filtrar por Status (LANCADO / PENDENTE / RESOLVIDO)")
):
    """Lista os beneficiários cadastrados no SIGATER Hub (Lançados e Pendentes)."""
    try:
        itens = listar_pendencias_do_banco(mes_contrato, atividade_nome, status)
        return {
            "total": len(itens),
            "pendencias": itens
        }
    except Exception as e:
        logger.error(f"Erro ao listar pendências/lançamentos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar registros: {str(e)}")


@router.patch("/pendencias/{pendencia_id}/status")
async def atualizar_status(pendencia_id: int, payload: AtualizarStatusRequest):
    """Atualiza o status de um registro (ex: 'LANCADO', 'PENDENTE' ou 'RESOLVIDO')."""
    try:
        ok = alterar_status_pendencia(pendencia_id, payload.status)
        if not ok:
            raise HTTPException(status_code=404, detail="Registro não encontrado.")
        return {"sucesso": True, "novo_status": payload.status.upper()}
    except Exception as e:
        logger.error(f"Erro ao atualizar status do registro {pendencia_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")


@router.patch("/pendencias/{pendencia_id}/codigo")
@router.put("/pendencias/{pendencia_id}")
async def atualizar_codigo_sigater(pendencia_id: int, payload: AtualizarCodigoSigaterRequest):
    """Atualiza dados cadastrais (Nome, CPF, etc.), Código SIGATER e status de um beneficiário."""
    try:
        ok = atualizar_codigo_sigater_registro(
            registro_id=pendencia_id,
            codigo_sigater=payload.codigo_sigater,
            novo_status=payload.status,
            beneficiario_nome=payload.beneficiario_nome,
            beneficiario_cpf=payload.beneficiario_cpf,
            tecnico=payload.tecnico,
            comunidade=payload.comunidade,
            municipio=payload.municipio,
            observacoes=payload.observacoes
        )
        if not ok:
            raise HTTPException(status_code=404, detail="Registro não encontrado.")
        return {
            "sucesso": True,
            "mensagem": "Registro atualizado com sucesso!",
            "codigo_sigater": (payload.codigo_sigater or "").strip().replace("#", ""),
            "beneficiario_nome": payload.beneficiario_nome,
            "status": payload.status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar registro {pendencia_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar registro: {str(e)}")


@router.get("/arquivos-beneficiario")
async def obter_arquivos_beneficiario(
    nome: str = Query(..., description="Nome do beneficiário"),
    tecnico: Optional[str] = Query(None, description="Nome do técnico"),
    comunidade: Optional[str] = Query(None, description="Comunidade")
):
    """Busca todos os arquivos PDFs (Atestes, Coletum e SIGATER) salvos no sistema para o beneficiário."""
    try:
        from app.modules.bahia_sem_fome.routers.beneficiarios import escanear_atividades_locais_beneficiario
        atividades = escanear_atividades_locais_beneficiario(0, nome, tecnico, comunidade)
        
        todos_arquivos = []
        for ativ in atividades:
            for arq in ativ.get("arquivos", []):
                todos_arquivos.append({
                    "atividade": ativ.get("tipo_atividade", "Atividade"),
                    "data": ativ.get("data") or ativ.get("data_atividade"),
                    "nome": arq.get("nome"),
                    "tipo": arq.get("tipo"),
                    "url": arq.get("url"),
                    "tamanho": arq.get("tamanho")
                })
        return {
            "sucesso": True,
            "total": len(todos_arquivos),
            "atividades": atividades,
            "arquivos": todos_arquivos
        }
    except Exception as e:
        logger.error(f"Erro ao buscar arquivos do beneficiário {nome}: {e}")
        return {"sucesso": False, "total": 0, "atividades": [], "arquivos": [], "erro": str(e)}


@router.delete("/pendencias/{pendencia_id}")
async def excluir_pendencia(pendencia_id: int):
    """Remove um registro do SIGATER Hub."""
    try:
        ok = remover_pendencia(pendencia_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Registro não encontrado.")
        return {"sucesso": True, "mensagem": "Registro excluído com sucesso."}
    except Exception as e:
        logger.error(f"Erro ao excluir registro {pendencia_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir: {str(e)}")
