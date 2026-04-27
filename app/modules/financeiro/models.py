from typing import Optional
from pydantic import BaseModel

# ==============================================================================
# MODELOS DE DADOS - FINANCEIRO
# ==============================================================================

# --- Entidades (Pessoas/Empresas) ---
class FinanceiroEntidadeBase(BaseModel):
    tipo_pessoa: Optional[str] = None # 'PF' ou 'PJ'
    nome_razao_social: str
    cpf_cnpj: Optional[str] = None
    funcao: Optional[str] = None
    municipio_atuacao: Optional[str] = None
    endereco_rua: Optional[str] = None
    endereco_numero: Optional[str] = None
    endereco_bairro: Optional[str] = None
    endereco_cidade: Optional[str] = None
    endereco_cep: Optional[str] = None
    contato_telefone: Optional[str] = None
    contato_email: Optional[str] = None
    dados_bancarios_banco: Optional[str] = None
    dados_bancarios_agencia: Optional[str] = None
    dados_bancarios_conta: Optional[str] = None

class FinanceiroEntidade(FinanceiroEntidadeBase):
    id: int

# --- Projetos ---
class FinanceiroProjetoBase(BaseModel):
    nome: str
    numero_contrato: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    valor_total: Optional[float] = None

class FinanceiroProjeto(FinanceiroProjetoBase):
    id: int

# --- Metas ---
class FinanceiroMetaBase(BaseModel):
    projeto_id: int
    numero_meta: Optional[str] = None
    descricao: Optional[str] = None

class FinanceiroMeta(FinanceiroMetaBase):
    id: int

# --- Etapas ---
class FinanceiroEtapaBase(BaseModel):
    meta_id: int
    numero_etapa: Optional[str] = None
    descricao: Optional[str] = None

class FinanceiroEtapa(FinanceiroEtapaBase):
    id: int

# --- Rubricas ---
class FinanceiroRubricaBase(BaseModel):
    etapa_id: int
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    unidade: Optional[str] = None
    quantidade_programada: Optional[float] = None
    valor_unitario_programado: Optional[float] = None
    valor_total_programado: Optional[float] = None

class FinanceiroRubrica(FinanceiroRubricaBase):
    id: int

# --- Lançamentos ---
class FinanceiroLancamentoBase(BaseModel):
    projeto_id: int
    rubrica_id: int
    entidade_id: Optional[int] = None
    data_lancamento: Optional[str] = None
    numero_processo: Optional[str] = None
    numero_nota_fiscal: Optional[str] = None
    historico: Optional[str] = None
    quantidade_executada: Optional[float] = None
    valor_total_executado: Optional[float] = None

class FinanceiroLancamento(FinanceiroLancamentoBase):
    id: int
