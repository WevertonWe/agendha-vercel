from typing import Optional
from pydantic import BaseModel

class FornecedorBase(BaseModel):
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj_cpf: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None

class Fornecedor(FornecedorBase):
    id: int

class FornecedorCreate(FornecedorBase):
    pass

class FornecedorUpdate(FornecedorBase):
    pass
