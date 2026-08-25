import logging
import io
import pandas as pd
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse, JSONResponse
from app.core.database import get_supabase, fetch_all, db_insert, db_update, db_delete
from app.modules.p1_plus_2.models import (
    BeneficiarioP12, BeneficiarioP12Create, BeneficiarioP12Update
)
from app.services.utils import limpar_cpf, remover_acentos

router = APIRouter(prefix="/api/p1-2/beneficiarios", tags=["P1+2 - Beneficiários"])
logger = logging.getLogger(__name__)

@router.get("", response_model=dict)
async def listar_beneficiarios(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=1000),
    search: Optional[str] = None,
    municipio: Optional[str] = None,
    status: Optional[str] = None
):
    try:
        dados = fetch_all("p12_beneficiarios")
        
        # Filtros
        if search:
            s_clean = search.lower().strip()
            s_num = "".join(filter(str.isdigit, search))
            dados = [
                d for d in dados if
                (d.get("nome_completo") and s_clean in str(d["nome_completo"]).lower()) or
                (d.get("nome_familiar") and s_clean in str(d["nome_familiar"]).lower()) or
                (s_num and (s_num in "".join(filter(str.isdigit, str(d.get("cpf") or ""))) or
                            s_num in "".join(filter(str.isdigit, str(d.get("cpf_familiar") or ""))))) or
                (d.get("comunidade") and s_clean in str(d["comunidade"]).lower()) or
                (d.get("nis") and s_clean in str(d["nis"]))
            ]
            
        if municipio and municipio != "TODOS":
            m_norm = remover_acentos(municipio).lower()
            dados = [d for d in dados if d.get("municipio") and remover_acentos(str(d["municipio"])).lower() == m_norm]
            
        if status and status != "TODOS":
            dados = [d for d in dados if str(d.get("status") or "").lower() == status.lower()]
            
        total = len(dados)
        start = (page - 1) * limit
        end = start + limit
        paginados = dados[start:end]
        
        # Obter lista de municípios únicos para os filtros do frontend
        todos_municipios = sorted(list(set([d.get("municipio") for d in fetch_all("p12_beneficiarios") if d.get("municipio")])))
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            "municipios": todos_municipios,
            "dados": paginados
        }
    except Exception as e:
        logger.error(f"Erro ao listar beneficiários P1+2: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@router.get("/{id}")
async def obter_beneficiario(id: int):
    try:
        supabase = get_supabase()
        res = supabase.table("p12_beneficiarios").select("*").eq("id", id).execute()
        if res.data:
            return res.data[0]
        raise HTTPException(status_code=404, detail="Beneficiário não encontrado")
    except HTTPException:
        raise
    except Exception:
        dados = fetch_all("p12_beneficiarios")
        item = next((d for d in dados if d.get("id") == id), None)
        if item:
            return item
        raise HTTPException(status_code=404, detail="Beneficiário não encontrado")

@router.post("", status_code=201)
async def criar_beneficiario(payload: BeneficiarioP12Create):
    try:
        data_dict = payload.dict()
        if data_dict.get("cpf"):
            data_dict["cpf"] = limpar_cpf(data_dict["cpf"])
        if data_dict.get("cpf_familiar"):
            data_dict["cpf_familiar"] = limpar_cpf(data_dict["cpf_familiar"])
            
        novo = db_insert("p12_beneficiarios", data_dict)
        
        # Auto sincroniza com a planilha do Plano Produtivo
        try:
            db_insert("p12_plano_produtivo_dados", {
                "beneficiario_id": novo["id"],
                "nome_beneficiario": novo.get("nome_completo") or novo.get("nome_familiar") or f"Beneficiário #{novo['id']}",
                "municipio": novo.get("municipio"),
                "comunidade": novo.get("comunidade"),
                "status_parcela_1": "Pendente",
                "status_parcela_2": "Pendente",
                "observacoes": "",
                "campos_dinamicos": "{}"
            })
        except Exception as e_sync:
            logger.warning(f"Aviso: auto-sync no plano produtivo falhou (não fatal): {e_sync}")
            
        return {"message": "Beneficiário cadastrado com sucesso!", "dados": novo}
    except Exception as e:
        logger.error(f"Erro ao criar beneficiário P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar: {e}")

@router.put("/{id}")
async def atualizar_beneficiario(id: int, payload: BeneficiarioP12Update):
    try:
        data_dict = {k: v for k, v in payload.dict().items() if v is not None}
        if "cpf" in data_dict and data_dict["cpf"]:
            data_dict["cpf"] = limpar_cpf(data_dict["cpf"])
        if "cpf_familiar" in data_dict and data_dict["cpf_familiar"]:
            data_dict["cpf_familiar"] = limpar_cpf(data_dict["cpf_familiar"])
            
        atualizado = db_update("p12_beneficiarios", id, data_dict)
            
        # Atualiza nome/município no plano produtivo também
        try:
            upd_plano = {}
            if "nome_completo" in data_dict:
                upd_plano["nome_beneficiario"] = data_dict["nome_completo"]
            if "municipio" in data_dict:
                upd_plano["municipio"] = data_dict["municipio"]
            if "comunidade" in data_dict:
                upd_plano["comunidade"] = data_dict["comunidade"]
            if upd_plano:
                db_update("p12_plano_produtivo_dados", id, upd_plano, id_col="beneficiario_id")
        except Exception:
            pass
            
        return {"message": "Beneficiário atualizado com sucesso!", "dados": atualizado}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar beneficiário P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {e}")

@router.delete("/{id}")
async def excluir_beneficiario(id: int):
    try:
        try:
            db_delete("p12_plano_produtivo_dados", id, id_col="beneficiario_id")
        except Exception:
            pass
        db_delete("p12_beneficiarios", id)
        return {"message": "Beneficiário excluído com sucesso!"}
    except Exception as e:
        logger.error(f"Erro ao excluir beneficiário P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir: {e}")


@router.get("/exportar/excel")
async def exportar_beneficiarios_excel():
    try:
        dados = fetch_all("p12_beneficiarios")
        if not dados:
            dados = [{"ID": "", "Nome Completo": "Nenhum registro encontrado", "CPF": "", "Município": "", "Comunidade": "", "Status": ""}]
        else:
            dados_formatados = []
            for d in dados:
                dados_formatados.append({
                    "ID": d.get("id"),
                    "Nome Completo": d.get("nome_completo"),
                    "Nome Familiar": d.get("nome_familiar"),
                    "CPF": d.get("cpf"),
                    "CPF Familiar": d.get("cpf_familiar"),
                    "NIS": d.get("nis"),
                    "Data Nascimento": d.get("data_nascimento"),
                    "Sexo": d.get("sexo"),
                    "Escolaridade": d.get("escolaridade"),
                    "Município": d.get("municipio"),
                    "Comunidade": d.get("comunidade"),
                    "Status": d.get("status"),
                    "Doc Status": d.get("doc_status"),
                    "Data Cadastro": d.get("data_cadastro"),
                    "Observações": d.get("observacoes")
                })
            dados = dados_formatados
            
        df = pd.DataFrame(dados)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Beneficiarios_P1_2")
        output.seek(0)
        
        headers = {"Content-Disposition": 'attachment; filename="beneficiarios_p1_2.xlsx"'}
        return StreamingResponse(output, headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        logger.error(f"Erro ao exportar excel P1+2: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar Excel: {e}")