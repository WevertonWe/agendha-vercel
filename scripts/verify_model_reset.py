
import requests  # noqa: F401
import json
from datetime import datetime

# URL da API
API_URL = "http://localhost:8000/api/bsf/visitas"

def registrar_visita_teste():
    print("\n--- Teste de Registro de Visita (Simulação Front-end) ---")
    
    # Dados simulando o formulário
    dados_visita = {
        "visitaTecnico": "tecnico_teste_reset",
        "visitaBeneficiario": "benef_teste_reset",
        "municipio": "Salvador",
        "comunidade": "Centro",
        "data_visita": datetime.now().strftime("%Y-%m-%d"),
        "atividade_id": "1", # String vinda do select HTML
        "status": "Realizada",
        "id": None # Opcional: simular o campo que causava problema
    }

    # Lógica do Front-end (producao.html)
    print("1. Dados Brutos do Formulário:", json.dumps(dados_visita, indent=2))
    
    # 1. Transformação de chaves
    payload = {
        "tecnico_id": dados_visita["visitaTecnico"],
        "beneficiario_id": dados_visita["visitaBeneficiario"],
        "municipio": dados_visita["municipio"],
        "comunidade": dados_visita["comunidade"],
        "data_visita": dados_visita["data_visita"],
        "status": dados_visita["status"]
    }

    # 2. Conversão de Inteiro
    try:
        payload["atividade_id"] = int(dados_visita["atividade_id"])
    except:  # noqa: E722
        payload["atividade_id"] = None
    
    # 3. Limpeza de ID (Ação Crítica)
    if "id" in dados_visita:
        print("   [Front] 'id' encontrado nos dados brutos. Ignorando no payload final.")
    
    # Payload Final
    print("2. Payload Enviado para API:", json.dumps(payload, indent=2))
    
    # Validação Local (Simulando Backend)
    try:
        from app.modules.bahia_sem_fome.models import BSFVisitaCreate
        print("\n3. Validação Backend (BSFVisitaCreate):")
        obj = BSFVisitaCreate(**payload)
        print("   [OK] Modelo aceitou o payload:", obj)
    except Exception as e:
        print("   [ERRO] Modelo rejeitou o payload:", e)

if __name__ == "__main__":
    registrar_visita_teste()
