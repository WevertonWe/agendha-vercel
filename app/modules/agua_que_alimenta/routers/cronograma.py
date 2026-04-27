import sqlite3
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_db_connection
from app.core.auth.dependencies import get_current_user
from app.modules.agua_que_alimenta.models import CronogramaItem, CronogramaItemBase

router = APIRouter(prefix="/api/cronograma", tags=["Cronograma"])

@router.get("", response_model=List[CronogramaItem])
def listar_itens_cronograma(
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Lista tarefas simples do cronograma geral (Legado/Simples).
    Ordenado por data prevista.
    """
    cursor = db.cursor()
    cursor.execute("SELECT * FROM cronograma ORDER BY data_prevista ASC")
    registros = cursor.fetchall()
    return [CronogramaItem(**registro) for registro in registros]


@router.get("/{item_id}", response_model=CronogramaItem)
def get_item_cronograma_por_id(
    item_id: int,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM cronograma WHERE id = ?", (item_id,))
    registro = cursor.fetchone()
    if registro is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return CronogramaItem(**registro)


@router.post("", response_model=CronogramaItem, status_code=201)
def criar_item_cronograma(
    item: CronogramaItemBase,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO cronograma (tarefa, data_prevista, data_realizada,
        status, responsavel, observacao) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (item.tarefa, item.data_prevista, item.data_realizada,
         item.status, item.responsavel, item.observacao)
    )
    novo_id = cursor.lastrowid
    db.commit()
    return CronogramaItem(id=novo_id, **item.dict())


@router.put("/{item_id}", response_model=CronogramaItem)
def atualizar_item_cronograma(
    item_id: int,
    item: CronogramaItemBase,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE cronograma SET tarefa = ?, data_prevista = ?,
        data_realizada = ?, status = ?, responsavel = ?, observacao = ?
        WHERE id = ?
        """,
        (item.tarefa, item.data_prevista, item.data_realizada, item.status,
         item.responsavel, item.observacao, item_id)
    )
    db.commit()
    return CronogramaItem(id=item_id, **item.dict())
