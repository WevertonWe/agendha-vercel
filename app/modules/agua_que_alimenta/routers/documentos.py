import os
import uuid
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from app.core.auth.dependencies import get_current_user
from app.modules.agua_que_alimenta.models import Documento
from app.config import settings
from app.core.database import get_supabase

router = APIRouter(prefix="/api/documentos", tags=["Documentos"])
logger = logging.getLogger(__name__)

@router.get("", response_model=List[Documento])
def listar_documentos():
    try:
        supabase = get_supabase()
        res = supabase.table('documentos').select('*').order('id', desc=True).execute()
        docs = []
        for row in res.data:
            docs.append(Documento(**row))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar documentos: {e}")

@router.post("", response_model=Documento, status_code=201)
async def criar_documento(
    nome_documento: str = Form(...),
    descricao: str | None = Form(None),
    arquivo: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    nome_arquivo_unico = f"{uuid.uuid4().hex[:8]}_{arquivo.filename}"
    caminho_web_relativo = f"uploads/documentos/{nome_arquivo_unico}"

    try:
        content = await arquivo.read()
        supabase = get_supabase()
        
        supabase.storage.from_('agendha-uploads').upload(
            path=caminho_web_relativo,
            file=content,
            file_options={"content-type": arquivo.content_type}
        )
    except Exception as e:
        logger.error(f"Erro upload documento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo no Storage: {e}")

    try:
        res = supabase.table('documentos').insert({
            "nome_documento": nome_documento,
            "descricao": descricao or "",
            "nome_arquivo": arquivo.filename,
            "caminho_arquivo": caminho_web_relativo
        }).execute()

        if not res.data:
            raise HTTPException(status_code=500, detail="Erro ao salvar documento no banco.")

        return Documento(**res.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar documento no banco: {e}")

@router.put("/{documento_id}", response_model=Documento)
async def atualizar_documento(
    documento_id: int,
    nome_documento: str = Form(...),
    descricao: str | None = Form(None),
    arquivo: UploadFile | None = File(None),
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_old = supabase.table('documentos').select('*').eq('id', documento_id).execute()

        if not res_old.data:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        doc_existente = res_old.data[0]
        nome_arquivo_novo = doc_existente["nome_arquivo"]
        caminho_web_novo = doc_existente["caminho_arquivo"]

        if arquivo and arquivo.filename:
            try:
                if caminho_web_novo:
                    try:
                        supabase.storage.from_('agendha-uploads').remove([caminho_web_novo])
                    except Exception:
                        pass

                nome_unico = f"{uuid.uuid4().hex[:8]}_{arquivo.filename}"
                content = await arquivo.read()
                
                caminho_web_novo = f"uploads/documentos/{nome_unico}"
                supabase.storage.from_('agendha-uploads').upload(
                    path=caminho_web_novo,
                    file=content,
                    file_options={"content-type": arquivo.content_type}
                )
                nome_arquivo_novo = arquivo.filename
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro no upload do arquivo: {e}")

        res_up = supabase.table('documentos').update({
            "nome_documento": nome_documento,
            "descricao": descricao or "",
            "nome_arquivo": nome_arquivo_novo,
            "caminho_arquivo": caminho_web_novo
        }).eq('id', documento_id).execute()

        if not res_up.data:
            raise HTTPException(status_code=500, detail="Erro ao atualizar documento no banco.")

        return Documento(**res_up.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar documento: {e}")

@router.delete("/{documento_id}", status_code=204)
def deletar_documento(
    documento_id: int,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_old = supabase.table('documentos').select('caminho_arquivo').eq('id', documento_id).execute()
        
        if not res_old.data:
            raise HTTPException(status_code=404, detail="Documento não encontrado")

        caminho_arquivo = res_old.data[0]["caminho_arquivo"]
        if caminho_arquivo:
            try:
                supabase.storage.from_('agendha-uploads').remove([caminho_arquivo])
            except Exception:
                pass

        supabase.table('documentos').delete().eq('id', documento_id).execute()
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar documento: {e}")

@router.get("/download/{documento_id}")
def download_documento(documento_id: int):
    try:
        supabase = get_supabase()
        res = supabase.table('documentos').select('caminho_arquivo').eq('id', documento_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        caminho = res.data[0].get('caminho_arquivo')
        url = supabase.storage.from_('agendha-uploads').get_public_url(caminho)
        return RedirectResponse(url=url)
    except Exception:
        raise HTTPException(status_code=404, detail="Erro ao gerar link do documento.")

