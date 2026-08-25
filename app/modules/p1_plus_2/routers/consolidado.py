import logging
from collections import defaultdict
from fastapi import APIRouter, HTTPException
from app.core.database import fetch_all

router = APIRouter(prefix="/api/p1-2/consolidado", tags=["P1+2 - Consolidado"])
logger = logging.getLogger(__name__)

@router.get("/kpis")
async def obter_kpis_consolidado():
    try:
        beneficiarios = fetch_all("p12_beneficiarios")
        monitoramentos = fetch_all("p12_monitoramentos")
        plano = fetch_all("p12_plano_produtivo_dados")
        cronograma = fetch_all("p12_cronograma_execucao")
        
        total_ben = len(beneficiarios)
        ben_ativos = len([b for b in beneficiarios if str(b.get("status") or "").lower() == "ativo"])
        
        # Monitoramentos por tipo
        tot_gapa = len([m for m in monitoramentos if str(m.get("tipo") or "").upper() == "GAPA"])
        tot_sisma = len([m for m in monitoramentos if str(m.get("tipo") or "").upper() == "SISMA"])
        tot_intercambio = len([m for m in monitoramentos if str(m.get("tipo") or "").upper() in ["INTERCAMBIO", "INTERCÂMBIO"]])
        
        # Plano Produtivo Parcelas
        p1_pagas = len([p for p in plano if str(p.get("status_parcela_1") or "").lower() in ["pago", "paga", "liberado", "liberada", "concluído", "concluido"]])
        p2_pagas = len([p for p in plano if str(p.get("status_parcela_2") or "").lower() in ["pago", "paga", "liberado", "liberada", "concluído", "concluido"]])
        
        # Planejamento Físico
        meta_total = sum(int(c.get("meta_planejada") or 0) for c in cronograma)
        exec_total = sum(int(c.get("qtd_executada") or 0) for c in cronograma)
        percent_exec = round((exec_total / meta_total * 100), 1) if meta_total > 0 else 0.0
        
        return {
            "beneficiarios": {
                "total": total_ben,
                "ativos": ben_ativos
            },
            "monitoramento": {
                "total": len(monitoramentos),
                "gapa": tot_gapa,
                "sisma": tot_sisma,
                "intercambio": tot_intercambio
            },
            "plano_produtivo": {
                "total_linhas": len(plano),
                "parcela_1_concluida": p1_pagas,
                "parcela_2_concluida": p2_pagas
            },
            "planejamento": {
                "meta": meta_total,
                "executado": exec_total,
                "percentual": percent_exec
            }
        }
    except Exception as e:
        logger.error(f"Erro ao obter KPIs consolidados P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/por-municipio")
async def obter_consolidado_por_municipio():
    try:
        beneficiarios = fetch_all("p12_beneficiarios")
        monitoramentos = fetch_all("p12_monitoramentos")
        plano = fetch_all("p12_plano_produtivo_dados")
        
        municipios_map = defaultdict(lambda: {
            "municipio": "",
            "beneficiarios_total": 0,
            "beneficiarios_ativos": 0,
            "gapa_count": 0,
            "sisma_count": 0,
            "intercambio_count": 0,
            "p1_pagas": 0,
            "p2_pagas": 0
        })
        
        for b in beneficiarios:
            m = b.get("municipio") or "Não Informado"
            municipios_map[m]["municipio"] = m
            municipios_map[m]["beneficiarios_total"] += 1
            if str(b.get("status") or "").lower() == "ativo":
                municipios_map[m]["beneficiarios_ativos"] += 1
                
        for m in monitoramentos:
            mun = m.get("municipio") or "Não Informado"
            tipo = str(m.get("tipo") or "").upper()
            if tipo == "GAPA":
                municipios_map[mun]["gapa_count"] += 1
            elif tipo == "SISMA":
                municipios_map[mun]["sisma_count"] += 1
            elif tipo in ["INTERCAMBIO", "INTERCÂMBIO"]:
                municipios_map[mun]["intercambio_count"] += 1
                
        for p in plano:
            mun = p.get("municipio") or "Não Informado"
            if str(p.get("status_parcela_1") or "").lower() in ["pago", "paga", "liberado", "liberada"]:
                municipios_map[mun]["p1_pagas"] += 1
            if str(p.get("status_parcela_2") or "").lower() in ["pago", "paga", "liberado", "liberada"]:
                municipios_map[mun]["p2_pagas"] += 1
                
        resultado = sorted(list(municipios_map.values()), key=lambda x: x["beneficiarios_total"], reverse=True)
        return resultado
    except Exception as e:
        logger.error(f"Erro ao obter consolidado por município P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/graficos-dados")
async def obter_dados_graficos():
    try:
        beneficiarios = fetch_all("p12_beneficiarios")
        monitoramentos = fetch_all("p12_monitoramentos")
        plano = fetch_all("p12_plano_produtivo_dados")
        
        # 1. Distribuição por Município
        mun_counts = defaultdict(int)
        for b in beneficiarios:
            m = b.get("municipio") or "Outros"
            mun_counts[m] += 1
            
        # 2. Status Geral dos Beneficiários
        status_counts = defaultdict(int)
        for b in beneficiarios:
            st = b.get("status") or "Ativo"
            status_counts[st] += 1
            
        # 3. Status das Parcelas (1ª e 2ª)
        p1_status = defaultdict(int)
        p2_status = defaultdict(int)
        for p in plano:
            st1 = p.get("status_parcela_1") or "Pendente"
            st2 = p.get("status_parcela_2") or "Pendente"
            p1_status[st1] += 1
            p2_status[st2] += 1
            
        # 4. Monitoramentos
        mon_counts = {
            "GAPA": len([m for m in monitoramentos if str(m.get("tipo") or "").upper() == "GAPA"]),
            "SISMA": len([m for m in monitoramentos if str(m.get("tipo") or "").upper() == "SISMA"]),
            "INTERCÂMBIO": len([m for m in monitoramentos if str(m.get("tipo") or "").upper() in ["INTERCAMBIO", "INTERCÂMBIO"]])
        }
        
        return {
            "municipios": {
                "labels": list(mun_counts.keys()),
                "data": list(mun_counts.values())
            },
            "status_beneficiarios": {
                "labels": list(status_counts.keys()),
                "data": list(status_counts.values())
            },
            "parcelas": {
                "labels": list(set(list(p1_status.keys()) + list(p2_status.keys()))),
                "p1_data": [p1_status[k] for k in list(set(list(p1_status.keys()) + list(p2_status.keys())))],
                "p2_data": [p2_status[k] for k in list(set(list(p1_status.keys()) + list(p2_status.keys())))]
            },
            "monitoramentos": {
                "labels": list(mon_counts.keys()),
                "data": list(mon_counts.values())
            }
        }
    except Exception as e:
        logger.error(f"Erro ao obter dados para gráficos P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")