import sqlite3
import logging
import uuid
import shutil
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import get_db_connection
from app.core.auth.dependencies import get_admin_user
from app.modules.agua_que_alimenta.models import Pedreiro, PedreiroCreate, PedreiroUpdate, FaturamentoCreate
from app.config import settings

router = APIRouter(prefix="/api/pedreiros", tags=["Pedreiros"])
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)

@router.get("", response_model=List[Pedreiro])
def listar_pedreiros(db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Lista todos os pedreiros cadastrados.
    
    Inclui campos calculados:
    - 'total_obras': COUNT de beneficiários vinculados
    - 'ultima_producao': MAX(data_conclusao) de beneficiários vinculados
    - 'status_financeiro': 'Pendente' se houver alguma obra com pagamento pendente, senão 'Pago' (ou 'Sem Obras')
    """
    try:
        cursor = db.cursor()
        # 1. Buscar todos os pedreiros
        cursor.execute("SELECT * FROM pedreiros")
        pedreiros_bd = cursor.fetchall()
        
        resultado = []
        for p in pedreiros_bd:
            pedreiro_dict = dict(p)
            pedreiro_id = pedreiro_dict['id']
            
            # 2. Contar produção real explicitamente para cada pedreiro
            cursor.execute("""
                SELECT 
                    COUNT(id) as producao_count,
                    MAX(data_conclusao) as ultima_producao,
                    SUM(CASE WHEN status_pagamento = 'PENDENTE' THEN 1 ELSE 0 END) as pendencias
                FROM beneficiarios
                WHERE pedreiro_id = ? AND (UPPER(status) LIKE '%CONSTRU%' OR UPPER(status) LIKE '%CONCLU%')
            """, (pedreiro_id,))
            
            stats = cursor.fetchone()
            
            # 3. Injetar explicitamente no Payload JSON
            producao_count = stats['producao_count'] if stats['producao_count'] is not None else 0
            pendencias = stats['pendencias'] if stats['pendencias'] is not None else 0
            
            pedreiro_dict['producao_count'] = producao_count
            pedreiro_dict['ultima_producao'] = stats['ultima_producao']
            
            if producao_count == 0:
                pedreiro_dict['status_financeiro'] = 'Sem Obras'
            elif pendencias > 0:
                pedreiro_dict['status_financeiro'] = 'Pendente'
            else:
                pedreiro_dict['status_financeiro'] = 'Pago'
                
            resultado.append(pedreiro_dict)
            
        return resultado
    except sqlite3.Error as e:
        logging.error(f"Erro ao listar pedreiros: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar pedreiros.")

@router.post("", response_model=Pedreiro, status_code=201)
def criar_pedreiro(
    pedreiro: PedreiroCreate, 
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_admin_user)
):
    try:
        cursor = db.cursor()
        
        # Verificar CPF duplicado
        cursor.execute("SELECT id FROM pedreiros WHERE cpf = ?", (pedreiro.cpf,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="CPF já cadastrado.")

        cursor.execute("""
            INSERT INTO pedreiros (nome_completo, cpf, telefone, endereco, dados_pagamento, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pedreiro.nome_completo, pedreiro.cpf, pedreiro.telefone, pedreiro.endereco, pedreiro.dados_pagamento, pedreiro.status))
        
        db.commit()
        novo_id = cursor.lastrowid
        
        return {**pedreiro.dict(), "id": novo_id, "producao_count": 0}
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Erro ao criar pedreiro: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar pedreiro.")

