"""
BSF Auditoria e Conformidade - API Router
Rotas para consulta e execução de auditoria local de pastas (Ateste + Coletum),
deduplicação de diretórios com acentos e cruzamento inteligente com a API Coletum v2.
"""

import logging
import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.modules.bahia_sem_fome.services.auditoria_service import (
    executar_auditoria_completa_pastas_locais,
    obter_ultimo_snapshot_auditoria,
    consolidar_pastas_duplicadas_segura,
    consolidar_todas_atividades_divididas,
    get_base_storage_path
)
from app.services.coletum_service import auditar_discrepancias_coletum

router = APIRouter(prefix="/api/bsf/auditoria", tags=["BSF Auditoria e Conformidade"])
logger = logging.getLogger(__name__)


@router.get("/status")
async def obter_status_auditoria():
    """Retorna o status geral de auditoria e armazenamento local."""
    try:
        base_path = get_base_storage_path()
        snapshot = obter_ultimo_snapshot_auditoria()
        return {
            "status": "online",
            "storage_path": str(base_path),
            "storage_exists": base_path.exists(),
            "ultima_auditoria": snapshot.get("data_formatada"),
            "resumo": snapshot.get("resumo", {})
        }
    except Exception as e:
        logger.error(f"Erro ao obter status de auditoria: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/relatorio")
async def obter_relatorio_auditoria(
    tecnico: Optional[str] = Query(None, description="Filtro por técnico"),
    status: Optional[str] = Query(None, description="Filtro por status (COMPLETO, PENDENTE_ATESTE, PENDENTE_COLETUM, VAZIA)"),
    atividade: Optional[str] = Query(None, description="Filtro por categoria de atividade (ex: PLANO PRODUTIVO, SOCIOECONOMICO)"),
    apenas_duplicados: bool = Query(False, description="Exibir apenas beneficiários com pastas duplicadas")
):
    """
    Retorna o relatório completo de auditoria das pastas locais,
    com suporte a filtros por técnico, status de conformidade e categoria de atividade.
    """
    try:
        snapshot = obter_ultimo_snapshot_auditoria()
        detalhes = snapshot.get("detalhes_beneficiarios", [])

        if tecnico:
            tec_upper = tecnico.upper()
            detalhes = [d for d in detalhes if tec_upper in d.get("tecnico", "").upper()]

        if atividade:
            ativ_upper = atividade.upper()
            detalhes_filtrados = []
            for d in detalhes:
                atividades = [a for a in d.get("atividades", []) if ativ_upper in a.get("categoria", "").upper() or ativ_upper in a.get("pasta_atividade", "").upper()]
                if atividades:
                    d_copy = dict(d)
                    d_copy["atividades"] = atividades
                    detalhes_filtrados.append(d_copy)
            detalhes = detalhes_filtrados

        if status:
            status_upper = status.upper()
            detalhes_filtrados = []
            for d in detalhes:
                atividades = [a for a in d.get("atividades", []) if a.get("status") == status_upper]
                if atividades:
                    d_copy = dict(d)
                    d_copy["atividades"] = atividades
                    detalhes_filtrados.append(d_copy)
            detalhes = detalhes_filtrados

        return {
            "timestamp": snapshot.get("timestamp"),
            "data_formatada": snapshot.get("data_formatada"),
            "resumo": snapshot.get("resumo"),
            "duplicidades_detectadas": snapshot.get("duplicidades_detectadas", []),
            "tecnicos": snapshot.get("tecnicos", {}),
            "detalhes": detalhes
        }
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de auditoria: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar relatório de auditoria.")


@router.post("/executar-local")
async def disparar_auditoria_local(auto_consolidar: bool = False):
    """
    Dispara imediatamente a varredura e auditoria no disco local em thread separada.
    Pode opcionalmente consolidar automaticamente pastas duplicadas por acentos.
    """
    try:
        resultado = await asyncio.to_thread(
            executar_auditoria_completa_pastas_locais,
            auto_consolidar_acentos=auto_consolidar
        )
        return {
            "status": "sucesso",
            "mensagem": "Auditoria local executada com sucesso.",
            "resumo": resultado.get("resumo"),
            "duplicidades_encontradas": len(resultado.get("duplicidades_detectadas", []))
        }
    except Exception as e:
        logger.error(f"Erro na execução da auditoria local: {e}")
        raise HTTPException(status_code=500, detail=f"Falha na varredura: {str(e)}")


