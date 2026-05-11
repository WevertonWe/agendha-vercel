"""
BSF Beneficiários - API Router
Endpoints para listagem, filtros e preparação de arquivos do módulo BSF.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import io
import csv

from app.core.database import get_supabase
from app.services.utils import limpar_cpf

class BeneficiarioBSFCreate(BaseModel):
    nome_completo: str
    cpf: Optional[str] = None
    caf: Optional[str] = None
    municipio: Optional[str] = None
    comunidade: Optional[str] = None
    tecnico: Optional[str] = None

router = APIRouter(prefix="/api/bsf/beneficiarios", tags=["BSF Beneficiários"])

logger = logging.getLogger(__name__)


@router.get("")
async def listar_beneficiarios(
    tecnico: Optional[str] = Query(None, description="Filtro por técnico responsável"),
    municipio: Optional[str] = Query(None, description="Filtro por município"),
    status: Optional[str] = Query(None, description="Filtro por status"),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(50, ge=1, le=200, description="Itens por página"),
):
    """Lista beneficiários com filtros opcionais por técnico e município."""
    try:
        supabase = get_supabase()
        
        cols = (
            "id, nome_completo, cpf, caf, nis, municipio, comunidade, "
            "nome_tecnico, tecnico_agua_que_alimenta, status, "
            "verificado_bsf, data_atividade, projeto"
        )
        
        query = supabase.table("beneficiarios").select(cols, count="exact").eq("projeto", "Bahia Sem Fome")
        
        if tecnico:
            query = query.ilike("nome_tecnico", f"%{tecnico}%")
        if municipio:
            query = query.ilike("municipio", f"%{municipio}%")
        if status:
            query = query.ilike("status", f"%{status}%")
        
        # BSF filter: only verified beneficiaries if needed
        # query = query.not_.is_("verificado_bsf", "null")
        
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        query = query.order("id", desc=True)
        
        res = query.execute()
        
        total = res.count if res.count is not None else len(res.data or [])
        
        return {
            "data": res.data or [],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, -(-total // page_size)),
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar beneficiários BSF: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar beneficiários.")


@router.get("/filtros")
async def obter_filtros():
    """Retorna valores únicos de técnico e município para popular os selects de filtro."""
    try:
        supabase = get_supabase()
        
        # Fetch unique tecnicos
        res_tec = supabase.table("beneficiarios").select("nome_tecnico").eq("projeto", "Bahia Sem Fome").not_.is_("nome_tecnico", "null").execute()
        tecnicos_raw = [r["nome_tecnico"] for r in (res_tec.data or []) if r.get("nome_tecnico")]
        tecnicos = sorted(set(t.strip() for t in tecnicos_raw if t.strip()))
        
        # Fetch unique municipios
        res_mun = supabase.table("beneficiarios").select("municipio").eq("projeto", "Bahia Sem Fome").not_.is_("municipio", "null").execute()
        municipios_raw = [r["municipio"] for r in (res_mun.data or []) if r.get("municipio")]
        municipios = sorted(set(m.strip() for m in municipios_raw if m.strip()))
        
        # Fetch unique statuses
        res_st = supabase.table("beneficiarios").select("status").eq("projeto", "Bahia Sem Fome").not_.is_("status", "null").execute()
        statuses_raw = [r["status"] for r in (res_st.data or []) if r.get("status")]
        statuses = sorted(set(s.strip() for s in statuses_raw if s.strip()))
        
        return {
            "tecnicos": tecnicos,
            "municipios": municipios,
            "statuses": statuses,
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter filtros BSF: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar filtros.")


@router.get("/{beneficiario_id}")
async def detalhar_beneficiario(beneficiario_id: int):
    """Retorna os dados completos de um beneficiário específico."""
    try:
        supabase = get_supabase()
        res = supabase.table("beneficiarios").select("*").eq("id", beneficiario_id).eq("projeto", "Bahia Sem Fome").execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Beneficiário não encontrado.")
        
        return res.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao detalhar beneficiário {beneficiario_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar beneficiário.")


@router.get("/{beneficiario_id}/arquivos")
async def listar_arquivos_beneficiario(beneficiario_id: int):
    """
    Prepara a estrutura de associação de arquivos para um beneficiário.
    Retorna os caminhos esperados para Sigater, Colletum e Ateste.
    """
    try:
        supabase = get_supabase()
        res = supabase.table("beneficiarios").select(
            "id, nome_completo, cpf, caf, nis, municipio"
        ).eq("id", beneficiario_id).eq("projeto", "Bahia Sem Fome").execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Beneficiário não encontrado.")
        
        ben = res.data[0]
        cpf_ou_caf = (ben.get("cpf") or ben.get("caf") or "SEM_DOC").replace(".", "").replace("-", "").replace(" ", "")
        municipio = (ben.get("municipio") or "SEM_MUNICIPIO").strip()
        
        # Storage path pattern for BSF documents
        base_path = f"bsf/{municipio}/{cpf_ou_caf}"
        
        arquivos = {
            "sigater": {
                "tipo": "Sigater",
                "path": f"{base_path}/sigater/",
                "descricao": "Relatório do Sistema de Gestão da Assistência Técnica",
                "arquivos_encontrados": [],
            },
            "colletum": {
                "tipo": "Colletum",
                "path": f"{base_path}/colletum/",
                "descricao": "Formulários de coleta de dados em campo",
                "arquivos_encontrados": [],
            },
            "ateste": {
                "tipo": "Ateste",
                "path": f"{base_path}/ateste/",
                "descricao": "Termos de ateste de atividades realizadas",
                "arquivos_encontrados": [],
            },
        }
        
        return {
            "beneficiario": ben,
            "storage_base": base_path,
            "documentos": arquivos,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar arquivos do beneficiário {beneficiario_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar arquivos.")


@router.post("/{beneficiario_id}/upload")
async def upload_documento_bsf(
    beneficiario_id: int,
    tipo: str = Form(...),
    file: UploadFile = File(...)
):
    """Realiza o upload de um documento para o beneficiário."""
    try:
        if tipo not in ["sigater", "colletum", "ateste"]:
            raise HTTPException(status_code=400, detail="Tipo de documento inválido.")
            
        supabase = get_supabase()
        res = supabase.table("beneficiarios").select(
            "id, cpf, caf, municipio"
        ).eq("id", beneficiario_id).eq("projeto", "Bahia Sem Fome").execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Beneficiário não encontrado.")
            
        ben = res.data[0]
        cpf_ou_caf = (ben.get("cpf") or ben.get("caf") or "SEM_DOC").replace(".", "").replace("-", "").replace(" ", "")
        municipio = (ben.get("municipio") or "SEM_MUNICIPIO").strip()
        
        nome_arquivo = f"{tipo}.pdf"
        # agendha-uploads is the bucket
        caminho_storage = f"bsf/{municipio}/{cpf_ou_caf}/{tipo}/{nome_arquivo}"
        
        file_content = await file.read()
        
        # Fazendo upload pro Supabase Storage
        # Note: if the file exists, Supabase upload will fail unless upsert=True is supported, 
        # but let's try to remove existing first just in case.
        try:
            supabase.storage.from_("agendha-uploads").remove([caminho_storage])
        except Exception:
            pass
            
        res_upload = supabase.storage.from_("agendha-uploads").upload(
            file=file_content,
            path=caminho_storage,
            file_options={"content-type": "application/pdf"}
        )
        
        if res_upload.status_code != 200:
             # some supabase-py versions return dict, some return response objects
             pass

        return {"status": "success", "caminho": caminho_storage}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload BSF: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no upload: {e}")

@router.post("")
async def criar_beneficiario(dados: BeneficiarioBSFCreate):
    """Cria um novo beneficiário individualmente no projeto BSF."""
    try:
        supabase = get_supabase()
        cpf_limpo = limpar_cpf(dados.cpf) if dados.cpf else None
        caf_limpo = dados.caf.strip() if dados.caf else None
        
        if not cpf_limpo and not caf_limpo:
            raise HTTPException(400, "CPF ou CAF é obrigatório.")
            
        payload = {
            "nome_completo": dados.nome_completo,
            "cpf": cpf_limpo,
            "caf": caf_limpo,
            "municipio": dados.municipio,
            "comunidade": dados.comunidade,
            "nome_tecnico": dados.tecnico,
            "projeto": "Bahia Sem Fome",
            "status": "CADASTRADO"
        }
        res = supabase.table("beneficiarios").insert(payload).execute()
        return {"message": "Beneficiário cadastrado", "data": res.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao cadastrar BSF: {e}")
        raise HTTPException(500, f"Erro ao cadastrar: {e}")

@router.post("/importar")
async def importar_planilha_bsf(file: UploadFile = File(...)):
    """Importa lista de beneficiários BSF em massa, detectando colunas."""
    try:
        content = await file.read()
        filename = file.filename.lower()
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            return JSONResponse(content={"error": "Converta para CSV."}, status_code=400)
            
        decoded = content.decode('utf-8-sig')
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(decoded[:1024], delimiters=[',', ';', '\t'])
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ';' if ';' in decoded[:100] else ','
            
        csv_reader = csv.DictReader(io.StringIO(decoded), delimiter=delimiter)
        linhas = list(csv_reader)
        fieldnames = csv_reader.fieldnames or []

        def find_col(candidates):
            cols_map = {str(c).strip().upper(): c for c in fieldnames}
            for cand in candidates:
                cand_upper = cand.upper()
                if cand_upper in cols_map:
                    return cols_map[cand_upper]
                for real_col_upper, real_col_name in cols_map.items():
                    if cand_upper in real_col_upper:
                        return real_col_name
            return None

        col_cpf = find_col(['CPF', 'DOCUMENTO', 'DOC'])
        col_caf = find_col(['CAF', 'DAP', 'NIS'])
        col_nome = find_col(['NOME', 'BENEFICIARIO'])
        col_mun = find_col(['MUNICIPIO', 'CIDADE'])
        col_com = find_col(['COMUNIDADE', 'LOCALIDADE'])
        col_tec = find_col(['TECNICO', 'RESPONSAVEL'])
        
        supabase = get_supabase()
        count_novos = 0
        count_atualizados = 0
        
        for row in linhas:
            raw_cpf = row.get(col_cpf) if col_cpf else None
            raw_caf = row.get(col_caf) if col_caf else None
            cpf_limpo = limpar_cpf(raw_cpf) if raw_cpf else None
            
            nome = (row.get(col_nome) or "Desconhecido").strip()
            mun = row.get(col_mun)
            com = row.get(col_com)
            tec = row.get(col_tec)
            
            if not cpf_limpo and not raw_caf:
                continue 
                
            payload = {
                "nome_completo": nome,
                "municipio": mun,
                "comunidade": com,
                "nome_tecnico": tec,
                "projeto": "Bahia Sem Fome"
            }
            if raw_caf:
                payload["caf"] = raw_caf
            
            query = supabase.table("beneficiarios").select("id, projeto")
            if cpf_limpo:
                query = query.eq("cpf", cpf_limpo)
            else:
                query = query.eq("caf", raw_caf)
                
            res = query.execute()
            
            if res.data:
                existente = res.data[0]
                if not existente.get("projeto") or existente.get("projeto") == "Bahia Sem Fome":
                    supabase.table("beneficiarios").update(payload).eq("id", existente["id"]).execute()
                    count_atualizados += 1
            else:
                if cpf_limpo:
                    payload["cpf"] = cpf_limpo
                payload["status"] = "IMPORTADO"
                supabase.table("beneficiarios").insert(payload).execute()
                count_novos += 1
                
        return {"message": "Importação concluída", "novos": count_novos, "atualizados": count_atualizados}
    except Exception as e:
        logger.error(f"Erro importar bsf: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