@router.get("/perfil/{id}", response_class=HTMLResponse)
def perfil_pedreiro(request: Request, id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Renderiza página HTML com perfil completo do pedreiro e lista de obras associadas.
    """
    cursor = db.cursor()
    
    # Busca Pedreiro e total de obras concluídas
    cursor.execute("""
        SELECT p.*, COUNT(CASE WHEN UPPER(b.status) LIKE '%CONSTRU%' OR UPPER(b.status) LIKE '%CONCLU%' THEN 1 END) as producao_count
        FROM pedreiros p
        LEFT JOIN beneficiarios b ON p.id = b.pedreiro_id
        WHERE p.id = ?
        GROUP BY p.id
    """, (id,))
    pedreiro_row = cursor.fetchone()
    
    if not pedreiro_row:
        return templates.TemplateResponse("errors/404.html", {"request": request}, status_code=404)
        
    pedreiro = dict(pedreiro_row)
    
    # Busca Obras (Beneficiários)
    cursor.execute("""
        SELECT 
            b.id, 
            b.nome_completo, 
            b.municipio, 
            b.comunidade, 
            b.status,
            b.status_pagamento,
            b.link_nota_fiscal,
            b.data_conclusao
        FROM beneficiarios b
        WHERE b.pedreiro_id = ?
    """, (id,))
    obras = [dict(row) for row in cursor.fetchall()]
    
    return templates.TemplateResponse("pedreiros/perfil.html", {
        "request": request, 
        "pedreiro": pedreiro, 
        "obras": obras
    })

@router.put("/{pedreiro_id}", response_model=Pedreiro)
def atualizar_pedreiro(
    pedreiro_id: int,
    dados: PedreiroUpdate,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_admin_user)
):
    try:
        cursor = db.cursor()
        
        # Verificar se existe
        cursor.execute("SELECT * FROM pedreiros WHERE id = ?", (pedreiro_id,))
        registro_atual = cursor.fetchone()
        if not registro_atual:
            raise HTTPException(status_code=404, detail="Pedreiro não encontrado.")

        campos_para_atualizar = dados.dict(exclude_unset=True)
        if not campos_para_atualizar:
            return dict(registro_atual)

        set_clause_parts = []
        valores = []
        for campo, valor in campos_para_atualizar.items():
            set_clause_parts.append(f"{campo} = ?")
            valores.append(valor)
        
        valores.append(pedreiro_id)
        query = f"UPDATE pedreiros SET {', '.join(set_clause_parts)} WHERE id = ?"  # nosec
        
        cursor.execute(query, valores)
        db.commit()
        
        # Retorna com total atualizado (re-query)
        cursor.execute("""
            SELECT p.*, COUNT(CASE WHEN UPPER(b.status) LIKE '%CONSTRU%' OR UPPER(b.status) LIKE '%CONCLU%' THEN 1 END) as producao_count
            FROM pedreiros p
            LEFT JOIN beneficiarios b ON p.id = b.pedreiro_id
            WHERE p.id = ?
            GROUP BY p.id
        """, (pedreiro_id,))
        return dict(cursor.fetchone())

    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Erro ao atualizar pedreiro: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar pedreiro.")

        cursor.execute("DELETE FROM pedreiros WHERE id = ?", (pedreiro_id,))
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Erro ao excluir pedreiro: {e}")
        raise HTTPException(status_code=500, detail="Erro ao excluir pedreiro.")

@router.get("/{pedreiro_id}/producao", response_model=List[dict])
def listar_producao_pedreiro(pedreiro_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Retorna lista de cisternas (beneficiários) vinculadas ao pedreiro para o modal de gestão.
    """
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT 
                b.id, 
                b.nome_completo, 
                b.municipio, 
                b.comunidade, 
                b.status,
                b.status_pagamento,
                b.data_conclusao
            FROM beneficiarios b
            WHERE b.pedreiro_id = ? AND (UPPER(b.status) LIKE '%CONSTRU%' OR UPPER(b.status) LIKE '%CONCLU%')
            ORDER BY b.data_conclusao DESC
        """, (pedreiro_id,))
        obras = [dict(row) for row in cursor.fetchall()]
        return obras
    except sqlite3.Error as e:
        logging.error(f"Erro ao listar produção do pedreiro {pedreiro_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produção.")

@router.get("/{pedreiro_id}/pendentes", response_model=List[dict])
def listar_pendentes_faturamento(pedreiro_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Retorna lista de cisternas concluídas pendentes de faturamento em lote.
    Critérios: status = 'CONSTRUÍDA' e faturamento_id IS NULL.
    """
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT 
                b.id, 
                b.nome_completo, 
                b.municipio, 
                b.comunidade, 
                b.status,
                b.status_pagamento,
                b.data_conclusao,
                1000.0 as valor_sugerido
            FROM beneficiarios b
            WHERE b.pedreiro_id = ? 
              AND (UPPER(b.status) LIKE '%CONSTRU%' OR UPPER(b.status) LIKE '%CONCLU%') 
              AND b.faturamento_id IS NULL
            ORDER BY b.nome_completo ASC
        """, (pedreiro_id,))
        obras = [dict(row) for row in cursor.fetchall()]
        return obras
    except sqlite3.Error as e:
        logging.error(f"Erro ao listar pendentes do pedreiro {pedreiro_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar pendentes de faturamento.")

@router.post("/faturamentos", status_code=201)
def gerar_lote_faturamento(
    payload: FaturamentoCreate,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_admin_user)
):
    """
    Gera um novo lote de faturamento para um pedreiro a partir de um array de cisternas.
    Atualiza as cisternas vinculadas setando faturamento_id e status=PAGO.
    """
    if not payload.beneficiarios_ids:
        raise HTTPException(status_code=400, detail="Nenhuma cisterna foi enviada para faturar.")
        
    try:
        cursor = db.cursor()
        
        # 1. Inserir Header do Lote de Faturamento
        cursor.execute("""
            INSERT INTO faturamentos (pedreiro_id, valor_total, valor_dam, status_dam)
            VALUES (?, ?, ?, 'Pendente')
        """, (payload.pedreiro_id, payload.valor_total, payload.valor_dam))
        
        novo_faturamento_id = cursor.lastrowid
        
        # 2. Amarrar Obras (Beneficiarios) ao Lote Gerado e marcar PAGO
        placeholders = ",".join(["?"] * len(payload.beneficiarios_ids))
        query_update_obras = f"""
            UPDATE beneficiarios 
            SET faturamento_id = ?, status_pagamento = 'PAGO' 
            WHERE id IN ({placeholders})
        """
        valores_update = [novo_faturamento_id] + payload.beneficiarios_ids
        
        cursor.execute(query_update_obras, valores_update)
        db.commit()
        
        return {"message": "Lote gerado com sucesso", "faturamento_id": novo_faturamento_id}
        
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Erro ao gerar faturamento lote: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar faturamento.")

@router.get("/{pedreiro_id}/faturamentos", response_model=List[dict])
def listar_historico_faturamentos(pedreiro_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    """
    Retorna o histórico de Lotes de Faturamento gerados para o Pedreiro.
    Inclui a contagem de cisternas (obras).
    """
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT 
                f.id,
                f.pedreiro_id,
                f.valor_total,
                f.valor_dam,
                f.status_dam,
                f.arquivo_nf,
                f.arquivo_dam,
                f.data_criacao,
                COUNT(b.id) as qtd_obras,
                json_group_array(
                    json_object(
                        'nome', b.nome_completo,
                        'local', coalesce(b.comunidade, b.municipio, '')
                    )
                ) as obras
            FROM faturamentos f
            LEFT JOIN beneficiarios b ON b.faturamento_id = f.id
            WHERE f.pedreiro_id = ?
            GROUP BY f.id
            ORDER BY f.data_criacao DESC
        """, (pedreiro_id,))
        
        faturamentos = []
        for row in cursor.fetchall():
            item = dict(row)
            try:
                # O SQLite json_group_array pode retornar nulo ou vazios com "[{nome: null}]" devido ao LEFT JOIN
                obrasjson = json.loads(item['obras'])
                item['obras'] = [o for o in obrasjson if o.get('nome')]
            except (json.JSONDecodeError, TypeError):
                item['obras'] = []
            faturamentos.append(item)
            
        return faturamentos
        
    except sqlite3.Error as e:
        logging.error(f"Erro ao listar histórico de faturamentos do pedreiro {pedreiro_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar histórico financeiro.")