def _executar_consolidacao_pastas():
    base_path = get_base_storage_path()
    if not base_path.exists():
        raise HTTPException(status_code=404, detail="Diretório base de técnicos não localizado.")

    pastas_consolidadas_total = 0
    arquivos_movidos_total = 0

    # Varre cada técnico e comunidade
    for tec_dir in base_path.iterdir():
        if tec_dir.is_dir():
            doc_ativ = tec_dir / "documentos-atividades"
            alvo = doc_ativ if doc_ativ.exists() else tec_dir

            # 1. Consolida comunidades do técnico
            res_com = consolidar_pastas_duplicadas_segura(alvo)
            pastas_consolidadas_total += len(res_com.get("pastas_removidas", []))
            arquivos_movidos_total += res_com.get("arquivos_movidos", 0)

            # 2. Consolida beneficiários dentro de cada comunidade
            for com_dir in alvo.iterdir():
                if com_dir.is_dir():
                    res_ben = consolidar_pastas_duplicadas_segura(com_dir)
                    pastas_consolidadas_total += len(res_ben.get("pastas_removidas", []))
                    arquivos_movidos_total += res_ben.get("arquivos_movidos", 0)

    # 3. Consolida atividades complementares divididas (Ateste em uma pasta e Coletum em outra)
    res_ativ = consolidar_todas_atividades_divididas(base_path)
    pastas_consolidadas_total += res_ativ.get("total_pastas_removidas", 0)
    arquivos_movidos_total += res_ativ.get("total_arquivos_movidos", 0)
    total_atividades_unificadas = res_ativ.get("total_atividades_mescladas", 0)

    # Re-executa auditoria para atualizar snapshot em memória
    executar_auditoria_completa_pastas_locais()

    return {
        "status": "sucesso",
        "mensagem": f"Consolidação concluída com sucesso! {total_atividades_unificadas} atividades unificadas (Ateste + Coletum), {pastas_consolidadas_total} pastas duplicadas removidas e {arquivos_movidos_total} arquivos remanejados.",
        "pastas_removidas": pastas_consolidadas_total,
        "arquivos_movidos": arquivos_movidos_total,
        "atividades_unificadas": total_atividades_unificadas
    }


@router.post("/consolidar-duplicados")
async def consolidar_pastas_duplicadas():
    """
    Executa a unificação e consolidação segura de todas as pastas que divergem apenas por acentos.
    Preserva todos os arquivos e remove pastas vazias redundantes.
    """
    try:
        resultado = await asyncio.to_thread(_executar_consolidacao_pastas)
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na consolidação de pastas duplicadas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao consolidar pastas: {str(e)}")


@router.get("/coletum-discrepancias")
async def obter_discrepancias_coletum():
    """
    Consulta a API Coletum v2 e cruza as respostas com os beneficiários cadastrados.
    Retorna a lista de itens com status (SINCRONIZADO, ATENCAO_REVISAO_MANUAL, AVISO_DATA, NAO_ENCONTRADO).
    """
    try:
        resultado = await auditar_discrepancias_coletum()
        return resultado
    except Exception as e:
        logger.error(f"Erro ao auditar discrepâncias do Coletum: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao cruzar dados com o Coletum: {str(e)}")


def _processar_e_organizar_sigater(content: bytes, filename: str, atividade_padrao: str):
    from app.modules.bahia_sem_fome.services.sigater_service import (
        processar_pacote_zip_sigater,
        organizar_ateste_no_disco_local,
        extrair_metadados_ateste_pdf
    )
    nome = filename.lower()
    if nome.endswith('.zip'):
        res = processar_pacote_zip_sigater(content, atividade_padrao=atividade_padrao)
    elif nome.endswith('.pdf'):
        meta = extrair_metadados_ateste_pdf(content, filename)
        res_item = organizar_ateste_no_disco_local(
            pdf_bytes=content,
            nome_beneficiario=meta["beneficiario"],
            comunidade=meta["comunidade"],
            tecnico=meta["tecnico"],
            data_atividade=meta["data"],
            atividade_nome=meta["atividade"] or atividade_padrao
        )
        res = {
            "sucesso": True,
            "total_processados": 1,
            "total_erros": 0,
            "processados": [res_item],
            "erros": []
        }
    else:
        raise HTTPException(status_code=400, detail="Formato não suportado. Envie um arquivo .ZIP ou .PDF.")

    # Re-executa a auditoria para atualizar os cards imediatamente
    executar_auditoria_completa_pastas_locais()
    return res


@router.post("/importar-lote-sigater")
async def importar_lote_sigater(
    file: UploadFile = File(...),
    atividade_padrao: str = Form("PLANO PRODUTIVO")
):
    """
    Recebe um arquivo ZIP ou PDF único do SIGATER, extrai os dados de cada ateste
    e distribui automaticamente nas pastas dos beneficiários correspondentes em background thread.
    """
    try:
        content = await file.read()
        res = await asyncio.to_thread(_processar_e_organizar_sigater, content, file.filename, atividade_padrao)

        return {
            "status": "sucesso",
            "mensagem": f"Importação concluída: {res.get('total_processados', 0)} atestes organizados nas pastas locais com sucesso.",
            "total_processados": res.get("total_processados", 0),
            "total_erros": res.get("total_erros", 0),
            "erros": res.get("erros", [])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao importar lote do SIGATER: {e}")
        raise HTTPException(status_code=500, detail=f"Falha no processamento do lote: {str(e)}")

