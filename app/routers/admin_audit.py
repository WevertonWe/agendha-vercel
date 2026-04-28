from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import json
import logging
from app.dependencies import get_db

router = APIRouter(prefix="/admin/auditoria", tags=["Admin Audit"])
from jinja2 import Environment, FileSystemLoader
_env = Environment(loader=FileSystemLoader("app/templates"), cache_size=0)
templates = Jinja2Templates(env=_env)
logger = logging.getLogger(__name__)

# Mock auth dependency - In real app, import get_current_user and check role="admin"
# For integration now, we assume middleware or simple auth check
# def admin_required(user = Depends(get_current_user)): ...

@router.get("/", response_class=HTMLResponse)
async def view_audit_dashboard(request: Request):
    """
    Renders the Admin Audit Dashboard.
    """
    # Security check placeholder
    # if not request.state.user.is_admin: raise HTTPException(403)
    return templates.TemplateResponse("admin/auditoria.html", {"request": request})

@router.get("/dados")
def get_audit_data(
    db: sqlite3.Connection = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    search: str = None
):
    """
    JSON endpoint for DataTables.
    """
    cursor = db.cursor()
    
    query = """
        SELECT id, usuario_id, data_hora, tabela, operacao, detalhes, valor_antigo, valor_novo
        FROM audit_logs
    """
    params = []
    
    if search:
        query += " WHERE tabela LIKE ? OR usuario_id LIKE ? OR detalhes LIKE ?"
        s = f"%{search}%"
        params.extend([s, s, s])
        
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    data = []
    for row in rows:
        data.append({
            "id": row["id"],
            "usuario": row["usuario_id"],
            "data": row["data_hora"],
            "tabela": row["tabela"],
            "operacao": row["operacao"],
            "detalhes": row["detalhes"],
            # Keep raw JSON string for client-side diffing to save bandwidth or parse here?
            # Parsing here is safer for frontend
            "valor_antigo": row["valor_antigo"], 
            "valor_novo": row["valor_novo"]
        })
        
    return {"data": data}

@router.post("/undo/{log_id}")
def undo_audit_action(
    log_id: int,
    db: sqlite3.Connection = Depends(get_db) # This uses AuditConnection, meaning Undo is also Audited!
):
    """
    Rollback a specific action.
    """
    try:
        cursor = db.cursor()
        cursor.execute("SELECT tabela, operacao, valor_antigo, valor_novo, registro_id FROM audit_logs WHERE id = ?", (log_id,))
        log = cursor.fetchone()
        
        if not log:
            raise HTTPException(404, "Log entry not found")
            
        tabela = log['tabela']
        operacao = log['operacao']
        registro_id = log['registro_id']
        valor_antigo_raw = log['valor_antigo']
        
        # Undo Logic
        if operacao == 'UPDATE':
            if not valor_antigo_raw:
                raise HTTPException(400, "Cannot undo Update without old value")
            
            old_data = json.loads(valor_antigo_raw)
            # Construct UPDATE query dynamically
            set_clause = ", ".join([f"{k} = ?" for k in old_data.keys()])
            values = list(old_data.values())
            values.append(registro_id)
            
            sql = f"UPDATE {tabela} SET {set_clause} WHERE id = ?"  # nosec
            cursor.execute(sql, values)
            
        elif operacao == 'INSERT':
            # Undo Insert = DELETE
            cursor.execute(f"DELETE FROM {tabela} WHERE id = ?", (registro_id,))  # nosec
            
        elif operacao == 'DELETE':
            # Undo Delete = INSERT
             if not valor_antigo_raw:
                raise HTTPException(400, "Cannot undo Delete without old value")
             
             old_data = json.loads(valor_antigo_raw)
             cols = ", ".join(old_data.keys())
             placeholders = ", ".join(["?" for _ in old_data])
             values = list(old_data.values())
             
             sql = f"INSERT INTO {tabela} ({cols}) VALUES ({placeholders})"  # nosec
             cursor.execute(sql, values)
             
        db.commit()
        return {"status": "success", "message": f"Action {log_id} reversed successfully."}

    except Exception as e:
        db.rollback()
        logger.error(f"Undo failed: {e}")
        raise HTTPException(500, f"Undo failed: {str(e)}")
