from fastapi import APIRouter

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_stats():
    return {"total_projetos": 3, "usuarios_ativos": 10}
