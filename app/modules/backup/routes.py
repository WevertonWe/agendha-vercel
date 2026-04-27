from fastapi import APIRouter, Depends, HTTPException
from app.core.auth.dependencies import get_admin_user
from app.core.auth.models import UserInDB
from app.modules.backup.services import realizar_backup_agora

router = APIRouter(prefix="/api/backup", tags=["Backup"])

@router.post("/manual")
async def manual_backup(current_user: UserInDB = Depends(get_admin_user)):
    """
    Aciona o backup manual do banco de dados.
    Apenas administradores podem realizar esta ação.
    """
    filename = realizar_backup_agora()
    if not filename:
        raise HTTPException(status_code=500, detail="Falha ao realizar backup")
    
    return {"message": "Backup realizado com sucesso", "filename": filename}
