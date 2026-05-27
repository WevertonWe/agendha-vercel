import os
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.dependencies import get_db
from app.core.auth.dependencies import get_admin_user
from app.core.utils.crypto import encrypt_password, decrypt_password
from app.core.database import get_supabase
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["Admin Assets"])
logger = logging.getLogger(__name__)

# --- Schemas ---

class PowerBICredentialCreate(BaseModel):
    nome_projeto: str = Field(..., min_length=1)
    email_login: str = Field(..., min_length=1)
    senha: str = Field(..., min_length=1)
    status: str = Field("Ativo")

class PowerBICredentialUpdate(BaseModel):
    nome_projeto: Optional[str] = None
    email_login: Optional[str] = None
    senha: Optional[str] = None
    status: Optional[str] = None

class DispositivoCreate(BaseModel):
    tipo: str = Field(..., min_length=1)
    marca_modelo: str = Field(..., min_length=1)
    numero_serie_imei: str = Field(..., min_length=1)
    responsavel_atual: Optional[str] = None
    status: str = Field("Disponível")

class DispositivoUpdate(BaseModel):
    tipo: Optional[str] = None
    marca_modelo: Optional[str] = None
    numero_serie_imei: Optional[str] = None
    responsavel_atual: Optional[str] = None
    status: Optional[str] = None

# --- Helper de Compatibilidade de Banco ---

def execute_query(db, query: str, params: tuple = ()):
    """
    Executes a query and automatically handles parameter placeholder differences
    between SQLite ('?') and PostgreSQL ('%s').
    """
    cursor = db.cursor()
    # If connection class is not from local SQLite, translate placeholders to %s
    if db.__class__.__name__ not in ('AuditConnection', 'Connection', 'sqlite3.Connection'):
        query = query.replace('?', '%s')
    cursor.execute(query, params)
    return cursor

def row_to_dict(row) -> dict:
    """
    Safely converts a database row (sqlite3.Row or psycopg2 dict) to a standard dict.
    """
    if row is None:
        return {}
    if isinstance(row, dict):
        return row
    return dict(row)

# ==============================================================================
# CRUD - CREDENCIAIS POWERBI (bsf_powerbi_credentials)
# ==============================================================================

