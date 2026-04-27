
import requests

BASE_URL = "http://localhost:8000"

def test_routes():
    # Caminhos esperados
    meta_url = f"{BASE_URL}/api/projetos/ater-bahia-sem-fome/metas/999999"
    visita_url = f"{BASE_URL}/api/projetos/ater-bahia-sem-fome/visitas/999999"

    print(f"Testando DELETE Meta: {meta_url}")  # nosec
    try:
        r = requests.delete(meta_url)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 404:
             print("Resultado esperado (404 Not Found - registro não existe, mas rota existe?)")
             # Se a rota não existisse, seria 404 também, mas o detail seria diferente ou methods not allowed
             print(f"Response: {r.text}")
        elif r.status_code == 405:
            print("ERRO: Método não permitido (405). A rota existe mas não aceita DELETE?")
        else:
            print(f"Outro status: {r.status_code}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")

    print("-" * 30)

    print(f"Testando DELETE Visita: {visita_url}")  # nosec
    try:
        r = requests.delete(visita_url)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_routes()
