import uuid
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.core.auth.dependencies import get_current_user
from app.modules.agua_que_alimenta.models import Evento, EventoStatusUpdate
from app.core.database import get_supabase

router = APIRouter(prefix="/api/eventos_grh", tags=["Eventos GRH"])
logger = logging.getLogger(__name__)

@router.post("", response_model=Evento, status_code=201)
async def criar_evento_grh(
    municipio_comunidade: str = Form(...),
    dia_previsto: str = Form(...),
    observacao: Optional[str] = Form(None),
    arquivo: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user)
):
    caminho_web_relativo = None
    if arquivo and arquivo.filename:
        try:
            nome_arquivo_unico = f"{uuid.uuid4().hex[:8]}_{arquivo.filename}"
            content = await arquivo.read()
            supabase = get_supabase()
            
            supabase.storage.from_('agendha-uploads').upload(
                path=f"uploads/grh/{nome_arquivo_unico}",
                file=content,
                file_options={"content-type": arquivo.content_type}
            )
            caminho_web_relativo = f"uploads/grh/{nome_arquivo_unico}"
        except Exception as e:
            logger.error(f"Erro upload GRH: {e}")
            raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo no Storage: {e}")

    try:
        supabase = get_supabase()
        res = supabase.table('eventos_grh').insert({
            "municipio_comunidade": municipio_comunidade,
            "dia_previsto": str(dia_previsto),
            "observacao": observacao or "",
            "caminho_arquivo": caminho_web_relativo,
            "realizado": False
        }).execute()

        if not res.data:
            raise HTTPException(status_code=500, detail="Erro ao inserir evento no banco.")

        novo_evento = res.data[0]
        novo_evento['dia_previsto'] = str(novo_evento.get('dia_previsto', ''))
        return Evento(**novo_evento)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar evento: {e}")


@router.get("", response_model=List[Evento])
def listar_eventos_grh():
    try:
        supabase = get_supabase()
        res = supabase.table('eventos_grh').select('*').order('id').execute()
        eventos = []
        for row in res.data:
            row['dia_previsto'] = str(row.get('dia_previsto', ''))
            eventos.append(Evento(**row))
        return eventos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar eventos: {e}")


@router.put("/{evento_id}", response_model=Evento)
async def atualizar_evento_grh_form(
    evento_id: int,
    municipio_comunidade: str = Form(...),
    dia_previsto: str = Form(...),
    observacao: Optional[str] = Form(None),
    arquivo: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_old = supabase.table('eventos_grh').select('caminho_arquivo').eq('id', evento_id).execute()
        
        if not res_old.data:
            raise HTTPException(status_code=404, detail="Evento não encontrado.")

        caminho_web_relativo = res_old.data[0].get('caminho_arquivo')

        if arquivo and arquivo.filename:
            try:
                nome_arquivo_unico = f"{uuid.uuid4().hex[:8]}_{arquivo.filename}"
                content = await arquivo.read()
                
                if caminho_web_relativo:
                    try:
                        supabase.storage.from_('agendha-uploads').remove([caminho_web_relativo])
                    except Exception:
                        pass
                
                supabase.storage.from_('agendha-uploads').upload(
                    path=f"uploads/grh/{nome_arquivo_unico}",
                    file=content,
                    file_options={"content-type": arquivo.content_type}
                )
                caminho_web_relativo = f"uploads/grh/{nome_arquivo_unico}"
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro no upload do arquivo: {e}")

        res_up = supabase.table('eventos_grh').update({
            "municipio_comunidade": municipio_comunidade,
            "dia_previsto": str(dia_previsto),
            "observacao": observacao or "",
            "caminho_arquivo": caminho_web_relativo
        }).eq('id', evento_id).execute()

        if not res_up.data:
            raise HTTPException(status_code=500, detail="Erro ao atualizar evento no banco.")

        row = res_up.data[0]
        row['dia_previsto'] = str(row.get('dia_previsto', ''))
        return Evento(**row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar evento: {e}")


@router.put("/{evento_id}/status", response_model=Evento)
def atualizar_evento_grh_status(
    evento_id: int,
    status_update: EventoStatusUpdate,
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res = supabase.table('eventos_grh').update({
            "realizado": status_update.realizado
        }).eq('id', evento_id).execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Evento não encontrado.")

        row = res.data[0]
        row['dia_previsto'] = str(row.get('dia_previsto', ''))
        return Evento(**row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {e}")


@router.delete("/{evento_id}", status_code=204)
def deletar_evento_grh(
    evento_id: int, 
    current_user = Depends(get_current_user)
):
    try:
        supabase = get_supabase()
        res_old = supabase.table('eventos_grh').select('caminho_arquivo').eq('id', evento_id).execute()

        if res_old.data and res_old.data[0].get('caminho_arquivo'):
            caminho_web_relativo = res_old.data[0].get('caminho_arquivo')
            try:
                supabase.storage.from_('agendha-uploads').remove([caminho_web_relativo])
            except Exception:
                pass

        supabase.table('eventos_grh').delete().eq('id', evento_id).execute()
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar evento: {e}")

