from pydantic import BaseModel
from datetime import datetime

class SugestaoProjetoBase(BaseModel):
    projeto_id: str
    usuario_id: str
    sugestao: str

class SugestaoProjetoCreate(SugestaoProjetoBase):
    pass

class SugestaoProjeto(SugestaoProjetoBase):
    id: int
    data_criacao: datetime

    class Config:
        from_attributes = True
