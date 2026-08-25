"""
BSF Auditoria e Conformidade - API Router
Rotas para consulta e execução de auditoria local de pastas (Ateste + Coletum),
deduplicação de diretórios com acentos e cruzamento inteligente com a API Coletum v2.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from app.modules.bahia_sem_fome.services.auditoria_service import (
    executar_auditoria_completa_pastas_locais,
    obter_ultimo_snapshot_auditoria,
    consolidar_pastas_duplicadas_segura,
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
    apenas_duplicados: bool = Query(False, description="Exibir apenas beneficiários com pastas duplicadas")
):
    """
    Retorna o relatório completo de auditoria das pastas locais,
    com suporte a filtros por técnico e status de conformidade documental.
    """
    try:
        snapshot = obter_ultimo_snapshot_auditoria()
        detalhes = snapshot.get("detalhes_beneficiarios", [])

        if tecnico:
            tec_upper = tecnico.upper()
            detalhes = [d for d in detalhes if tec_upper in d.get("tecnico", "").upper()]

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
    Dispara imediatamente a varredura e auditoria no disco local.
    Pode opcionalmente consolidar automaticamente pastas duplicadas por acentos.
    """
    try:
        resultado = executar_auditoria_completa_pastas_locais(auto_consolidar_acentos=auto_consolidar)
        return {
            "status": "sucesso",
            "mensagem": "Auditoria local executada com sucesso.",
            "resumo": resultado.get("resumo"),
            "duplicidades_encontradas": len(resultado.get("duplicidades_detectadas", []))
        }
    except Exception as e:
        logger.error(f"Erro na execução da auditoria local: {e}")
        raise HTTPException(status_code=500, detail=f"Falha na varredura: {str(e)}")


@router.post("/consolidar-duplicados")
async def consolidar_pastas_duplicadas():
    """
    Executa a unificação e consolidação segura de todas as pastas que divergem apenas por acentos.
    Preserva todos os arquivos e remove pastas vazias redundantes.
    """
    try:
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

        # Re-executa auditoria para atualizar snapshot em memória
        executar_auditoria_completa_pastas_locais()

        return {
            "status": "sucesso",
            "mensagem": f"Consolidação concluída. {pastas_consolidadas_total} pastas duplicadas unificadas e {arquivos_movidos_total} arquivos remanejados com segurança.",
            "pastas_removidas": pastas_consolidadas_total,
            "arquivos_movidos": arquivos_movidos_total
        }
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
