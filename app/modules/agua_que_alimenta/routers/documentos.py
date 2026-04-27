import os
import shutil
import uuid
import sqlite3
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.dependencies import get_db_connection
from app.core.auth.dependencies import get_current_user
from app.modules.agua_que_alimenta.models import Documento
from app.config import settings

router = APIRouter(prefix="/api/documentos", tags=["Documentos"])

@router.get("", response_model=List[Documento])
def listar_documentos(db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id, nome_documento, descricao, nome_arquivo,
               caminho_arquivo, data_upload
        FROM documentos ORDER BY id DESC
        """
    )
    registros = cursor.fetchall()
    return [Documento(**registro) for registro in registros]


@router.post("", response_model=Documento, status_code=201)
async def criar_documento(
    nome_documento: str = Form(...),
    descricao: str | None = Form(None),
    arquivo: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    """
    Upload de documento para repositório central.
    Gera nome único (UUID prefix) para evitar colisão de arquivos.
    """
    nome_arquivo_unico = f"{uuid.uuid4().hex[:8]}_{arquivo.filename}"
    caminho_absoluto_salvo = settings.DOCUMENTOS_FOLDER / nome_arquivo_unico

    with open(caminho_absoluto_salvo, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    caminho_web_relativo = f"uploads/documentos/{nome_arquivo_unico}"

    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO documentos (nome_documento, descricao, nome_arquivo, caminho_arquivo)
        VALUES (?, ?, ?, ?)
        """,
        (nome_documento, descricao, arquivo.filename, caminho_web_relativo)
    )
    novo_id = cursor.lastrowid
    db.commit()

    cursor.execute("SELECT * FROM documentos WHERE id = ?", (novo_id,))
    novo_documento = cursor.fetchone()
    return Documento(**novo_documento)





@router.put("/{documento_id}", response_model=Documento)
async def atualizar_documento(
    documento_id: int,
    nome_documento: str = Form(...),
    descricao: str | None = Form(None),
    arquivo: UploadFile | None = File(None),
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM documentos WHERE id = ?", (documento_id,))
    doc_existente = cursor.fetchone()

    if not doc_existente:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    nome_arquivo_novo = doc_existente["nome_arquivo"]
    caminho_web_novo = doc_existente["caminho_arquivo"]

    # Se enviou novo arquivo, substitui o antigo
    if arquivo:
        # Remover arquivo antigo
        caminho_antigo_abs = settings.BASE_DIR / doc_existente["caminho_arquivo"]
        if os.path.exists(caminho_antigo_abs):
            try:
                os.remove(caminho_antigo_abs)
            except OSError:
                pass # Ignora erro se não conseguir deletar antigo

        # Salvar novo arquivo
        nome_unico = f"{uuid.uuid4().hex[:8]}_{arquivo.filename}"
        caminho_salvar = settings.DOCUMENTOS_FOLDER / nome_unico
        
        with open(caminho_salvar, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
            
        nome_arquivo_novo = arquivo.filename
        caminho_web_novo = f"uploads/documentos/{nome_unico}"

    cursor.execute(
        """
        UPDATE documentos
        SET nome_documento = ?, descricao = ?, nome_arquivo = ?, caminho_arquivo = ?
        WHERE id = ?
        """,
        (nome_documento, descricao, nome_arquivo_novo, caminho_web_novo, documento_id)
    )
    db.commit()

    cursor.execute("SELECT * FROM documentos WHERE id = ?", (documento_id,))
    doc_atualizado = cursor.fetchone()
    return Documento(**doc_atualizado)


@router.delete("/{documento_id}", status_code=204)
def deletar_documento(
    documento_id: int,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    cursor = db.cursor()
    cursor.execute(
        "SELECT caminho_arquivo FROM documentos WHERE id = ?", (documento_id,)
    )
    resultado = cursor.fetchone()
    if not resultado:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    caminho_arquivo = resultado["caminho_arquivo"]
    if caminho_arquivo:
        caminho_abs = settings.BASE_DIR / caminho_arquivo
        if os.path.exists(caminho_abs):
            os.remove(caminho_abs)

    cursor.execute("DELETE FROM documentos WHERE id = ?", (documento_id,))
    db.commit()
    return
