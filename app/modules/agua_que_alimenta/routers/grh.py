import json
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from app.modules.agua_que_alimenta.services.ai_scanner import extrair_lista_presenca
from app.core.database import get_supabase
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/grh", tags=["GRH Scanner"])
logger = logging.getLogger(__name__)

@router.post("/scan-lista")
async def scan_lista_grh(file: UploadFile = File(...)):
    if not file:
         raise HTTPException(status_code=400, detail="Arquivo obrigatório")
    
    try:
        content = await file.read()
        mime_type = file.content_type or "application/pdf"
        
        if mime_type == "application/octet-stream":
            if file.filename.lower().endswith(".pdf"):
                mime_type = "application/pdf"
            elif file.filename.lower().endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            elif file.filename.lower().endswith(".png"):
                mime_type = "image/png"

        resultado_json_str = await extrair_lista_presenca(content, mime_type)
        
        try:
             dados = json.loads(resultado_json_str)
             if "erro" in dados:
                 raise HTTPException(status_code=500, detail=dados.get("erro"))

             beneficiarios_detectados = dados.get("beneficiarios_detectados", [])
             supabase = get_supabase()
             
             for item in beneficiarios_detectados:
                 item['encontrado'] = False
                 item['id_beneficiario'] = None
                 item['match_type'] = None
                 
                 nome_busca = item.get('nome_extraido')
                 cpf_busca = item.get('cpf_extraido')
                 
                 if cpf_busca:
                     cpf_limpo = "".join(filter(str.isdigit, cpf_busca))
                     if len(cpf_limpo) > 5:
                         res = supabase.table('beneficiarios').select('id, nome_familiar, nome_tecnico, cpf_familiar, cpf_tecnico').ilike('cpf_familiar', f"%{cpf_limpo}%").execute()
                         if not res.data:
                             res = supabase.table('beneficiarios').select('id, nome_familiar, nome_tecnico, cpf_familiar, cpf_tecnico').ilike('cpf_tecnico', f"%{cpf_limpo}%").execute()
                             
                         if res.data:
                             found = res.data[0]
                             item['encontrado'] = True
                             item['id_beneficiario'] = found.get('id')
                             item['match_type'] = 'CPF'
                             item['nome_banco'] = found.get('nome_familiar') or found.get('nome_tecnico')
                             continue
                             
                 if nome_busca and len(nome_busca) > 4:
                     res = supabase.table('beneficiarios').select('id, nome_familiar, nome_tecnico').ilike('nome_familiar', f"%{nome_busca}%").execute()
                     if not res.data:
                         res = supabase.table('beneficiarios').select('id, nome_familiar, nome_tecnico').ilike('nome_tecnico', f"%{nome_busca}%").execute()
                         
                     if res.data:
                         found = res.data[0]
                         item['encontrado'] = True
                         item['id_beneficiario'] = found.get('id')
                         item['match_type'] = 'NOME'
                         item['nome_banco'] = found.get('nome_familiar') or found.get('nome_tecnico')
             
             return dados

        except json.JSONDecodeError:
             return {"erro": "Falha ao decodificar resposta da IA", "raw": resultado_json_str}

    except Exception as e:
        logger.error(f"Erro no scan GRH: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

class VinculoGRH(BaseModel):
    termo_grh: str
    ids_beneficiarios: List[int]

@router.post("/vincular")
def vincular_grh_lote(dados: VinculoGRH):
    if not dados.ids_beneficiarios:
         return {"mensagem": "Nenhum beneficiário para vincular."}

    try:
        supabase = get_supabase()
        updates_count = 0
        
        for p_id in dados.ids_beneficiarios:
            res = supabase.table('beneficiarios').update({"grh": dados.termo_grh}).eq('id', p_id).execute()
            if res.data:
                updates_count += 1
                
        return {
            "mensagem": "Vinculação realizada com sucesso!",
            "afetados": updates_count
        }

    except Exception as e:
        logger.error(f"Erro ao vincular GRH: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar vínculo: {e}")

class BuscaManual(BaseModel):
    nome: str
    cpf: str = None

@router.post("/match-manual")
def buscar_beneficiario_manual(dados: BuscaManual):
    try:
        supabase = get_supabase()
        
        if dados.cpf:
            cpf_limpo = "".join(filter(str.isdigit, dados.cpf))
            if len(cpf_limpo) > 5:
                res = supabase.table('beneficiarios').select('id, nome_familiar, nome_tecnico, cpf_familiar, cpf_tecnico').ilike('cpf_familiar', f"%{cpf_limpo}%").execute()
                if not res.data:
                    res = supabase.table('beneficiarios').select('id, nome_familiar, nome_tecnico, cpf_familiar, cpf_tecnico').ilike('cpf_tecnico', f"%{cpf_limpo}%").execute()
                    
                if res.data:
                    found = res.data[0]
                    return {
                        "encontrado": True,
                        "id": found.get('id'),
                        "nome": found.get('nome_familiar') or found.get('nome_tecnico'),
                        "cpf": found.get('cpf_familiar') or found.get('cpf_tecnico'),
                        "match_type": "CPF_MANUAL"
                    }

        if dados.nome and len(dados.nome) > 2:
            nome_busca = dados.nome.strip()
            res = supabase.table('beneficiarios').select('id, nome_familiar, nome_tecnico, cpf_familiar').ilike('nome_familiar', f"%{nome_busca}%").execute()
            if not res.data:
                res = supabase.table('beneficiarios').select('id, nome_familiar, nome_tecnico, cpf_familiar').ilike('nome_tecnico', f"%{nome_busca}%").execute()
                
            if not res.data:
                primeiro_nome = nome_busca.split()[0]
                if len(primeiro_nome) > 3:
                    res = supabase.table('beneficiarios').select('id, nome_familiar, nome_tecnico, cpf_familiar').ilike('nome_familiar', f"%{primeiro_nome}%").execute()
                    if not res.data:
                        res = supabase.table('beneficiarios').select('id, nome_familiar, nome_tecnico, cpf_familiar').ilike('nome_tecnico', f"%{primeiro_nome}%").execute()
                        
            if res.data:
                found = res.data[0]
                return {
                    "encontrado": True,
                    "id": found.get('id'),
                    "nome": found.get('nome_familiar') or found.get('nome_tecnico'),
                    "cpf": found.get('cpf_familiar'),
                    "match_type": "NOME_MANUAL"
                }

        return {"encontrado": False, "mensagem": "Nenhum beneficiário encontrado."}

    except Exception as e:
        logger.error(f"Erro na busca manual: {e}")
        raise HTTPException(status_code=500, detail="Erro interno na busca.")

@router.get("/documento/{filename}")
def download_grh_documento(filename: str):
    # Redirecionar para a URL pública do Supabase Storage
    from app.core.database import get_supabase
    supabase = get_supabase()
    url = supabase.storage.from_('agendha-uploads').get_public_url(f"uploads/grh/{filename}")
    return RedirectResponse(url=url)
