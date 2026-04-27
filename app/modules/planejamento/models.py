from pydantic import BaseModel
from typing import Optional

class CronogramaExecucaoBase(BaseModel):
    municipio: str
    semana_referencia: str # Format YYYY-MM-DD
    quant_cisternas: int = 0
    meta_planejada: int = 0
    qtd_executada: int = 0

class CronogramaExecucao(CronogramaExecucaoBase):
    id: int
    saldo_acumulado: Optional[int] = 0

class CronogramaUpdate(BaseModel):
    semana_referencia: Optional[str] = None
    quant_cisternas: Optional[int] = None
    meta_planejada: Optional[int] = None
    qtd_executada: Optional[int] = None
