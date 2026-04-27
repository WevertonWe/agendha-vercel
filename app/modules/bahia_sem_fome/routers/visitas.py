
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
import sqlite3
# import pandas as pd
import io
from datetime import datetime
from app.core.database import get_db_connection
from app.modules.bahia_sem_fome.models import BSFVisita, BSFVisitaCreate, BSFVisitaBatch

router = APIRouter(prefix="/api/bsf/visitas", tags=["BSF - Visitas"])

# --- NOVO: Rotas de Atividades (Auxiliar para selects) ---
@router.get("/atividades", response_model=List[dict])
async def list_atividades(db: sqlite3.Connection = Depends(get_db_connection)):
    """Lista todas as atividades disponíveis para cadastro."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT a.id, a.nome, a.descricao
        FROM bsf_atividades a
        JOIN bsf_metas_contrato mc ON mc.atividade_id = a.id
        GROUP BY a.id, a.nome, a.descricao
        ORDER BY MIN(mc.id)
    """)
    rows = cursor.fetchall()
    return [{"id": r[0], "nome": r[1], "descricao": r[2]} for r in rows]

@router.get("", response_model=List[BSFVisita])
async def list_visitas(
    municipio: Optional[str] = None,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    tecnico: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    cursor = db.cursor()
    query = """
        SELECT v.*, a.nome as atividade_nome 
        FROM bsf_visitas v
        LEFT JOIN bsf_atividades a ON v.atividade_id = a.id
        WHERE 1=1
    """
    params = []
    
    if municipio:
        query += " AND v.municipio = ?"
        params.append(municipio)
        
    if ano:
         query += " AND strftime('%Y', data_visita) = ?"
         params.append(str(ano))
         
    if mes:
         query += " AND strftime('%m', data_visita) = ?"
         params.append(f"{mes:02d}")

    if tecnico:
         query += " AND v.tecnico_id = ?"
         params.append(tecnico)

    query += " ORDER BY v.data_visita DESC"
         
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Mapear para o modelo (convertendo row -> dict -> Pydantic)
    results = []
    for row in rows:
        # sqlite3.Row objects can be accessed like dictionaries if row_factory is set to sqlite3.Row
        # Assuming row_factory is set or converting to dict explicitly
        row_dict = dict(row) 
        # Adaptar para o modelo
        results.append(BSFVisita(
            id=row_dict['id'],
            tecnico_id=row_dict['tecnico_id'],
            beneficiario_id=row_dict['beneficiario_id'],
            municipio=row_dict['municipio'],
            comunidade=row_dict['comunidade'],
            data_visita=row_dict['data_visita'],
            atividade_id=row_dict['atividade_id'] if row_dict['atividade_id'] else 0, # Fallback 0 for nulls
            status=row_dict['status'],
            atividade_nome=row_dict['atividade_nome']
        ))
        
    return results

@router.post("")
async def create_visita(
    visita: BSFVisitaCreate,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Diagnostic logging — cada campo que chega
    import logging
    logger = logging.getLogger("bsf.visitas")
    logger.info("=" * 60)
    logger.info(">>> POST /api/bsf/visitas RECEBIDO")
    logger.info(f"  tecnico_id:      '{visita.tecnico_id}'")
    logger.info(f"  beneficiario_id: '{visita.beneficiario_id}'")
    logger.info(f"  municipio:       '{visita.municipio}'")
    logger.info(f"  comunidade:      '{visita.comunidade}'")
    logger.info(f"  data_visita:     '{visita.data_visita}'")
    logger.info(f"  atividade_id:    {visita.atividade_id} (type: {type(visita.atividade_id).__name__})")
    logger.info(f"  status:          '{visita.status}'")
    logger.info(f"  data_registro:   '{today}'")
    
    try:
        cursor = db.cursor()
        
        # BYPASS FK — o banco existente tem FK inválida em municipio→bsf_metas
        # bsf_metas usa UNIQUE(municipio,mes,ano), não UNIQUE(municipio)
        cursor.execute("PRAGMA foreign_keys = OFF")
        logger.info("  FK desabilitada para INSERT")
        
        cursor.execute("""
            INSERT INTO bsf_visitas (tecnico_id, beneficiario_id, municipio, comunidade, data_visita, status, atividade_id, data_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            visita.tecnico_id, 
            visita.beneficiario_id, 
            visita.municipio, 
            visita.comunidade, 
            visita.data_visita, 
            visita.status or 'Realizada',
            visita.atividade_id,
            today
        ))
        
        visita_id = cursor.lastrowid
        logger.info(f"  INSERT OK — lastrowid = {visita_id}")  # nosec
        
        db.commit()
        logger.info("  COMMIT OK")
        
        # Re-enable FK para o resto da conexão
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Verificação: o dado realmente entrou?
        cursor.execute("SELECT COUNT(*) FROM bsf_visitas WHERE id = ?", (visita_id,))
        count = cursor.fetchone()[0]
        logger.info(f"  VERIFICAÇÃO: registro id={visita_id} existe? {count > 0}")
        logger.info("=" * 60)
        
        return {"status": "sucesso", "message": f"Visita registrada (id={visita_id})"}
    except sqlite3.IntegrityError as ie:
        db.rollback()
        logger.error(f"  INTEGRITY ERROR: {ie}")
        logger.error("  Verificando FKs...")
        
        # Diagnóstico detalhado
        try:
            c = db.cursor()
            c.execute("SELECT COUNT(*) FROM bsf_atividades WHERE id = ?", (visita.atividade_id,))
            atv_exists = c.fetchone()[0]
            logger.error(f"    atividade_id={visita.atividade_id} existe em bsf_atividades? {atv_exists > 0}")
            
            c.execute("SELECT COUNT(*) FROM bsf_metas WHERE municipio = ?", (visita.municipio,))
            mun_exists = c.fetchone()[0]
            logger.error(f"    municipio='{visita.municipio}' existe em bsf_metas? {mun_exists > 0}")
        except Exception:
            pass
            
        raise HTTPException(status_code=500, detail=f"Erro de integridade: {ie}")
    except Exception as e:
        db.rollback()
        logger.error(f"  ERRO GERAL: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao registrar visita: {type(e).__name__}: {e}")

@router.post("/batch")
async def create_visitas_batch(
    batch: BSFVisitaBatch,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """Cria múltiplas visitas de uma vez (lançamento em lote)."""
    import logging
    import calendar
    logger = logging.getLogger("bsf.visitas")
    logger.info(f"BATCH: {batch.quantidade}x {batch.atividade_id} para {batch.tecnico_id} em {batch.mes}/{batch.ano}")

    try:
        cursor = db.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")

        # Distribuir datas ao longo do mês
        _, days_in_month = calendar.monthrange(batch.ano, batch.mes)
        today = datetime.now().strftime("%Y-%m-%d")

        for i in range(batch.quantidade):
            day = (i % days_in_month) + 1
            data_visita = f"{batch.ano}-{batch.mes:02d}-{day:02d}"
            cursor.execute("""
                INSERT INTO bsf_visitas (tecnico_id, beneficiario_id, municipio, comunidade, data_visita, status, atividade_id, data_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                batch.tecnico_id,
                f"Lote-{i+1}",
                batch.municipio,
                None,
                data_visita,
                'Realizada',
                batch.atividade_id,
                today
            ))

        db.commit()
        cursor.execute("PRAGMA foreign_keys = ON")
        logger.info(f"BATCH OK: {batch.quantidade} registros criados")

        return {"status": "sucesso", "message": f"{batch.quantidade} visitas registradas em lote"}
    except Exception as e:
        db.rollback()
        logger.error(f"BATCH ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no lançamento em lote: {e}")


@router.delete("/{visita_id}")
async def delete_visita(
    visita_id: int,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM bsf_visitas WHERE id = ?", (visita_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Visita não encontrada")
        db.commit()
        return {"status": "success", "message": "Visita excluída com sucesso", "id": visita_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir visita: {e}")

@router.put("/{visita_id}")
async def update_visita(
    visita_id: int,
    visita_in: BSFVisitaCreate,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """Atualiza uma visita existente."""
    cursor = db.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("""
            UPDATE bsf_visitas 
            SET tecnico_id = ?, beneficiario_id = ?, municipio = ?, comunidade = ?, data_visita = ?, status = ?, atividade_id = ?
            WHERE id = ?
        """, (
            visita_in.tecnico_id,
            visita_in.beneficiario_id,
            visita_in.municipio,
            visita_in.comunidade,
            visita_in.data_visita,
            visita_in.status,
            visita_in.atividade_id,
            visita_id
        ))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Visita não encontrada")
        
        db.commit()
        cursor.execute("PRAGMA foreign_keys = ON")
        return {"status": "sucesso", "message": "Visita atualizada"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar visita: {e}")

@router.get("/export")
async def export_planning(
    ano: int = 2026,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    # Exportar Metas e Realizado para Excel
    query = """
        SELECT 
            m.municipio, m.mes, m.ano, m.meta_total,
            (SELECT COUNT(*) FROM bsf_visitas v 
             WHERE v.municipio = m.municipio 
             AND strftime('%Y', v.data_visita) = cast(m.ano as text)
             AND strftime('%m', v.data_visita) = printf('%02d', m.mes)
            ) as realizado
        FROM bsf_metas m
        WHERE m.ano = ?
        ORDER BY m.municipio, m.mes
    """
    
    df = pd.read_sql_query(query, db, params=(ano,))
    
    # Adicionar cálculo de % e Status
    df['Percentual'] = (df['realizado'] / df['meta_total'] * 100).round(1)
    df['Status'] = df['Percentual'].apply(
        lambda x: 'Crítico' if x < 50 else ('Atenção' if x < 80 else 'Ótimo')
    )
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Planejamento BSF')
        
    output.seek(0)
    
    headers = {
        'Content-Disposition': f'attachment; filename="planejamento_bsf_{ano}.xlsx"'
    }
    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
