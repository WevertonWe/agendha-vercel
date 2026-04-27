from typing import List, Optional
from pydantic import BaseModel
import datetime

# ==============================================================================
# MODELOS DE DADOS - COTAÇÕES
# ==============================================================================

class PropostaBase(BaseModel):
    nome_fornecedor: str # Mantido como string (pode vir do form ou do cadastro)
    fornecedor_id: Optional[int] = None # Novo campo integration
    tipo_fornecedor: Optional[str] = None
    data_contrato: Optional[str] = None
    valor: Optional[float] = None
    status: Optional[str] = None
    observacao: Optional[str] = None
    caminho_arquivo: Optional[str] = None


class Proposta(PropostaBase):
    id: int
    cotacao_master_id: int


class CotacaoItemBase(BaseModel):
    material_id: int
    quantidade: float

class CotacaoItem(CotacaoItemBase):
    id: int
    cotacao_master_id: int
    # Optional fields for display if needed (e.g. material_nome) but usually backend joins or front handles

class CotacaoMasterBase(BaseModel):
    codigo_cotacao: str
    titulo: str
    descricao: Optional[str] = None
    status: Optional[str] = 'Aberto'
    itens: List[CotacaoItemBase] = [] # Novo: Lista de itens para criação


class CotacaoMaster(CotacaoMasterBase):
    id: int
    data_criacao: datetime.datetime
    propostas: List[Proposta] = []
    itens_detalhes: List[CotacaoItem] = [] # Para retorno detalhado


class AnaliseCotacaoInput(BaseModel):
    cotacao_id: int
    codigo_cotacao: str
    texto_analise: str
    descricao_item: str
    # Proposta 1 (Vencedora)
    empresa1_nome: str
    empresa1_valor: float
    # Proposta 2
    empresa2_nome: Optional[str] = None
    empresa2_valor: Optional[float] = None
    # Proposta 3
    empresa3_nome: Optional[str] = None
    empresa3_valor: Optional[float] = None
