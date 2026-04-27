from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def test_create_pedreiro():
    # 1. Login
    login_data = {
        "username": settings.ADMIN_USERNAME,
        "password": settings.ADMIN_PASSWORD
    }
    response = client.post("/api/login", data=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Pedreiro
    pedreiro_data = {
        "nome_completo": "João da Silva",
        "cpf": "123.456.789-00",
        "telefone": "11999999999",
        "endereco": "Rua Teste, 123",
        "status": "Ativo"
    }
    
    print("Sending POST /api/pedreiros...")
    response = client.post("/api/pedreiros", json=pedreiro_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 201:
        print("Pedreiro created successfully.")
    elif response.status_code == 400 and "CPF já cadastrado" in response.text:
        print("Pedreiro already exists (CPF duplicate).")
    else:
        print("Failed to create pedreiro.")

    # 3. List Pedreiros
    print("\nListing Pedreiros...")
    response = client.get("/api/pedreiros", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

if __name__ == "__main__":
    test_create_pedreiro()
