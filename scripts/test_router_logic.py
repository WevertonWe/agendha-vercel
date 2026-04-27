
from typing import Optional
from pydantic import BaseModel

# --- MOCKS DO MODELS.PY (Como deve estar agora) ---
class BSFVisitaBase(BaseModel):
    tecnico_id: str
    beneficiario_id: str
    municipio: str
    comunidade: Optional[str] = None
    data_visita: str
    atividade_id: int
    status: Optional[str] = 'Realizada'

class BSFVisitaCreate(BSFVisitaBase):
    pass

class BSFVisita(BSFVisitaBase):
    id: int
    atividade_nome: Optional[str] = None

# --- SIMULAÇÃO DO ROUTER ---
def simulate_router():
    print("Simulando create_visita...")
    
    # 1. Payload vindo do frontend (sem ID, como corrigido)
    payload = {
        "tecnico_id": "tech",
        "beneficiario_id": "benef",
        "municipio": "muni",
        "data_visita": "2026-01-01",
        "atividade_id": 1,
        "status": "Realizada"
    }
    
    # 2. Criação do objeto Pydantic de entrada
    visita_in = BSFVisitaCreate(**payload)
    print(f"Objeto Entrada: {visita_in}")
    
    visita_id_gerado = 123
    atividade_nome_buscado = "Atividade Teste"
    
    # 3. Lógica do Router (Original - Pode falhar se visita_in tiver 'id')
    try:
        print("\nTentativa 1: **visita_in.dict()")
        response = BSFVisita(
            id=visita_id_gerado,
            **visita_in.dict(),
            atividade_nome=atividade_nome_buscado
        )
        print("Sucesso Tentativa 1!")
    except Exception as e:
        print(f"Erro Tentativa 1: {e}")

    # 4. Simular caso onde 'id' entra sem querer no dict (ex: se o model tiver id opcional e o user mandar)
    # Vamos 'sujar' o dict para testar a robustez do exclude
    data_sujo = visita_in.dict()
    data_sujo['id'] = 999 # User mandou ID malandramente e o model aceitou (hipotese)
    
    try:
        print("\nTentativa 2: Simulação de 'id' intruso no dict")
        # Se data_sujo tem 'id', isso VAI falhar:
        # BSFVisita(id=123, id=999, ...) -> TypeError
        response = BSFVisita(
            id=visita_id_gerado,
            **data_sujo, 
            atividade_nome=atividade_nome_buscado
        )
        print("Sucesso Tentativa 2 (Inesperado se id estava duplicado)!")
    except TypeError as e:
        print(f"Erro Esperado Tentativa 2: {e}")

    # 5. Lógica Proposta (Robustez)
    try:
        print("\nTentativa 3: Com exclude={'id'}")
        # Mesmo se o dict tiver id, removemos antes de passar
        safe_dict = data_sujo.copy()
        if 'id' in safe_dict:
             del safe_dict['id'] # Simulating exclude={'id'} manually for dict, or using pydantic's exclude
        
        # Pydantic dict(exclude=) logic check
        # visita_in.dict(exclude={'id'}) should work if visita_in had id. 
        # But BSFVisitaCreate doesn't have id field anymore.
        
        response = BSFVisita(  # noqa: F841
            id=visita_id_gerado,
            **visita_in.dict(exclude={'id'}), # Validation
            atividade_nome=atividade_nome_buscado
        )
        print("Sucesso Tentativa 3 (Com exclude)!")
    except Exception as e:
        print(f"Erro Tentativa 3: {e}")

if __name__ == "__main__":
    simulate_router()
