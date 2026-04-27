import sqlite3
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_db_connection
from app.core.auth.dependencies import get_current_user
from app.modules.materiais.models import Material, MaterialCreate, MaterialUpdate

router = APIRouter(prefix="/api/materiais", tags=["Materiais"])
logger = logging.getLogger(__name__)

# --- CRUD ---

@router.get("/", response_model=List[Material])
def listar_materiais(db: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM materiais ORDER BY nome ASC")
        registros = cursor.fetchall()
        return [Material(**dict(r)) for r in registros]
    except Exception as e:
        logger.error(f"Erro ao listar materiais: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar materiais.")

@router.post("/", response_model=Material, status_code=status.HTTP_201_CREATED)
def criar_material(
    material: MaterialCreate,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO materiais (nome, unidade, categoria, descricao)
            VALUES (?, ?, ?, ?)
            """,
            (material.nome, material.unidade, material.categoria, material.descricao)
        )
        novo_id = cursor.lastrowid
        db.commit()

        cursor.execute("SELECT * FROM materiais WHERE id = ?", (novo_id,))
        novo_registro = dict(cursor.fetchone())
        return Material(**novo_registro)

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar material: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar material.")

@router.put("/{id}", response_model=Material)
def atualizar_material(
    id: int,
    material: MaterialUpdate,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM materiais WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Material não encontrado.")

        # Construção dinâmica do UPDATE
        campos = []
        valores = []
        if material.nome is not None:
             campos.append("nome = ?")
             valores.append(material.nome)
        if material.unidade is not None:
             campos.append("unidade = ?")
             valores.append(material.unidade)
        if material.categoria is not None:
             campos.append("categoria = ?")
             valores.append(material.categoria)
        if material.descricao is not None:
             campos.append("descricao = ?")
             valores.append(material.descricao)

        if not campos:
             raise HTTPException(status_code=400, detail="Nenhum campo para atualizar.")

        valores.append(id)
        sql = f"UPDATE materiais SET {', '.join(campos)} WHERE id = ?"  # nosec
        
        cursor.execute(sql, tuple(valores))
        db.commit()

        cursor.execute("SELECT * FROM materiais WHERE id = ?", (id,))
        return Material(**dict(cursor.fetchone()))

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar material: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar material.")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_material(
    id: int,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM materiais WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Material não encontrado.")

        cursor.execute("DELETE FROM materiais WHERE id = ?", (id,))
        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar material: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar material.")
