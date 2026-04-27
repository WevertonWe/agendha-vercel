from fastapi import APIRouter

router = APIRouter(prefix="/api/financeiro", tags=["Financeiro"])

@router.get("/status")
def get_status():
    return {"status": "Módulo Financeiro Ativo"}
