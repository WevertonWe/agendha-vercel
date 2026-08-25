import requests
import json

def explorar_token_coletum(token: str):
    print(f"Investigando token no Coletum API...")
    
    headers = {
        "token": token,
        "Accept": "application/json"
    }
    
    # Endpoint para listar os formulários disponíveis para este token
    url_forms = "https://coletum.com/api/forms"
    
    try:
        response = requests.get(url_forms, headers=headers, timeout=15)
        
        print(f"\nStatus Code (Formulários): {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            forms = data if isinstance(data, list) else data.get("forms", [])
            print(f"✅ SUCESSO! O token conseguiu acessar o Coletum.")
            print(f"Total de Formulários vinculados a esse token: {len(forms)}")
            
            for f in forms[:5]: # Mostrar só os 5 primeiros
                f_id = f.get('id', 'N/A')
                f_name = f.get('name', 'N/A')
                print(f" - ID: {f_id} | Nome: {f_name}")
                
            if forms:
                print("\n---------------------------------------------------------")
                print("Deseja ver os preenchimentos (respostas) do primeiro formulário acima?")
                print(f"Endpoint que usaríamos: https://coletum.com/api/answers/{forms[0].get('id')}")
        else:
            print("❌ Falha ao acessar. Verifique se o token está correto.")
            print("Resposta da API:", response.text)
            
    except Exception as e:
        print(f"Erro ao tentar conectar na API do Coletum: {e}")

if __name__ == "__main__":
    print("=== TESTE DE TOKEN DO COLETUM ===")
    meu_token = input("Cole o seu token do Coletum aqui e aperte ENTER: ").strip()
    
    if meu_token:
        explorar_token_coletum(meu_token)
    else:
        print("Token não fornecido.")