@router.post("/faturamentos/{faturamento_id}/upload-nf")
async def upload_faturamento_nf(
    faturamento_id: int,
    arquivo: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_admin_user)
):
    """ Upload de Nota Fiscal anexada ao Lote de Faturamento """
    DEST_FOLDER = settings.UPLOAD_FOLDER / "financeiro"
    DEST_FOLDER.mkdir(parents=True, exist_ok=True)

    nome_arquivo_unico = f"nf_lote_{faturamento_id}_{uuid.uuid4().hex[:8]}_{arquivo.filename}"
    caminho_absoluto = DEST_FOLDER / nome_arquivo_unico
    
    with open(caminho_absoluto, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    caminho_web_relativo = f"uploads/financeiro/{nome_arquivo_unico}"

    try:
        cursor = db.cursor()
        cursor.execute("UPDATE faturamentos SET arquivo_nf = ? WHERE id = ?", (caminho_web_relativo, faturamento_id))
        db.commit()
        return {"message": "Nota Fiscal salva com sucesso", "url": caminho_web_relativo}
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar NF no banco: {e}")


@router.post("/faturamentos/{faturamento_id}/upload-dam")
async def upload_faturamento_dam(
    faturamento_id: int,
    arquivo: UploadFile = File(...),
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_admin_user)
):
    """ Upload do DAM pago anexado ao Lote de Faturamento """
    DEST_FOLDER = settings.UPLOAD_FOLDER / "financeiro"
    DEST_FOLDER.mkdir(parents=True, exist_ok=True)

    nome_arquivo_unico = f"dam_lote_{faturamento_id}_{uuid.uuid4().hex[:8]}_{arquivo.filename}"
    caminho_absoluto = DEST_FOLDER / nome_arquivo_unico
    
    with open(caminho_absoluto, "wb") as buffer:
        shutil.copyfileobj(arquivo.file, buffer)

    caminho_web_relativo = f"uploads/financeiro/{nome_arquivo_unico}"

    try:
        cursor = db.cursor()
        cursor.execute("UPDATE faturamentos SET arquivo_dam = ? WHERE id = ?", (caminho_web_relativo, faturamento_id))
        db.commit()
        return {"message": "DAM salvo com sucesso", "url": caminho_web_relativo}
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar DAM no banco: {e}")

@router.delete("/faturamentos/{faturamento_id}")
def estornar_lote_faturamento(
    faturamento_id: int,
    db: sqlite3.Connection = Depends(get_db_connection),
    current_user = Depends(get_admin_user)
):
    """
    Cancela um Lote de Faturamento:
    1. Define faturamento_id como nulo e status como 'PENDENTE' em todas as obras.
    2. Remove o Lote da tabela faturamentos.
    """
    try:
        cursor = db.cursor()
        
        # 1. Recuperar cisternas para Pendente
        cursor.execute("""
            UPDATE beneficiarios 
            SET faturamento_id = NULL, status_pagamento = 'PENDENTE'
            WHERE faturamento_id = ?
        """, (faturamento_id,))
        
        # 2. Apagar Lote
        cursor.execute("DELETE FROM faturamentos WHERE id = ?", (faturamento_id,))
        
        if cursor.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Lote de faturamento não encontrado.")
            
        db.commit()
        return {"message": "Lote estornado com sucesso."}
        
    except sqlite3.Error as e:
        db.rollback()
        logging.error(f"Erro ao estornar faturamento lote {faturamento_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao estornar lote de faturamento.")
