
from typing import Optional, List
from pydantic import BaseModel

# ==============================================================================
# MODELOS DE DADOS - BAHIA SEM FOME (BSF)
# ==============================================================================

class BSFAtividade(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None

class BSFMetaBase(BaseModel):
    municipio: str
    mes: int
    ano: int
    meta_total: int
    tecnico_responsavel: Optional[str] = None

class BSFMetaCreate(BSFMetaBase):
    pass

class BSFMetaBulk(BaseModel):
    municipio: str
    ano: int
    meta_mensal: int
    tecnico_responsavel: Optional[str] = None
    composicao: Optional[List[dict]] = [] # [{"atividade_id": 1, "valor": 10}, ...]

class BSFMeta(BSFMetaBase):
    id: int
    progresso_percentual: Optional[float] = 0.0
    visitas_realizadas: Optional[int] = 0
    resumo_atividades: Optional[List[dict]] = [] # [{"nome": "Visita", "count": 10}, ...]

class BSFVisitaBase(BaseModel):
    tecnico_id: str
    beneficiario_id: str
    municipio: str
    comunidade: Optional[str] = None
    data_visita: str # YYYY-MM-DD
    atividade_id: int # NOVO: Obrigatório
    status: Optional[str] = 'Realizada'

class BSFVisitaCreate(BSFVisitaBase):
    quantidade: Optional[int] = 1 # Novo: Para suporte a envio híbrido (Unitário/Lote)

class BSFVisita(BSFVisitaBase):
    id: int
    atividade_nome: Optional[str] = None # Para exibição


class BSFMetaContrato(BaseModel):
    id: int
    atividade_id: int
    atividade_nome: Optional[str] = None
    ano: int
    meta_mensal: int
    meta_anual: int
    total_realizado: Optional[int] = 0
    percentual: Optional[float] = 0.0

class BSFDashboardData(BaseModel):
    global_status: List[BSFMetaContrato]
    municipios: List[BSFMeta]


class BSFVisitaBatch(BaseModel):
    municipio: str
    tecnico_id: str
    atividade_id: int
    mes: int
    ano: int
    quantidade: int


class BSFMetaTecnico(BaseModel):
    tecnico_id: str
    atividade_id: int
    mes: int
    ano: int
    valor_meta: int
