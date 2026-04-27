import sqlite3
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_db_connection
from app.core.auth.dependencies import get_current_user
from app.modules.fornecedores.models import Fornecedor, FornecedorCreate, FornecedorUpdate

router = APIRouter(prefix="/api/fornecedores", tags=["Fornecedores"])
logger = logging.getLogger(__name__)

# --- CRUD ---

@router.get("/", response_model=List[Fornecedor])
def listar_fornecedores(db: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM fornecedores ORDER BY id DESC")
        registros = cursor.fetchall()
        return [Fornecedor(**dict(r)) for r in registros]
    except Exception as e:
        logger.error(f"Erro ao listar fornecedores: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar fornecedores.")

@router.post("/", response_model=Fornecedor, status_code=status.HTTP_201_CREATED)
def criar_fornecedor(
    fornecedor: FornecedorCreate,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        # Verificar duplicidade de CNPJ/CPF se fornecido
        if fornecedor.cnpj_cpf:
            cursor.execute("SELECT id FROM fornecedores WHERE cnpj_cpf = ?", (fornecedor.cnpj_cpf,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="CNPJ/CPF já cadastrado.")

        cursor.execute(
            """
            INSERT INTO fornecedores (razao_social, nome_fantasia, cnpj_cpf, email, telefone, endereco)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (fornecedor.razao_social, fornecedor.nome_fantasia, fornecedor.cnpj_cpf, 
             fornecedor.email, fornecedor.telefone, fornecedor.endereco)
        )
        novo_id = cursor.lastrowid
        db.commit()

        cursor.execute("SELECT * FROM fornecedores WHERE id = ?", (novo_id,))
        novo_registro = dict(cursor.fetchone())
        return Fornecedor(**novo_registro)

    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Erro de integridade: {e}")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar fornecedor: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar fornecedor.")

@router.put("/{id}", response_model=Fornecedor)
def atualizar_fornecedor(
    id: int,
    fornecedor: FornecedorUpdate,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM fornecedores WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")

        cursor.execute(
            """
            UPDATE fornecedores
            SET razao_social = ?, nome_fantasia = ?, cnpj_cpf = ?, email = ?, telefone = ?, endereco = ?
            WHERE id = ?
            """,
            (fornecedor.razao_social, fornecedor.nome_fantasia, fornecedor.cnpj_cpf,
             fornecedor.email, fornecedor.telefone, fornecedor.endereco, id)
        )
        db.commit()

        cursor.execute("SELECT * FROM fornecedores WHERE id = ?", (id,))
        return Fornecedor(**dict(cursor.fetchone()))

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar fornecedor: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar.")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_fornecedor(
    id: int,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_current_user)
):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM fornecedores WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")

        cursor.execute("DELETE FROM fornecedores WHERE id = ?", (id,))
        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar fornecedor: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar.")
