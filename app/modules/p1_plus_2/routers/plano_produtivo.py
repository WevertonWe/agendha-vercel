import logging
import json
import io
import pandas as pd
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.core.database import get_supabase, fetch_all, db_insert, db_update, db_delete
from app.modules.p1_plus_2.models import (
    PlanoProdutivoSalvarCelula, PlanoProdutivoColunaCreate, PlanoProdutivoLinhaCreate
)

router = APIRouter(prefix="/api/p1-2/plano-produtivo", tags=["P1+2 - Plano Produtivo"])
logger = logging.getLogger(__name__)

# Colunas padrão do sistema
COLUNAS_PADRAO = [
    {"chave": "nome_beneficiario", "chave_coluna": "nome_beneficiario", "titulo": "Nome do Beneficiário", "titulo_coluna": "Nome do Beneficiário", "tipo": "texto", "tipo_coluna": "texto", "fixa": True},
    {"chave": "municipio", "chave_coluna": "municipio", "titulo": "Município", "titulo_coluna": "Município", "tipo": "texto", "tipo_coluna": "texto", "fixa": True},
    {"chave": "comunidade", "chave_coluna": "comunidade", "titulo": "Comunidade", "titulo_coluna": "Comunidade", "tipo": "texto", "tipo_coluna": "texto", "fixa": True},
    {"chave": "status_parcela_1", "chave_coluna": "status_parcela_1", "titulo": "1ª Parcela", "titulo_coluna": "Status 1ª Parcela", "tipo": "status_p1", "tipo_coluna": "status_p1", "fixa": True},
    {"chave": "status_parcela_2", "chave_coluna": "status_parcela_2", "titulo": "2ª Parcela", "titulo_coluna": "Status 2ª Parcela", "tipo": "status_p2", "tipo_coluna": "status_p2", "fixa": True},
    {"chave": "observacoes", "chave_coluna": "observacoes", "titulo": "Observações", "titulo_coluna": "Observações", "tipo": "texto", "tipo_coluna": "texto", "fixa": True}
]

OPCOES_STATUS_PARCELA = [
    "Pendente",
    "Em Análise",
    "Liberado",
    "Pago",
    "Prestado Contas",
    "Bloqueado"
]

