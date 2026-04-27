
import requests  # noqa: F401
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/bsf/visitas"

def test_create_visita():
    # Payload similar ao enviado pelo frontend
    payload = {
        "tecnico_id": "test_tech_schema",
        "beneficiario_id": "benef_test",
        "municipio": "TestCity",
        "comunidade": "TestCommunity",
        "data_visita": datetime.now().strftime("%Y-%m-%d"),
        "atividade_id": 1, # ID válido (assumindo que existe atividade com ID 1)
        "status": "Realizada"
        # Note: NO 'id' field here
    }
    
    print(f"Sending payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Se o servidor não estiver rodando, vai falhar a conexão.
        # Mas o objetivo é validar o schema se a API estivesse ativa.
        # Como não posso garantir que a API esteja rodando na porta 8000 agora,
        # vou simular a validação Pydantic importando o modelo diretamente.
        
        from app.modules.bahia_sem_fome.models import BSFVisitaCreate
        
        print("\nValidating with Pydantic model directly...")
        obj = BSFVisitaCreate(**payload)
        print(f"Validation SUCCESS: {obj}")
        
        # Testar com ID nulo (simulando envio errado)
        payload_with_id = payload.copy()
        payload_with_id['id'] = None
        print("\nValidating payload WITH 'id': None ...")
        
        # Isso deve FALHAR se 'id' não for permitido em BSFVisitaCreate (herança de BSFVisitaBase)
        # Como removi 'id' de BSFVisitaBase, ele deve ignorar se for Extra='ignore' ou falhar se Extra='forbid'.
        # Por padrão Pydantic v1 ignora extras, v2 depende da config.
        try:
             obj2 = BSFVisitaCreate(**payload_with_id)
             print(f"Validation with ID=None result: {obj2}") 
             # Se passou, verifique se 'id' está no objeto
             if hasattr(obj2, 'id'):
                 print("WARNING: 'id' field still present in model!")
             else:
                 print("SUCCESS: 'id' field ignored/absent in model.")
                 
        except Exception as e:
            print(f"Validation raised error (Expected if strict): {e}")

    except ImportError:
        print("Could not import app modules. Are we in the root dir?")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_visita()
