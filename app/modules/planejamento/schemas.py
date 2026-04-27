from pydantic import BaseModel
from typing import Optional

class CronogramaExecucaoBase(BaseModel):
    municipio: str
    semana_referencia: str 
    quant_cisternas: int = 0
    meta_planejada: int = 0
    qtd_executada: int = 0

class CronogramaExecucaoCreate(CronogramaExecucaoBase):
    pass

class CronogramaExecucaoResponse(CronogramaExecucaoBase):
    id: int
    saldo_acumulado: int = 0
    
    class Config:
        from_attributes = True

class CronogramaUpdate(BaseModel):
    semana_referencia: Optional[str] = None
    quant_cisternas: Optional[int] = None
    meta_planejada: Optional[int] = None
    qtd_executada: Optional[int] = None

class SchemaGeracao(BaseModel):
    data_inicio: str # YYYY-MM-DD
    total_cisternas: int
    meta_semanal: int
