
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import sqlite3
from app.core.database import get_db_connection

from app.modules.bahia_sem_fome.models import BSFMeta, BSFMetaCreate, BSFMetaBulk, BSFMetaContrato

router = APIRouter(prefix="/api/bsf/metas", tags=["BSF - Metas"])

@router.get("/tecnicos", response_model=List[str])
async def list_tecnicos(db: sqlite3.Connection = Depends(get_db_connection)):
    """Lista todos os técnicos que têm responsabilidade ou visitas registradas."""
    cursor = db.cursor()
    # Union of technicians from metas (responsibles) and visits (executors)
    cursor.execute("""
        SELECT DISTINCT tecnico_responsavel FROM bsf_metas WHERE tecnico_responsavel IS NOT NULL
        UNION
        SELECT DISTINCT tecnico_id FROM bsf_visitas WHERE tecnico_id IS NOT NULL
        ORDER BY 1
    """)
    rows = cursor.fetchall()
    return [r[0] for r in rows if r[0]]

@router.get("")
async def list_metas(
    ano: Optional[int] = Query(None, description="Ano de referência (vazio = todos)"),
    mes: Optional[int] = Query(None, description="Mês de referência"),
    tecnico: Optional[str] = Query(None, description="Filtrar por Técnico"),
    db: sqlite3.Connection = Depends(get_db_connection)
):
    cursor = db.cursor()
    
    # 1. Status Global (Metas do Contrato vs Realizado)
    global_status = []
    
    if ano:
        # Metas de um ano específico
        cursor.execute("""
            SELECT mc.*, a.nome
            FROM bsf_metas_contrato mc
            JOIN bsf_atividades a ON mc.atividade_id = a.id
            WHERE mc.ano = ?
        """, (ano,))
    else:
        # Todos os anos: meta fixa do contrato (MAX, não SUM)
        cursor.execute("""
            SELECT mc.atividade_id, a.nome,
                   MIN(mc.id) as id,
                   MAX(mc.meta_mensal) as meta_mensal,
                   MAX(mc.meta_anual) as meta_anual,
                   0 as ano
            FROM bsf_metas_contrato mc
            JOIN bsf_atividades a ON mc.atividade_id = a.id
            GROUP BY mc.atividade_id, a.nome
        """)
    metas_contrato = cursor.fetchall()
    
    for row in metas_contrato:
        meta = dict(row)
        # Contar realizado
        query_realizado = "SELECT COUNT(*) FROM bsf_visitas WHERE atividade_id = ?"
        params_realizado = [meta['atividade_id']]
        
        if ano:
            query_realizado += " AND strftime('%Y', data_visita) = ?"
            params_realizado.append(str(ano))
        
        if mes:
            query_realizado += " AND strftime('%m', data_visita) = ?"
            params_realizado.append(f"{mes:02d}")
            
        if tecnico:
            query_realizado += " AND tecnico_id = ?"
            params_realizado.append(tecnico)

        # Meta Alvo: técnico+mês → meta individual; mês → meta_mensal; senão → meta_anual
        meta_alvo = meta['meta_anual']
        if mes and ano:
            meta_alvo = meta['meta_mensal']

        if tecnico and mes and ano:
            cursor.execute("""
                SELECT valor_meta FROM bsf_metas_tecnicos
                WHERE tecnico_id = ? AND atividade_id = ? AND mes = ? AND ano = ?
            """, (tecnico, meta['atividade_id'], mes, ano))
            meta_tec = cursor.fetchone()
            if meta_tec:
                meta_alvo = meta_tec[0]

        cursor.execute(query_realizado, params_realizado)
        realizado = cursor.fetchone()[0]
        
        percent = (realizado / meta_alvo * 100) if meta_alvo > 0 else 0
        
        global_status.append(BSFMetaContrato(
            id=meta['id'],
            atividade_id=meta['atividade_id'],
            atividade_nome=meta['nome'],
            ano=meta.get('ano', 0),
            meta_mensal=meta_alvo if (mes and ano) else meta['meta_mensal'],
            meta_anual=meta['meta_anual'],
            total_realizado=realizado,
            percentual=round(percent, 1)
        ))

    # 2. Municípios (Cards) — UNION: aparecem mesmo sem entrada em bsf_metas
    query_municipios = """
        SELECT municipio, tecnico_responsavel FROM (
            SELECT municipio, MAX(tecnico_responsavel) as tecnico_responsavel FROM bsf_metas GROUP BY municipio
            UNION
            SELECT DISTINCT municipio, MAX(tecnico_id) as tecnico_responsavel FROM bsf_visitas WHERE municipio IS NOT NULL GROUP BY municipio
        ) sub GROUP BY municipio
    """
    cursor.execute(query_municipios)
    metas_rows = cursor.fetchall()
    
    municipios_results = []
    
    for row in metas_rows:
        muni = dict(row)
        
        query_atv_muni = """
            SELECT a.nome, COUNT(v.id) as qtd
            FROM bsf_atividades a
            JOIN bsf_visitas v ON v.atividade_id = a.id
            WHERE v.municipio = ?
        """
        params_atv = [muni['municipio']]

        if ano:
            query_atv_muni += " AND strftime('%Y', v.data_visita) = ?"
            params_atv.append(str(ano))

        if mes:
            query_atv_muni += " AND strftime('%m', v.data_visita) = ?"
            params_atv.append(f"{mes:02d}")
            
        if tecnico:
            query_atv_muni += " AND v.tecnico_id = ?"
            params_atv.append(tecnico)
            
        query_atv_muni += " GROUP BY a.id, a.nome ORDER BY qtd DESC"
        
        cursor.execute(query_atv_muni, params_atv)
        atividades_stats = [{"nome": r[0], "count": r[1]} for r in cursor.fetchall()]
        
        total_realizado_muni = sum(item['count'] for item in atividades_stats)

        municipios_results.append(BSFMeta(
            id=0, 
            municipio=muni['municipio'],
            mes=mes if mes else 0,
            ano=ano if ano else 0,
            meta_total=0, 
            tecnico_responsavel=muni['tecnico_responsavel'],
            visitas_realizadas=total_realizado_muni,
            progresso_percentual=0,
            resumo_atividades=atividades_stats
        ))

    return {
        "global_status": global_status,
        "municipios": municipios_results
    }
    