@router.get("/powerbi", response_model=List[dict])
def list_powerbi_credentials(
    db = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Lists all PowerBI credentials. Passwords are masked for security.
    """
    try:
        cursor = execute_query(db, "SELECT id, nome_projeto, email_login, status, created_at FROM bsf_powerbi_credentials ORDER BY id DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            row_dict = row_to_dict(r)
            row_dict["senha"] = "********"  # Mask password by default
            result.append(row_dict)
        return result
    except Exception as e:
        logger.error(f"Error listing PowerBI credentials: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao listar credenciais do PowerBI.")

@router.get("/powerbi/{id}/reveal")
def reveal_powerbi_password(
    id: int,
    db = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Decrypts and reveals the password for a specific PowerBI credential.
    Strictly protected by admin auth.
    """
    try:
        cursor = execute_query(db, "SELECT senha FROM bsf_powerbi_credentials WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Credencial não encontrada.")
        
        row_dict = row_to_dict(row)
        encrypted_pw = row_dict.get("senha")
        decrypted_pw = decrypt_password(encrypted_pw)
        
        return {"senha": decrypted_pw}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error revealing PowerBI password: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao revelar a senha.")

@router.post("/powerbi", status_code=201)
def create_powerbi_credential(
    payload: PowerBICredentialCreate,
    db = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Creates a new PowerBI credential with encrypted password storage.
    """
    try:
        encrypted_pw = encrypt_password(payload.senha)
        execute_query(
            db,
            "INSERT INTO bsf_powerbi_credentials (nome_projeto, email_login, senha, status) VALUES (?, ?, ?, ?)",
            (payload.nome_projeto, payload.email_login, encrypted_pw, payload.status)
        )
        db.commit()
        return {"status": "success", "message": "Credencial do PowerBI cadastrada com sucesso."}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating PowerBI credential: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao cadastrar credencial.")

@router.put("/powerbi/{id}")
def update_powerbi_credential(
    id: int,
    payload: PowerBICredentialUpdate,
    db = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Updates an existing PowerBI credential. Automatically encrypts the new password if provided.
    """
    try:
        cursor = execute_query(db, "SELECT * FROM bsf_powerbi_credentials WHERE id = ?", (id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Credencial não encontrada.")
        
        existing_dict = row_to_dict(existing)
        
        nome_projeto = payload.nome_projeto if payload.nome_projeto is not None else existing_dict["nome_projeto"]
        email_login = payload.email_login if payload.email_login is not None else existing_dict["email_login"]
        status = payload.status if payload.status is not None else existing_dict["status"]
        
        if payload.senha:
            senha = encrypt_password(payload.senha)
        else:
            senha = existing_dict["senha"]
            
        execute_query(
            db,
            "UPDATE bsf_powerbi_credentials SET nome_projeto = ?, email_login = ?, senha = ?, status = ? WHERE id = ?",
            (nome_projeto, email_login, senha, status, id)
        )
        db.commit()
        return {"status": "success", "message": "Credencial atualizada com sucesso."}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating PowerBI credential: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar credencial.")

@router.delete("/powerbi/{id}")
def delete_powerbi_credential(
    id: int,
    db = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Deletes a PowerBI credential.
    """
    try:
        cursor = execute_query(db, "SELECT id FROM bsf_powerbi_credentials WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Credencial não encontrada.")
        
        execute_query(db, "DELETE FROM bsf_powerbi_credentials WHERE id = ?", (id,))
        db.commit()
        return {"status": "success", "message": "Credencial excluída com sucesso."}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting PowerBI credential: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao excluir credencial.")


# ==============================================================================
# CRUD - INVENTÁRIO DE DISPOSITIVOS (agendha_dispositivos)
# ==============================================================================

@router.get("/dispositivos", response_model=List[dict])
def list_dispositivos(
    db = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Lists all devices in the inventory.
    """
    try:
        cursor = execute_query(db, "SELECT * FROM agendha_dispositivos ORDER BY id DESC")
        rows = cursor.fetchall()
        return [row_to_dict(r) for r in rows]
    except Exception as e:
        logger.error(f"Error listing dispositivos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao listar dispositivos.")

@router.post("/dispositivos", status_code=201)
def create_dispositivo(
    payload: DispositivoCreate,
    db = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Creates a new device inside the inventory. Ensures Serial/IMEI uniqueness.
    """
    try:
        # Check uniqueness of Serial / IMEI
        cursor = execute_query(db, "SELECT id FROM agendha_dispositivos WHERE numero_serie_imei = ?", (payload.numero_serie_imei,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Já existe um dispositivo cadastrado com este Número de Série / IMEI.")
        
        execute_query(
            db,
            "INSERT INTO agendha_dispositivos (tipo, marca_modelo, numero_serie_imei, responsavel_atual, status) VALUES (?, ?, ?, ?, ?)",
            (payload.tipo, payload.marca_modelo, payload.numero_serie_imei, payload.responsavel_atual, payload.status)
        )
        db.commit()
        return {"status": "success", "message": "Dispositivo cadastrado com sucesso."}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating dispositivo: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao cadastrar dispositivo.")

@router.put("/dispositivos/{id}")
def update_dispositivo(
    id: int,
    payload: DispositivoUpdate,
    db = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Updates device inventory specifications. Validates Serial/IMEI uniqueness across other assets.
    """
    try:
        cursor = execute_query(db, "SELECT * FROM agendha_dispositivos WHERE id = ?", (id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Dispositivo não encontrado.")
        
        existing_dict = row_to_dict(existing)
        
        tipo = payload.tipo if payload.tipo is not None else existing_dict["tipo"]
        marca_modelo = payload.marca_modelo if payload.marca_modelo is not None else existing_dict["marca_modelo"]
        numero_serie_imei = payload.numero_serie_imei if payload.numero_serie_imei is not None else existing_dict["numero_serie_imei"]
        responsavel_atual = payload.responsavel_atual if payload.responsavel_atual is not None else existing_dict["responsavel_atual"]
        status = payload.status if payload.status is not None else existing_dict["status"]
        
        # Validate Serial/IMEI change
        if numero_serie_imei != existing_dict["numero_serie_imei"]:
            cursor = execute_query(db, "SELECT id FROM agendha_dispositivos WHERE numero_serie_imei = ? AND id != ?", (numero_serie_imei, id))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Já existe outro dispositivo cadastrado com este Número de Série / IMEI.")
        
        execute_query(
            db,
            "UPDATE agendha_dispositivos SET tipo = ?, marca_modelo = ?, numero_serie_imei = ?, responsavel_atual = ?, status = ? WHERE id = ?",
            (tipo, marca_modelo, numero_serie_imei, responsavel_atual, status, id)
        )
        db.commit()
        return {"status": "success", "message": "Dispositivo atualizado com sucesso."}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating dispositivo: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar dispositivo.")

@router.delete("/dispositivos/{id}")
def delete_dispositivo(
    id: int,
    db = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Deletes a device from the inventory database.
    """
    try:
        cursor = execute_query(db, "SELECT id FROM agendha_dispositivos WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Dispositivo não encontrado.")
        
        execute_query(db, "DELETE FROM agendha_dispositivos WHERE id = ?", (id,))
        db.commit()
        return {"status": "success", "message": "Dispositivo excluído com sucesso."}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting dispositivo: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao excluir dispositivo.")

# ==============================================================================
# STORAGE & UPLOAD OF DEVICES TERMS (PDF UPLOAD & EXPIRING URLs)
# ==============================================================================

@router.post("/dispositivos/{id}/upload-termo")
async def upload_dispositivo_termo(
    id: int,
    file: UploadFile = File(...),
    db = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Uploads a device ownership / assignment term PDF.
    Saves to Supabase Private Bucket 'termos-dispositivos' or local storage fallback.
    """
    try:
        cursor = execute_query(db, "SELECT * FROM agendha_dispositivos WHERE id = ?", (id,))
        device = cursor.fetchone()
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo não encontrado.")
        
        # PDF Extension validation
        if not file.filename.lower().endswith(".pdf") and file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos.")
        
        file_content = await file.read()
        file_name = f"termo_dispositivo_{id}.pdf"
        saved_path = ""
        
        # Try Supabase Storage Upload
        supabase_success = False
        try:
            supabase = get_supabase()
            if supabase:
                # Private upload to termos-dispositivos
                supabase.storage.from_("termos-dispositivos").upload(
                    path=file_name,
                    file=file_content,
                    file_options={"content-type": "application/pdf", "x-upsert": "true"}
                )
                saved_path = file_name
                supabase_success = True
                logger.info(f"Term for device {id} uploaded successfully to Supabase.")
        except Exception as se:
            logger.warning(f"Supabase Storage failed or is not configured: {se}. Falling back to local storage.")
        
        # Local Fallback
        if not supabase_success:
            local_dir = settings.UPLOAD_FOLDER / "termos"
            os.makedirs(local_dir, exist_ok=True)
            local_file_path = local_dir / file_name
            with open(local_file_path, "wb") as f:
                f.write(file_content)
            saved_path = f"local:{file_name}"
            logger.info(f"Term for device {id} saved locally at {local_file_path}.")
        
        # Update database with saved path
        execute_query(db, "UPDATE agendha_dispositivos SET url_termo_pdf = ? WHERE id = ?", (saved_path, id))
        db.commit()
        
        return {"status": "success", "message": "Termo de dispositivo enviado com sucesso.", "path": saved_path}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading term for device {id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao realizar o upload do termo.")

@router.get("/dispositivos/{id}/termo-url")
def get_dispositivo_termo_url(
    id: int,
    db = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Generates an expiring 5-minute signed URL from Supabase for the device assignment term.
    If the term is local, returns a route to retrieve it.
    """
    try:
        cursor = execute_query(db, "SELECT url_termo_pdf FROM agendha_dispositivos WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Dispositivo não encontrado.")
        
        row_dict = row_to_dict(row)
        url_termo = row_dict.get("url_termo_pdf")
        
        if not url_termo:
            raise HTTPException(status_code=404, detail="Este dispositivo ainda não possui um termo enviado.")
        
        # Handle Local File Serving fallback
        if url_termo.startswith("local:"):
            filename = url_termo.replace("local:", "")
            local_url = f"/api/admin/dispositivos/local-termo/{filename}"
            return {"url": local_url}
        
        # Handle Supabase Signed URL
        try:
            supabase = get_supabase()
            res = supabase.storage.from_("termos-dispositivos").create_signed_url(
                path=url_termo,
                expires_in=300
            )
            
            # Treat dynamic object models returned by python SDK response
            if isinstance(res, dict):
                signed_url = res.get("signedURL") or res.get("signedUrl") or res.get("url")
            else:
                signed_url = getattr(res, "signedURL", None) or getattr(res, "signedUrl", None) or getattr(res, "url", None) or res
            
            if not signed_url:
                raise ValueError("Signed URL was not returned by Supabase Storage Client.")
                
            return {"url": signed_url}
        except Exception as se:
            logger.error(f"Error generating Supabase signed URL for term {url_termo}: {se}. Checking local fallback.")
            # Fallback to check if a local file exists with that name
            filename = url_termo
            local_path = settings.UPLOAD_FOLDER / "termos" / filename
            if os.path.exists(local_path):
                return {"url": f"/api/admin/dispositivos/local-termo/{filename}"}
            raise HTTPException(status_code=500, detail="Erro ao gerar a URL do termo do Supabase Storage.")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving term url for device {id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao obter link do termo.")

@router.get("/dispositivos/local-termo/{filename}")
def get_local_termo(
    filename: str,
    current_user = Depends(get_admin_user)
):
    """
    Serves a device term PDF saved locally (only accessible to authenticated Admins).
    """
    local_path = settings.UPLOAD_FOLDER / "termos" / filename
    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="Arquivo de termo não encontrado localmente.")
    
    return FileResponse(
        path=local_path,
        media_type="application/pdf",
        filename=filename
    )
