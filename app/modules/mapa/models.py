from pydantic import BaseModel
from typing import Optional

class PontoCreate(BaseModel):
    nome: str
    tipo: str
    latitude: float
    longitude: float
    descricao: Optional[str] = None
    projeto_id: Optional[int] = None
    poligono: Optional[str] = None
    cor: Optional[str] = None
    contexto: Optional[str] = 'geral'
    responsavel: Optional[str] = None
    status_beneficiario: Optional[str] = None
    verificacao_bsf: Optional[bool] = False
    endereco: Optional[str] = None
    foto_url: Optional[str] = None
    imagem: Optional[str] = None
    municipio: Optional[str] = None
    comunidade: Optional[str] = None
    area_telhado: Optional[float] = None
    status_obra: Optional[str] = None
    edital: Optional[str] = None
    beneficiario: Optional[str] = None
    data_coleta: Optional[str] = None

class PontoResponse(PontoCreate):
    id: int
    full_address: Optional[str] = None

    def __init__(self, **data):
        if not data.get('foto_url') and data.get('imagem'):
            data['foto_url'] = data['imagem']
        elif not data.get('imagem') and data.get('foto_url'):
            data['imagem'] = data['foto_url']
        super().__init__(**data)
        if self.endereco:
            self.full_address = self.endereco
        elif self.comunidade and self.municipio:
            self.full_address = f"{self.comunidade}, {self.municipio}"
        elif self.descricao and "Rua" in self.descricao:
             # Fallback simples se a descricao contiver dados de endereço
             self.full_address = self.descricao[:100] # Truncate for safety
        else:
             self.full_address = f"{self.latitude}, {self.longitude}"

    class Config:
        from_attributes = True

class CategoriaCreate(BaseModel):
    nome: str
    cor: str # Hex color e.g. #FF0000

class CategoriaResponse(CategoriaCreate):
    id: int

    class Config:
        from_attributes = True
