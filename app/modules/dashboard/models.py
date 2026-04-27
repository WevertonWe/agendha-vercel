from pydantic import BaseModel

# ==============================================================================
# MODELOS DE DADOS - DASHBOARD
# ==============================================================================

class DashboardStats(BaseModel):
    total_projetos: int
    usuarios_ativos: int