@router.post("/", response_model=BSFMeta)
async def create_or_update_meta(
    meta_in: BSFMetaCreate,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    # Mantendo compatibilidade se alguém chamar, mas a lógica mudou.
    # Apenas cria o registro do município na tabela bsf_metas para ele aparecer na lista.
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO bsf_metas (municipio, mes, ano, meta_total, tecnico_responsavel) VALUES (?, ?, ?, ?, ?)",
        (meta_in.municipio, meta_in.mes, meta_in.ano, 0, meta_in.tecnico_responsavel)
    )
    db.commit()
    return BSFMeta(
        id=cursor.lastrowid, 
        municipio=meta_in.municipio, mes=meta_in.mes, ano=meta_in.ano, 
        meta_total=0, tecnico_responsavel=meta_in.tecnico_responsavel
    )

@router.post("/bulk-municipio")
async def create_bulk_municipio(
    meta_in: BSFMetaBulk,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """Cria 'pastas' para os 12 meses de um município."""
    cursor = db.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM bsf_metas WHERE municipio = ? AND ano = ?", (meta_in.municipio, meta_in.ano))
    if cursor.fetchone()[0] > 0:
        raise HTTPException(status_code=400, detail=f"Município '{meta_in.municipio}' já existe.")
    
    try:
        for mes in range(1, 13):
            cursor.execute(
                "INSERT INTO bsf_metas (municipio, mes, ano, meta_total, tecnico_responsavel) VALUES (?, ?, ?, ?, ?)",
                (meta_in.municipio, mes, meta_in.ano, 0, meta_in.tecnico_responsavel)
            )
        db.commit()
        
        return {
            "status": "success",
            "message": f"Município '{meta_in.municipio}' adicionado!",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro: {e}")


@router.put("/bulk-municipio/{municipio_original}")
async def update_bulk_municipio(
    municipio_original: str,
    folha_in: dict, # Recebe {"novo_nome": str, "novo_tecnico": str}
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Atualiza o nome do município e o técnico responsável em TODAS as metas.
    Também atualiza o nome do município na tabela de visitas para manter integridade.
    """
    cursor = db.cursor()
    novo_nome = folha_in.get('novo_nome')
    novo_tecnico = folha_in.get('novo_tecnico')
    
    if not novo_nome:
        raise HTTPException(status_code=400, detail="Novo nome do município é obrigatório")

    try:
        # 1. Verificar se o novo nome já existe (se for diferente do original)
        if novo_nome != municipio_original:
            cursor.execute("SELECT COUNT(*) FROM bsf_metas WHERE municipio = ? AND municipio != ?", (novo_nome, municipio_original))
            if cursor.fetchone()[0] > 0:
                raise HTTPException(status_code=400, detail=f"O município '{novo_nome}' já existe.")

        # 2. Atualizar Metas
        cursor.execute(
            "UPDATE bsf_metas SET municipio = ?, tecnico_responsavel = ? WHERE municipio = ?",
            (novo_nome, novo_tecnico, municipio_original)
        )
        metas_afetadas = cursor.rowcount

        # 3. Atualizar Visitas (Integridade)
        visitas_afetadas = 0
        if novo_nome != municipio_original:
            cursor.execute(
                "UPDATE bsf_visitas SET municipio = ? WHERE municipio = ?",
                (novo_nome, municipio_original)
            )
            visitas_afetadas = cursor.rowcount

        db.commit()
        
        return {
            "status": "success",
            "message": "Município atualizado com sucesso!",
            "original": municipio_original,
            "novo": novo_nome,
            "metas_atualizadas": metas_afetadas,
            "visitas_atualizadas": visitas_afetadas
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar município: {e}")

@router.delete("/{meta_id}")
async def delete_meta(
    meta_id: int,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """Exclui uma meta específica (card de município/mês)."""
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM bsf_metas WHERE id = ?", (meta_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        db.commit()
        return {"status": "success", "message": "Meta excluída com sucesso", "id": meta_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir meta: {e}")

@router.delete("/municipio/{municipio}")
async def delete_municipio(
    municipio: str,
    ano: Optional[int] = None,
    db: sqlite3.Connection = Depends(get_db_connection)
):
    """Exclui todas as metas e visitas de um município. Se ano for omitido, limpa tudo."""
    from urllib.parse import unquote
    municipio = unquote(municipio)
    
    cursor = db.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = OFF")

        # Deletar visitas
        if ano:
            cursor.execute("DELETE FROM bsf_visitas WHERE municipio = ? AND strftime('%Y', data_visita) = ?", (municipio, str(ano)))
        else:
            cursor.execute("DELETE FROM bsf_visitas WHERE municipio = ?", (municipio,))
        visitas_removidas = cursor.rowcount

        # Deletar metas
        if ano:
            cursor.execute("DELETE FROM bsf_metas WHERE municipio = ? AND ano = ?", (municipio, ano))
        else:
            cursor.execute("DELETE FROM bsf_metas WHERE municipio = ?", (municipio,))
        metas_removidas = cursor.rowcount

        cursor.execute("PRAGMA foreign_keys = ON")

        if metas_removidas == 0 and visitas_removidas == 0:
            raise HTTPException(status_code=404, detail=f"Município '{municipio}' não encontrado")
        
        db.commit()
        return {"message": f"'{municipio}' excluído", "metas_removidas": metas_removidas, "visitas_removidas": visitas_removidas}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir: {e}")
