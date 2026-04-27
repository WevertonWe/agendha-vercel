import os
import uuid
import shutil
import logging
import sqlite3
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.dependencies import get_db_connection
from app.core.auth.dependencies import get_current_user
from app.modules.agua_que_alimenta.models import Evento, EventoStatusUpdate
from app.config import settings

router = APIRouter(prefix="/api/eventos_grh", tags=["Eventos GRH"])

@router.post("", response_model=Evento, status_code=201)
async def criar_evento_grh(
    municipio_comunidade: str = Form(...),
    dia_previsto: str = Form(...),
    observacao: Optional[str] = Form(None),
    arquivo: Optional[UploadFile] = File(None),
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user: str = Depends(get_current_user)
):
    """
    Cria um novo evento de monitoramento GRH.
    
    1. Salva arquivo de evidência (se enviado) no disco.
    2. Insere registro no banco de dados.
    3. Retorna objeto criado.
    """
    caminho_web_relativo = None
    if arquivo and arquivo.filename:
        nome_arquivo_unico = f"{uuid.uuid4().hex[:8]}_{arquivo.filename}"
        caminho_absoluto = settings.GRH_FOLDER / nome_arquivo_unico
        with open(caminho_absoluto, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
        caminho_web_relativo = f"uploads/grh/{nome_arquivo_unico}"

    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO eventos_grh (municipio_comunidade, dia_previsto, observacao, caminho_arquivo, realizado) VALUES (?, ?, ?, ?, ?)",
            (municipio_comunidade, dia_previsto,
             observacao, caminho_web_relativo, False)
        )
        novo_id = cursor.lastrowid
        db.commit()

        cursor.execute("SELECT * FROM eventos_grh WHERE id = ?", (novo_id,))
        novo_evento = dict(cursor.fetchone())
        return Evento(**novo_evento)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar evento: {e}")


@router.get("", response_model=List[Evento])
def listar_eventos_grh(db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM eventos_grh ORDER BY id")
    return [Evento(**dict(registro)) for registro in cursor.fetchall()]


@router.put("/{evento_id}", response_model=Evento)
async def atualizar_evento_grh_form(
    evento_id: int,
    municipio_comunidade: str = Form(...),
    dia_previsto: str = Form(...),
    observacao: Optional[str] = Form(None),
    arquivo: Optional[UploadFile] = File(None),
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user: str = Depends(get_current_user)
):
    """
    Atualiza dados de um evento existente.
    
    Atenção: Se um novo arquivo for enviado, o arquivo antigo (se existir) é substituído fisicamente no disco.
    """
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT caminho_arquivo FROM eventos_grh WHERE id = ?", (evento_id,))
        evento_atual = cursor.fetchone()
        if not evento_atual:
            raise HTTPException(
                status_code=404, detail="Evento não encontrado.")

        caminho_web_relativo = evento_atual['caminho_arquivo']

        if arquivo and arquivo.filename:
            logging.info(
                f"Recebendo novo arquivo para o evento {evento_id}: {arquivo.filename}")
            if caminho_web_relativo:
                caminho_antigo_abs = settings.BASE_DIR / caminho_web_relativo
                if os.path.exists(caminho_antigo_abs):
                    os.remove(caminho_antigo_abs)
                    logging.info(
                        f"Arquivo antigo removido: {caminho_antigo_abs}")
                else:
                    logging.warning(
                        f"Caminho do arquivo antigo não encontrado: {caminho_antigo_abs}")

            nome_arquivo_unico = f"{uuid.uuid4().hex[:8]}_{arquivo.filename}"
            caminho_absoluto_novo = settings.GRH_FOLDER / nome_arquivo_unico
            with open(caminho_absoluto_novo, "wb") as buffer:
                shutil.copyfileobj(arquivo.file, buffer)
            caminho_web_relativo = f"uploads/grh/{nome_arquivo_unico}"

        cursor.execute(
            """UPDATE eventos_grh 
               SET municipio_comunidade = ?, dia_previsto = ?, observacao = ?, caminho_arquivo = ?
               WHERE id = ?""",
            (municipio_comunidade, dia_previsto,
             observacao, caminho_web_relativo, evento_id)
        )
        db.commit()

        cursor.execute("SELECT * FROM eventos_grh WHERE id = ?", (evento_id,))
        registro_atualizado = dict(cursor.fetchone())
        return Evento(**registro_atualizado)

    except Exception as e:
        db.rollback()
        logging.error(f"Erro ao ATUALIZAR evento {evento_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar evento: {e}")


@router.put("/{evento_id}/status", response_model=Evento)
def atualizar_evento_grh_status(
    evento_id: int,
    status_update: EventoStatusUpdate,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE eventos_grh SET realizado = ? WHERE id = ?",
            (status_update.realizado, evento_id)
        )
        db.commit()

        cursor.execute("SELECT * FROM eventos_grh WHERE id = ?", (evento_id,))
        registro_atualizado = dict(cursor.fetchone())
        return Evento(**registro_atualizado)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar status: {e}")


@router.delete("/{evento_id}", status_code=204)
def deletar_evento_grh(
    evento_id: int, 
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    cursor = db.cursor()
    cursor.execute(
        "SELECT caminho_arquivo FROM eventos_grh WHERE id = ?", (evento_id,))
    resultado = cursor.fetchone()

    if resultado and resultado['caminho_arquivo']:
        caminho_arquivo = settings.BASE_DIR / resultado['caminho_arquivo']
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
            logging.info(
                f"Arquivo associado ao evento {evento_id} removido: {caminho_arquivo}")

    cursor.execute("DELETE FROM eventos_grh WHERE id = ?", (evento_id,))
    db.commit()
    return