@router.get("/dados")
async def obter_dados_plano(
    search: Optional[str] = None,
    status_p1: Optional[str] = None,
    status_p2: Optional[str] = None
):
    try:
        # Busca colunas dinâmicas configuradas
        colunas_custom = fetch_all("p12_plano_produtivo_config")
        colunas_custom.sort(key=lambda x: int(x.get("ordem") or 0))
        
        todas_colunas = list(COLUNAS_PADRAO)
        for cc in colunas_custom:
            ch = cc.get("chave_coluna") or cc.get("chave")
            tit = cc.get("titulo_coluna") or cc.get("titulo") or ch
            tip = cc.get("tipo_coluna") or cc.get("tipo") or "texto"
            todas_colunas.append({
                "chave": ch,
                "chave_coluna": ch,
                "titulo": tit,
                "titulo_coluna": tit,
                "tipo": tip,
                "tipo_coluna": tip,
                "fixa": False
            })

            
        linhas = fetch_all("p12_plano_produtivo_dados")
        
        # Se estiver vazio, popula automaticamente a partir dos beneficiários existentes
        if not linhas:
            beneficiarios = fetch_all("p12_beneficiarios")
            if beneficiarios:
                for b in beneficiarios:
                    nome = b.get("nome_completo") or b.get("nome_familiar") or f"Beneficiário #{b.get('id')}"
                    novo_dado = {
                        "beneficiario_id": b.get("id"),
                        "nome_beneficiario": nome,
                        "municipio": b.get("municipio") or "",
                        "comunidade": b.get("comunidade") or "",
                        "status_parcela_1": "Pendente",
                        "status_parcela_2": "Pendente",
                        "observacoes": "",
                        "campos_dinamicos": "{}"
                    }
                    db_insert("p12_plano_produtivo_dados", novo_dado)
                linhas = fetch_all("p12_plano_produtivo_dados")
                
        # Parse dos campos dinâmicos JSON
        for l in linhas:
            cd = l.get("campos_dinamicos")
            if isinstance(cd, str):
                try:
                    l["campos_dinamicos_dict"] = json.loads(cd)
                except Exception:
                    l["campos_dinamicos_dict"] = {}
            elif isinstance(cd, dict):
                l["campos_dinamicos_dict"] = cd
            else:
                l["campos_dinamicos_dict"] = {}
                
        # Filtros
        if search:
            s_clean = search.lower().strip()
            linhas = [
                l for l in linhas if
                (l.get("nome_beneficiario") and s_clean in str(l["nome_beneficiario"]).lower()) or
                (l.get("municipio") and s_clean in str(l["municipio"]).lower()) or
                (l.get("comunidade") and s_clean in str(l["comunidade"]).lower()) or
                (l.get("observacoes") and s_clean in str(l["observacoes"]).lower())
            ]
            
        if status_p1 and status_p1 != "TODOS":
            linhas = [l for l in linhas if str(l.get("status_parcela_1") or "").lower() == status_p1.lower()]
            
        if status_p2 and status_p2 != "TODOS":
            linhas = [l for l in linhas if str(l.get("status_parcela_2") or "").lower() == status_p2.lower()]
            
        return {
            "colunas": todas_colunas,
            "status_opcoes": OPCOES_STATUS_PARCELA,
            "total_linhas": len(linhas),
            "linhas": linhas
        }
    except Exception as e:
        logger.error(f"Erro ao obter dados do plano produtivo P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.post("/salvar-celula")
async def salvar_celula(payload: PlanoProdutivoSalvarCelula):
    try:
        dados = fetch_all("p12_plano_produtivo_dados")
        linha = next((d for d in dados if d.get("id") == payload.linha_id), None)
        if not linha:
            raise HTTPException(status_code=404, detail="Linha não encontrada")
            
        campos_fixos = ["nome_beneficiario", "municipio", "comunidade", "status_parcela_1", "status_parcela_2", "observacoes"]
        
        if payload.campo in campos_fixos:
            update_data = {payload.campo: payload.valor}
            db_update("p12_plano_produtivo_dados", payload.linha_id, update_data)
        else:
            # Campo dinâmico
            cd = linha.get("campos_dinamicos")
            dict_cd = {}
            if isinstance(cd, str):
                try:
                    dict_cd = json.loads(cd)
                except Exception:
                    pass
            elif isinstance(cd, dict):
                dict_cd = cd
                
            dict_cd[payload.campo] = payload.valor
            db_update("p12_plano_produtivo_dados", payload.linha_id, {"campos_dinamicos": json.dumps(dict_cd, ensure_ascii=False)})
            
        return {"status": "ok", "message": "Célula atualizada com sucesso!"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao salvar célula: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar célula: {e}")

@router.post("/coluna", status_code=201)
async def adicionar_coluna(payload: PlanoProdutivoColunaCreate):
    try:
        import re
        chave = re.sub(r'[^a-zA-Z0-9_]', '_', payload.chave_coluna.lower()).strip('_')
        if not chave:
            chave = f"col_{int(pd.Timestamp.now().timestamp())}"
            
        # Verifica se já existe
        existentes = fetch_all("p12_plano_produtivo_config")
        if any(c.get("chave_coluna") == chave for c in existentes):
            raise HTTPException(status_code=400, detail="Já existe uma coluna com esta chave.")
            
        nova_col = {
            "chave_coluna": chave,
            "titulo_coluna": payload.titulo_coluna,
            "tipo_coluna": payload.tipo_coluna or "texto",
            "ordem": len(existentes) + 1
        }
        novo = db_insert("p12_plano_produtivo_config", nova_col)
        return {"message": "Coluna adicionada com sucesso!", "coluna": novo}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar coluna no plano produtivo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar coluna: {e}")

@router.delete("/coluna/{chave}")
async def remover_coluna(chave: str):
    try:
        db_delete("p12_plano_produtivo_config", chave, id_col="chave_coluna")
        return {"message": f"Coluna '{chave}' removida com sucesso!"}
    except Exception as e:
        logger.error(f"Erro ao remover coluna: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao remover coluna: {e}")

@router.post("/linha", status_code=201)
async def adicionar_linha(payload: PlanoProdutivoLinhaCreate):
    try:
        dados = {
            "beneficiario_id": payload.beneficiario_id,
            "nome_beneficiario": payload.nome_beneficiario,
            "municipio": payload.municipio or "",
            "comunidade": payload.comunidade or "",
            "status_parcela_1": payload.status_parcela_1 or "Pendente",
            "status_parcela_2": payload.status_parcela_2 or "Pendente",
            "observacoes": payload.observacoes or "",
            "campos_dinamicos": json.dumps(payload.campos_dinamicos or {}, ensure_ascii=False)
        }
        novo = db_insert("p12_plano_produtivo_dados", dados)
        return {"message": "Linha adicionada com sucesso!", "linha": novo}
    except Exception as e:
        logger.error(f"Erro ao adicionar linha: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar linha: {e}")

@router.delete("/linha/{id}")
async def remover_linha(id: int):
    try:
        db_delete("p12_plano_produtivo_dados", id)
        return {"message": "Linha removida com sucesso!"}
    except Exception as e:
        logger.error(f"Erro ao remover linha: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao remover linha: {e}")

@router.get("/exportar-excel")
async def exportar_plano_produtivo_excel():
    try:
        dados_resp = await obter_dados_planilha()
        colunas = dados_resp.get("colunas", [])
        linhas = dados_resp.get("linhas", [])
        
        lista_export = []
        for l in linhas:
            row_dict = {}
            for col in colunas:
                k = col["chave"]
                tit = col["titulo"]
                if col.get("fixa"):
                    row_dict[tit] = l.get(k, "")
                else:
                    cd = l.get("campos_dinamicos_dict", {})
                    row_dict[tit] = cd.get(k, "")
            lista_export.append(row_dict)
            
        df = pd.DataFrame(lista_export) if lista_export else pd.DataFrame([{"Mensagem": "Nenhum registro no Plano Produtivo"}])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Plano_Produtivo_P1_2")
        output.seek(0)
        
        headers = {"Content-Disposition": 'attachment; filename="plano_produtivo_p1_2.xlsx"'}
        return StreamingResponse(output, headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        logger.error(f"Erro ao exportar excel plano produtivo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar Excel: {e}")