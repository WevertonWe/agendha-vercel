
import requests
import json  # noqa: F401
from datetime import date

# Config
BASE_URL = "http://localhost:8000" # Ajuste se porta for diferente
API_URL = f"{BASE_URL}/api/bsf/visitas"

def test_create_visita():
    print(f"Testando POST em: {API_URL}")
    
    payload = {
        "tecnico_id": "TEST_BOT",
        "beneficiario_id": "TEST_USER",
        "municipio": "Glória", # Deve existir como meta
        "comunidade": "Teste Auto",
        "data_visita": str(date.today()),
        "status": "Realizada"
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ SUCESSO! Visita criada.")
            # Cleanup - Delete the test visit
            data = response.json()
            new_id = data.get('id')
            if new_id:
                print(f"Limpando visita de teste ID {new_id}...")
                # Assuming delete route is fixed too
                del_resp = requests.delete(f"{API_URL}/{new_id}")
                if del_resp.status_code == 200:
                    print("✅ Limpeza concluída.")
                else:
                    print(f"⚠️ Falha ao limpar: {del_resp.status_code}")
        else:
            print("❌ FALHA NA CRIAÇÃO.")
            
    except Exception as e:
        print(f"ERRO DE CONEXÃO: {e}")
        print("Certifique-se que o servidor está rodando.")

if __name__ == "__main__":
    test_create_visita()
